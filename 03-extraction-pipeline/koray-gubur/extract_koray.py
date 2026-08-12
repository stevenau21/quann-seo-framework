#!/usr/bin/env python3
"""
Koray Gubur Framework Extraction — Direct LightRAG Query Approach
=================================================================
Queries the LightRAG knowledge graph with targeted extraction prompts,
aggregates results into structured frameworks.json.

Avoids fragile .format() escaping by using simple string replacement.
"""

import json
import os
import sys
import time
import re
import httpx
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────

LIGHTRAG_URL = "http://localhost:8012"
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"
WORKSPACE = "/home/steve/lightrag-apps/koray-gubur/workspace"

os.makedirs(OUTDIR, exist_ok=True)


def query_lightrag(query: str, mode: str = "hybrid") -> str:
    """Query LightRAG and return response text."""
    try:
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(
                f"{LIGHTRAG_URL}/query",
                json={"query": query, "mode": mode},
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
    except Exception as e:
        print(f"  ⚠ LightRAG error: {e}")
        return ""


def call_ollama(system: str, user: str, max_tokens: int = 3000) -> str:
    """Call local Ollama and return raw response text."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    
    for attempt in range(3):
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "temperature": 0.3,
                        "max_tokens": max_tokens,
                        "messages": messages,
                    },
                )
                resp.raise_for_status()
                content = (
                    resp.json()
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                if content:
                    return content
        except Exception as e:
            print(f"  Ollama attempt {attempt+1}: {e}")
            time.sleep(2 * (attempt + 1))
    return ""


def try_parse_json(text: str):
    """Try to extract JSON from LLM response."""
    # Direct parse
    try:
        return json.loads(text)
    except:
        pass
    # Code fence
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    # Find JSON object or array
    for pattern in [r'\[[\s\S]*\]', r'\{[\s\S]*\}']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None


# ── Step 1: Extract Frameworks ───────────────────────────────────

def extract_frameworks():
    """Query LightRAG for Koray's frameworks, then structure with Ollama."""
    print("\n═══ STEP 1: Framework Extraction ═══")
    
    # Query 1: Get all frameworks
    rag_context = query_lightrag(
        "What are all the SEO frameworks, methodologies, and systems that Koray Gubur has developed or teaches? "
        "List every named framework like Topical Authority, Semantic SEO, Holistic SEO, Query-Entity Mapping, etc."
    )
    
    print(f"  LightRAG response: {len(rag_context)} chars")
    
    # Structure with Ollama
    prompt = """You are extracting Koray Gubur's SEO frameworks from his writing.

Read the LightRAG context below and extract EVERY named framework, methodology, or system. For each one, provide:

- name: exact name of the framework
- definition: 2-3 sentence summary in Koray's own framing
- problem_solved: what was broken that this fixes
- evolution: how it changed over time (v1, v2, etc if mentioned)
- depends_on: other concepts it requires
- contradicts: conventional wisdom it challenges
- unique_position: what makes Koray's version different
- confidence: "core" (central to his work), "secondary", or "emerging"

Return ONLY a JSON array of framework objects. No markdown, no extra text.

LIGHTRAG CONTEXT:
"""
    prompt += rag_context[:8000]  # Truncate to avoid token overflow
    
    result = call_ollama(
        "You extract structured SEO framework data. Return ONLY valid JSON array.",
        prompt,
        max_tokens=4000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, list):
        print(f"  ✓ Extracted {len(parsed)} frameworks")
        return parsed
    else:
        print(f"  ✗ Parse failed. Saving raw output.")
        with open(f"{OUTDIR}/frameworks_raw.txt", "w") as f:
            f.write(result)
        return []


# ── Step 2: Extract Mental Models ────────────────────────────────

def extract_mental_models():
    """Extract how Koray THINKS about search."""
    print("\n═══ STEP 2: Mental Model Extraction ═══")
    
    rag_context = query_lightrag(
        "What mental models, conceptual frameworks, and ways of thinking does Koray Gubur use to understand search engines? "
        "How does he think about information retrieval, entity relationships, semantic understanding, and ranking? "
        "What are his core beliefs about how search works?"
    )
    
    print(f"  LightRAG response: {len(rag_context)} chars")
    
    prompt = """Extract Koray Gubur's MENTAL MODELS from this context.

A mental model is a conceptual lens — HOW he thinks about search, not what he does.

For each mental model, provide:
- name: short label
- description: how Koray frames this way of thinking
- origin: where it comes from (patent, IR theory, linguistics, etc)
- implications: what this mental model leads him to do differently

Return ONLY a JSON array. No markdown.

CONTEXT:
"""
    prompt += rag_context[:8000]
    
    result = call_ollama(
        "Extract mental models. Return ONLY valid JSON array.",
        prompt,
        max_tokens=3000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, list):
        print(f"  ✓ Extracted {len(parsed)} mental models")
        return parsed
    else:
        print("  ✗ Parse failed, saving raw.")
        with open(f"{OUTDIR}/mental_models_raw.txt", "w") as f:
            f.write(result)
        return []


# ── Step 3: Extract Signal Hierarchy ─────────────────────────────

def extract_signal_hierarchy():
    """Extract ranked ranking signals."""
    print("\n═══ STEP 3: Signal Hierarchy ═══")
    
    rag_context = query_lightrag(
        "What ranking signals and factors does Koray Gubur consider most important for SEO? "
        "Rank them from most important to least important. What does he say about backlinks, content quality, "
        "entity coverage, topical depth, user signals, technical factors, semantic structure?"
    )
    
    print(f"  LightRAG response: {len(rag_context)} chars")
    
    prompt = """Extract Koray Gubur's RANKING SIGNAL HIERARCHY.

Rank the signals from MOST important (1) to LEAST important. For each:
- rank: number
- name: signal name
- description: how Koray describes its importance
- source: evidence he cites
- confidence: high/medium/speculative (how certain Koray seems)

Return ONLY: {"signal_hierarchy": [{"rank": 1, "name": "...", ...}]}

CONTEXT:
"""
    prompt += rag_context[:8000]
    
    result = call_ollama(
        "Extract ranking signal hierarchy. Return ONLY valid JSON object with 'signal_hierarchy' key.",
        prompt,
        max_tokens=3000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        signals = parsed.get("signal_hierarchy", [])
        print(f"  ✓ Extracted {len(signals)} signals")
        return parsed
    else:
        print("  ✗ Parse failed, saving raw.")
        with open(f"{OUTDIR}/signals_raw.txt", "w") as f:
            f.write(result)
        return {}


# ── Step 4: Negative Space ───────────────────────────────────────

def extract_negative_space():
    """Find what Koray doesn't address."""
    print("\n═══ STEP 4: Negative Space ═══")
    
    rag_context = query_lightrag(
        "What topics, questions, or areas does Koray Gubur NOT cover in his SEO methodology? "
        "Does he address AI Overviews, ChatGPT, Perplexity, generative search? "
        "Does he cover local SEO, ecommerce SEO, enterprise SEO, international SEO?"
    )
    
    print(f"  LightRAG response: {len(rag_context)} chars")
    
    prompt = """Analyze what's MISSING from Koray Gubur's work. Identify:

- topics_avoided: significant SEO topics he notably does NOT discuss (with why it's notable)
- questions_unanswered: questions he raises but never resolves
- contradictions: where does he say things that conflict?
- blind_spots: approaches or paradigms he dismisses or overlooks
- aeo_geo_coverage: "extensive", "partial", "minimal", or "none" — with one sentence assessment

Return ONLY a JSON object. No markdown.

CONTEXT:
"""
    prompt += rag_context[:8000]
    
    result = call_ollama(
        "Analyze gaps and blind spots. Return ONLY valid JSON object.",
        prompt,
        max_tokens=3000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        print(f"  ✓ Negative space analyzed")
        return parsed
    else:
        print("  ✗ Parse failed, saving raw.")
        with open(f"{OUTDIR}/negative_space_raw.txt", "w") as f:
            f.write(result)
        return {}


# ── Step 5: Breadcrumbs ──────────────────────────────────────────

def extract_breadcrumbs():
    """Trace intellectual influences."""
    print("\n═══ STEP 5: Breadcrumb Tracing ═══")
    
    rag_context = query_lightrag(
        "What patents, research papers, Google documentation, academic sources, books, "
        "and other practitioners does Koray Gubur cite or reference in his writing? "
        "List specific patent numbers, paper titles, authors, and document names."
    )
    
    print(f"  LightRAG response: {len(rag_context)} chars")
    
    prompt = """Trace Koray Gubur's intellectual influences. Extract every citation:

- patents: [{"id": "USPTO number", "title": "...", "why_cited": "..."}]
- papers: [{"title": "...", "authors": "...", "venue": "...", "why_cited": "..."}]
- official_docs: [{"name": "...", "why_cited": "..."}]
- api_docs: [{"name": "...", "why_cited": "..."}]
- books: [{"title": "...", "author": "...", "why_cited": "..."}]
- practitioners: [{"name": "...", "context": "..."}]

Return ONLY a JSON object. No markdown.

CONTEXT:
"""
    prompt += rag_context[:8000]
    
    result = call_ollama(
        "Trace citations and influences. Return ONLY valid JSON object.",
        prompt,
        max_tokens=3000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        total = sum(len(v) for v in parsed.values() if isinstance(v, list))
        print(f"  ✓ Traced {total} breadcrumbs")
        return parsed
    else:
        print("  ✗ Parse failed, saving raw.")
        with open(f"{OUTDIR}/breadcrumbs_raw.txt", "w") as f:
            f.write(result)
        return {}


# ── Step 6: Assemble ─────────────────────────────────────────────

def assemble(frameworks, mental_models, signal_hierarchy, negative_space, breadcrumbs):
    """Merge all extractions into final frameworks.json."""
    print("\n═══ STEP 6: Final Assembly ═══")
    
    final = {
        "architect": {
            "name": "Koray Tugberk GUBUR",
            "paradigm": "seo",
            "domains": ["holisticseo.digital", "koraygubur.com"],
            "extraction_date": time.strftime("%Y-%m-%d"),
            "total_docs_analyzed": 394,
        },
        "frameworks": frameworks,
        "mental_models": mental_models,
        "signal_hierarchy": signal_hierarchy,
        "negative_space": negative_space,
        "breadcrumbs": breadcrumbs,
    }
    
    outpath = f"{OUTDIR}/frameworks.json"
    with open(outpath, "w") as f:
        json.dump(final, f, indent=2)
    
    size_kb = os.path.getsize(outpath) / 1024
    print(f"  ✓ frameworks.json — {size_kb:.1f}KB")
    print(f"    Frameworks: {len(frameworks)}")
    print(f"    Mental models: {len(mental_models)}")
    
    return final


# ── Main ─────────────────────────────────────────────────────────

def main():
    start = time.time()
    
    frameworks = extract_frameworks()
    mental_models = extract_mental_models()
    signal_hierarchy = extract_signal_hierarchy()
    negative_space = extract_negative_space()
    breadcrumbs = extract_breadcrumbs()
    
    final = assemble(frameworks, mental_models, signal_hierarchy, negative_space, breadcrumbs)
    
    elapsed = time.time() - start
    print(f"\n✅ Extraction complete in {elapsed:.0f}s")
    print(f"Output: {OUTDIR}/frameworks.json")


if __name__ == "__main__":
    main()
