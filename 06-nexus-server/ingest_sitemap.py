#!/usr/bin/env python3
"""
Shared incremental sitemap ingestion for all LightRAG notebooks.

ONE script. Each notebook drops a config.json in its directory.
This script reads that config, diffs the sitemap, scrapes only
new/changed URLs via Docling, and POSTs chunks to the running
LightRAG service (which owns the embedding model — can never mismatch).

Usage:
    python3 ingest_sitemap.py [--notebook DIR] [--force]

Config format (config.json in notebook dir):
    {
        "sitemap_url": "https://example.com/sitemap.xml",
        "sitemap_index": false,
        "backend_port": 8011,
        "notebook_dir": "/path/to/notebook",
        "chunk_size": 800
    }

State is stored alongside config as ingest_state.json.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
import requests

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_markdown(text: str, source_url: str, max_chars: int = 800) -> list[dict]:
    """Sentence-aware chunking. One chunk = {text, source, id}."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for s in sentences:
        if (len(current) + 1 + len(s)) > max_chars and len(current) > 100:
            chunks.append({"text": current.strip(), "source": source_url})
            current = s
        else:
            current = (current + " " + s) if current else s
    if len(current.strip()) > 50:
        chunks.append({"text": current.strip(), "source": source_url})
    return chunks


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------

_UA = "Mozilla/5.0 (compatible; HermesAgent/1.0; +https://quann.homes)"

def fetch_sitemap_urls(sitemap_url: str) -> dict[str, str]:
    """Return {url: lastmod} from a single sitemap XML."""
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    resp = requests.get(sitemap_url, headers={"User-Agent": _UA}, timeout=30)
    resp.raise_for_status()
    tree = ET.fromstring(resp.content)
    urls = {}
    for el in tree.findall(".//s:url", ns):
        loc = el.find("s:loc", ns)
        lastmod = el.find("s:lastmod", ns) if "lastmod" not in str(el.tag) else el.find("s:lastmod", ns)
        # Actually just find lastmod properly
        lm_el = None
        for child in el:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "loc" and child.text:
                loc_url = child.text.strip()
            elif tag == "lastmod" and child.text:
                lm_el = child.text.strip()
        # Simpler approach:
        loc_el = el.find("s:loc", ns)
        lm_el = el.find("s:lastmod", ns)
        if loc_el is not None and loc_el.text:
            urls[loc_el.text.strip()] = lm_el.text.strip() if lm_el is not None and lm_el.text else ""
    return urls


def fetch_sitemap_index_urls(index_url: str) -> dict[str, str]:
    """For sitemap_index.xml — fetch all sub-sitemaps and return combined {url: lastmod}."""
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    resp = requests.get(index_url, headers={"User-Agent": _UA}, timeout=30)
    resp.raise_for_status()
    tree = ET.fromstring(resp.content)

    sub_sitemaps = []
    for el in tree.findall(".//s:sitemap", ns):
        loc = el.find("s:loc", ns)
        if loc is not None and loc.text:
            sub_sitemaps.append(loc.text.strip())

    all_urls = {}
    for sm_url in sub_sitemaps:
        try:
            urls = fetch_sitemap_urls(sm_url)
            all_urls.update(urls)
        except Exception as e:
            print(f"  ⚠ Failed to fetch sub-sitemap {sm_url}: {e}")

    return all_urls


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state(state_file: Path) -> dict:
    if state_file.exists():
        with open(state_file) as f:
            data = json.load(f)
            if "urls" not in data:
                data = {"urls": data}
            return data
    return {"urls": {}}


def save_state(state_file: Path, state: dict) -> None:
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, default=str)


