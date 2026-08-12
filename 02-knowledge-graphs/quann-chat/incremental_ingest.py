#!/usr/bin/env python3
"""Ingest quann.homes sitemap into LightRAG with full entity extraction (gleaning=2).

Strategy:
  - Scrape every page with requests (Docling for clean markdown)
  - Insert via LightRAG.ainsert() directly — bypasses the /documents/text API
    so we can control gleaning and entity_types from the constructor
  - Uses the same workspace the lightrag-server serves from
  - Dedup via MD5 — re-runs are safe (LightRAG skips existing content)
"""

import json
import time
import re
import sys
import tempfile
import os
import warnings

import requests
from docling.document_converter import DocumentConverter
from lightrag import LightRAG
from lightrag.llm.ollama import ollama_model_complete

warnings.filterwarnings("ignore")

# ── Config ──────────────────────────────────────────────────────────
WORKSPACE = "/home/steve/lightrag-apps/quann-chat/workspace"
SITEMAP_URL = "https://quann.homes/sitemap.xml"
STATE_FILE = "/home/steve/lightrag-apps/quann-chat/ingest_state.json"
LLM_MODEL = "deepseek-v4-pro:cloud"  # deep model for quality extraction
EMBED_MODEL = "nomic-embed-text-v2-moe"
OLLAMA_BASE = "http://192.168.4.148:11434"  # IP-based (host.docker.internal in WSL2 context)
BATCH_SIZE = 5

# ── Docling ──────────────────────────────────────────────────────────
_converter = None

def get_converter():
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter

def extract_content(html: str) -> str | None:
    """Extract clean markdown from HTML via Docling."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            temp_path = f.name
        result = get_converter().convert(temp_path)
        os.unlink(temp_path)
        return result.document.export_to_markdown().strip()
    except Exception as e:
        print(f"  ⚠ Docling failed: {e}")
        return None

# ── LightRAG init ────────────────────────────────────────────────────
async def get_rag():
    """Create LightRAG instance pointing at existing workspace."""
    from functools import partial
    from lightrag.utils import EmbeddingFunc
    from lightrag.llm.ollama import ollama_embed

    # CRITICAL: Use .func to avoid double-wrapping (ollama_embed already decorated)
    embed_fn = partial(
        ollama_embed.func,
        embed_model=EMBED_MODEL,
        host=OLLAMA_BASE,
        port=11434,
    )

    embedding_func = EmbeddingFunc(
        embedding_dim=768,
        max_token_size=512,
        func=embed_fn,
    )

    rag = LightRAG(
        working_dir=WORKSPACE,
        llm_model_func=lambda prompt, system_prompt=None, history_messages=None, **kwargs:
            ollama_model_complete(
                prompt, system_prompt=system_prompt,
                history_messages=history_messages,
                host=OLLAMA_BASE, port=11434,
                model=LLM_MODEL, **kwargs,
            ),
        embedding_func=embedding_func,
        chunk_token_size=256,
        addon_params={
            "example_number": 1,
            "language": "English",
            "entity_types": ["organization", "person", "geo", "event", "category"],
            "entity_extract_max_gleaning": 2,
        },
        kv_storage="JsonKVStorage",
        doc_status_storage="JsonDocStatusStorage",
        graph_storage="NetworkXStorage",
        vector_storage="NanoVectorDBStorage",
        enable_llm_cache_for_entity_extract=True,
        max_parallel_insert=2,
    )
    return rag

# ── Sitemap ──────────────────────────────────────────────────────────
def parse_sitemap() -> list[dict]:
    """Fetch sitemap, return [{url, lastmod}]."""
    resp = requests.get(SITEMAP_URL, headers={"User-Agent": "Mozilla/5.0 (compatible; quann-ingest)"})
    resp.raise_for_status()
    urls = []
    for match in re.finditer(r'<url>.*?<loc>(.*?)</loc>.*?(?:<lastmod>(.*?)</lastmod>)?.*?</url>', resp.text, re.DOTALL):
        urls.append({"url": match.group(1), "lastmod": match.group(2) or ""})
    return urls

# ── Main ─────────────────────────────────────────────────────────────
async def main():
    # Load or init state
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {"urls": {}}

    urls = parse_sitemap()
    print(f"📋 Sitemap: {len(urls)} URLs")

    # Determine which URLs need ingestion
    to_ingest = []
    for item in urls:
        url = item["url"]
        prev = state["urls"].get(url, {})
        if not prev or prev.get("lastmod") != item["lastmod"]:
            to_ingest.append(item)

    if not to_ingest:
        print("✅ All URLs up to date. Nothing to ingest.")
        return

    print(f"🔄 {len(to_ingest)} URLs changed/new. Starting ingestion...")

    # Filter: only real quann.homes pages (no PDFs, images, external urls)
    content_urls = [
        item for item in to_ingest
        if item["url"].startswith("https://quann.homes/")
        and not item["url"].endswith((".pdf", ".png", ".jpg", ".jpeg", ".gif", ".mp3", ".mp4", ".zip"))
    ]
    print(f"📄 {len(content_urls)} content pages (filtered from {len(to_ingest)})")

    rag = await get_rag()
    await rag.initialize_storages()  # Required before ainsert()
    print("✅ LightRAG initialized")

    for batch_start in range(0, len(content_urls), BATCH_SIZE):
        batch = content_urls[batch_start:batch_start + BATCH_SIZE]
        print(f"\n📦 Batch {batch_start//BATCH_SIZE + 1}/{(len(content_urls) + BATCH_SIZE - 1)//BATCH_SIZE}: {len(batch)} pages")

        documents = []
        for item in batch:
            url = item["url"]
            print(f"  📡 {url} ... ", end="", flush=True)
            try:
                resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; quann-ingest)"}, timeout=20)
                resp.raise_for_status()
                content = extract_content(resp.text)
                if content and len(content.strip()) > 50:
                    documents.append(content)
                    state["urls"][url] = {"lastmod": item["lastmod"], "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
                    print(f"OK ({len(content)} chars)")
                else:
                    print(f"SKIP (empty/short content: {len(content) if content else 0} chars)")
            except Exception as e:
                print(f"ERR: {e}")
                continue
            time.sleep(0.5)

        if documents:
            print(f"  ⏳ Inserting {len(documents)} docs into LightRAG...", flush=True)
            await rag.ainsert(documents)
            print(f"  ✅ Batch complete.", flush=True)

        # Save state after each batch
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

        time.sleep(2)

    print(f"\n✅ Ingestion complete. {len(content_urls)} pages processed.")
    print(f"State saved to {STATE_FILE}")
    print(f"Workspace: {WORKSPACE}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