def diff_sitemap(current: dict[str, str], state: dict) -> tuple[list[str], list[str]]:
    """Return (new_urls, changed_urls)."""
    stored = state.get("urls", {})
    new_urls = []
    changed_urls = []
    for url, lastmod in current.items():
        stored_entry = stored.get(url)
        if stored_entry is None:
            new_urls.append(url)
        elif isinstance(stored_entry, dict) and stored_entry.get("lastmod") != lastmod:
            changed_urls.append(url)
        elif isinstance(stored_entry, str) and stored_entry != lastmod:
            changed_urls.append(url)
    deleted = [u for u in stored if u not in current]
    if deleted:
        print(f"  {len(deleted)} URLs removed from sitemap")
    return new_urls, changed_urls


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

def scrape_urls(urls: list[str]) -> list[dict]:
    """Extract content from URLs using Docling. Returns [{text, source}, ...]."""
    if not urls:
        return []

    print(f"📄 Extracting {len(urls)} pages with Docling...")
    all_chunks = []

    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
    except ImportError:
        print("⚠ Docling not installed — falling back to requests + basic HTML strip")
        for url in urls:
            try:
                resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                text = re.sub(r"<script[\s\S]*?</script>", "", resp.text)
                text = re.sub(r"<style[\s\S]*?</style>", "", text)
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                if len(text) > 100:
                    chunks = chunk_markdown(text, url)
                    all_chunks.extend(chunks)
                    print(f"  {url}: {len(chunks)} chunks ({len(text)} chars)")
            except Exception as e:
                print(f"  ⚠ {url}: {e}")
        return all_chunks

    for i, url in enumerate(urls, 1):
        try:
            print(f"  [{i}/{len(urls)}] {url}")
            result = converter.convert(url)
            markdown = result.document.export_to_markdown()
            if not markdown or len(markdown.strip()) < 100:
                print(f"    ⚠ Extracted too little ({len(markdown.strip()) if markdown else 0} chars)")
                continue
            chunks = chunk_markdown(markdown.strip(), url)
            all_chunks.extend(chunks)
            print(f"    → {len(chunks)} chunks ({len(markdown.strip())} chars)")
        except Exception as e:
            print(f"  ⚠ {url}: {e}")

    print(f"\n  Total: {len(all_chunks)} chunks from {len(urls)} URLs")
    return all_chunks


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def ingest_chunks(backend_url: str, chunks: list[dict]) -> int:
    """POST chunks to LightRAG service. Returns number accepted."""
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    file_paths = [c["source"] for c in chunks]
    # Stable IDs: hash of URL + chunk index
    ids = [
        hashlib.md5(f"{fp}|{i}".encode()).hexdigest()[:16]
        for i, fp in enumerate(file_paths)
    ]

    resp = requests.post(
        f"{backend_url}/documents/texts",
        json={"texts": texts, "ids": ids, "file_paths": file_paths},
        timeout=120,
    )

    if resp.status_code == 200:
        data = resp.json()
        status = data.get("status", "")
        track_id = data.get("track_id", "")
        if status == "success":
            print(f"  ✅ Accepted {len(texts)} chunks (track: {track_id})")
            return len(texts)
        else:
            print(f"  ⚠ Unexpected response: {data}")
            return 0
    else:
        print(f"  ❌ POST failed ({resp.status_code}): {resp.text[:300]}")
        return 0


def poll_until_ready(backend_url: str, timeout: int = 600) -> bool:
    """Wait for LightRAG pipeline to finish processing."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{backend_url}/documents/pipeline_status", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                busy = data.get("busy", data.get("is_processing", False))
                if not busy:
                    return True
        except Exception:
            pass
        time.sleep(15)
    return False


def wait_for_incremental_cooldown(backend_url: str, chunks_count: int, timeout: int = 600) -> bool:
    """
    After posting chunks, wait for the service to finish extracting entities.
    Checks doc_status counts to verify extraction caught up.
    """
    if chunks_count == 0:
        return True

    print("  ⏳ Waiting for extraction to complete...")
    time.sleep(30)  # initial buffer

    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{backend_url}/documents/status_counts", timeout=10)
            if resp.status_code == 200:
                counts = resp.json()
                pending = counts.get("pending", 0) + counts.get("processing", 0)
                if pending == 0:
                    print(f"  ✅ Extraction complete: {counts}")
                    return True
                print(f"    pending={pending}, status={counts}")
        except Exception as e:
            print(f"    ⚠ status check: {e}")
        time.sleep(30)

    print("  ⚠ Timeout waiting for extraction")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Shared incremental sitemap ingestion")
    parser.add_argument("--notebook", required=True, help="Path to notebook directory")
    parser.add_argument("--force", action="store_true", help="Reingest all URLs (ignore diff)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, don't ingest")
    args = parser.parse_args()

    notebook_dir = Path(args.notebook).resolve()
    if not notebook_dir.is_dir():
        print(f"❌ Not a directory: {notebook_dir}")
        sys.exit(1)

    config_file = notebook_dir / "config.json"
    if not config_file.exists():
        print(f"❌ No config.json in {notebook_dir}")
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)

    sitemap_url = config["sitemap_url"]
    sitemap_index = config.get("sitemap_index", False)
    backend_port = config["backend_port"]
    chunk_size = config.get("chunk_size", 800)
    exclude_patterns = config.get("exclude_patterns", [])

    backend_url = f"http://127.0.0.1:{backend_port}"
    state_file = notebook_dir / "ingest_state.json"

    print(f"\n{'='*60}")
    print(f"[{datetime.now(timezone.utc).isoformat()}] {notebook_dir.name}")
    print(f"  Sitemap: {sitemap_url}")
    print(f"  Backend: {backend_url}")
    print(f"  Force:   {args.force}")
    if exclude_patterns:
        print(f"  Exclude patterns: {len(exclude_patterns)}")
        for p in exclude_patterns:
            print(f"    • {p}")
    print(f"{'='*60}\n")

    # 1. Fetch sitemap
    print("📡 Fetching sitemap...")
    try:
        if sitemap_index:
            current = fetch_sitemap_index_urls(sitemap_url)
        else:
            current = fetch_sitemap_urls(sitemap_url)
    except Exception as e:
        print(f"❌ Failed to fetch sitemap: {e}")
        sys.exit(1)
    print(f"  {len(current)} URLs in sitemap")

    # 1b. Apply exclude patterns
    if exclude_patterns:
        filtered = {}
        excluded_count = 0
        for url in current:
            if any(re.search(pat, url) for pat in exclude_patterns):
                excluded_count += 1
            else:
                filtered[url] = current[url]
        print(f"  🗑 {excluded_count} URLs excluded by {len(exclude_patterns)} patterns")
        current = filtered

    # 2. Diff against state
    state = load_state(state_file)
    if args.force:
        all_to_process = list(current.keys())
        print(f"  🔄 Force mode: all {len(all_to_process)} URLs")
    else:
        new_urls, changed_urls = diff_sitemap(current, state)
        all_to_process = new_urls + changed_urls
        print(f"  {len(new_urls)} new, {len(changed_urls)} changed")

    if not all_to_process:
        print("✅ No changes — nothing to ingest")
        return 0

    # 3. Dry run
    if args.dry_run:
        print(f"\n🔍 DRY RUN — would process:")
        for u in all_to_process[:10]:
            print(f"  {u}")
        if len(all_to_process) > 10:
            print(f"  ... and {len(all_to_process) - 10} more")
        return 0

    # 4. Scrape
    chunks = scrape_urls(all_to_process)
    if not chunks:
        print("⚠ No chunks produced")
        return 0

    # 5. Ingest
    print(f"\n⚙️  Inserting {len(chunks)} chunks...")
    inserted = ingest_chunks(backend_url, chunks)

    # 6. Wait for extraction to catch up (important for immediate query quality)
    wait_for_incremental_cooldown(backend_url, inserted)

    # 7. Update state
    for url in all_to_process:
        state["urls"][url] = {
            "lastmod": current.get(url, ""),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
    save_state(state_file, state)
    print(f"✅ State saved ({len(state['urls'])} URLs tracked)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
