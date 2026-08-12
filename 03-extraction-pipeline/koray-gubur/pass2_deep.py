#!/usr/bin/env python3
"""
Pass 2: Deep-dive per framework + orthogonal angle queries
==========================================================
Takes Pass 1's 8 frameworks and queries each one specifically.
Also queries from different angles to catch missed frameworks.
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
os.makedirs(OUTDIR, exist_ok=True)


def query_lightrag(query: str, mode: str = "hybrid") -> str:
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
    try:
        return json.loads(text)
    except:
        pass
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    for pattern in [r'\[[\s\S]*\]', r'\{[\s\S]*\}']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return None


# ── Pass 1 frameworks as seeds ────────────────────────────────────
SEED_FRAMEWORKS = [
    "Holistic SEO",
    "Topical Authority",
    "Semantic SEO",
    "Entity-based Search Engine Optimization Projects",
    "Topical Maps",
    "SaaS SEO",
    "Theoretical SEO",
    "Flywheel Model",
]

# Orthogonal query angles to catch missed frameworks
ANGLE_QUERIES = [
    # Technical angle
    (
        "technical_depth",
        "What technical SEO frameworks, methods, or systems does Koray Gubur describe? "
        "Focus on crawl budget, indexing strategies, server-side rendering, JavaScript SEO, "
        "structured data strategies, log file analysis, page speed optimization, "
        "HSTS and security, rendering strategies, pagination handling, canonicalization approaches."
    ),
    # Linguistic / NLP angle
    (
        "linguistic_nlp",
        "What linguistic, NLP, or semantic frameworks does Koray Gubur describe? "
        "Focus on word embeddings, vector space models, lemmatization, stemming, "
        "collocation analysis, TF-IDF, BM25, N-grams, word sense disambiguation, "
        "named entity recognition, text classification, topic modeling, sentiment analysis."
    ),
    # Information Retrieval angle
    (
        "information_retrieval",
        "What information retrieval frameworks, models, or systems does Koray Gubur describe? "
        "Focus on retrieval models, ranking algorithms, relevance scoring, query understanding, "
        "intent classification, click models, ranking factors, information needs, "
        "document representation, indexing theory."
    ),
    # Content strategy angle
    (
        "content_strategy",
        "What content strategy frameworks, methodologies, or systems does Koray Gubur describe? "
        "Focus on content briefs, editorial planning, content hierarchies, content updating, "
        "content pruning, content freshness, content quality metrics, readability, "
        "E-A-T, author expertise, fact-checking, source attribution."
    ),
    # Entity / Knowledge Graph angle
    (
        "entity_knowledge",
        "What entity-based, knowledge graph, or structured data frameworks does Koray Gubur describe? "
        "Focus on Knowledge Graph optimization, Knowledge Panel management, entity disambiguation, "
        "entity salience, attribute extraction, Schema.org types, Google's Knowledge Vault, "
        "entity-oriented search, machine IDs, related entities."
    ),
    # AI / ML angle
    (
        "ai_ml_search",
        "What AI, machine learning, or algorithmic frameworks does Koray Gubur describe? "
        "Focus on RankBrain, neural matching, BERT, MUM, deep learning for search, "
        "learning to rank, relevance feedback, query embeddings, document embeddings, "
        "transformer models, language models for SEO."
    ),
    # Business / Strategy angle
    (
        "business_strategy",
        "What business strategy, growth, or marketing frameworks does Koray Gubur describe? "
        "Focus on SEO ROI, marketing funnels, growth loops, flywheel models, "
        "client acquisition, pricing models, agency operations, market positioning, "
        "competitive analysis, market share strategies."
    ),
    # Data Science / Analytics angle
    (
        "data_science",
        "What data science, analytics, or measurement frameworks does Koray Gubur describe? "
        "Focus on Python for SEO, data pipelines, statistical analysis, A/B testing, "
        "log analysis, click curves, click-through rate models, SERP analysis, "
        "ranking distribution analysis, traffic forecasting, cohort analysis."
    ),
    # International / Multilingual angle
    (
        "international",
        "What international SEO, multilingual, or localization frameworks does Koray Gubur describe? "
        "Focus on hreflang implementation, country targeting, language targeting, "
        "international content strategy, multilingual entity alignment, "
        "regional search behavior differences."
    ),
    # Link building / Authority angle
    (
        "authority_links",
        "What link building, authority, or trust frameworks does Koray Gubur describe? "
        "Focus on TrustRank, PageRank, link quality assessment, link graphs, "
        "authority signals, brand signals, citation analysis, co-citation, "
        "bibliographic coupling, link velocity, link reclamation."
    ),
]


# ── Pass 2a: Deep-dive per seed framework ────────────────────────
def deep_dive_framework(fw_name: str) -> dict:
    print(f"\n  🔍 Deep-diving: {fw_name}")

    rag = query_lightrag(
        f"Everything about {fw_name} framework or methodology as described by Koray Gubur. "
        f"How does it work? What are its components? How has it evolved? "
        f"What are specific techniques, steps, or implementations? "
        f"What examples does he give?"
    )

    prompt = f"""Deep-dive extraction on Koray Gubur's "{fw_name}" framework.

From the context below, extract:
- name: "{fw_name}"
- components: specific sub-components, techniques, or steps
- methods: concrete how-to instructions (numbered steps if available)
- evolution: versions, iterations, or changes over time
- metrics: anything he measures or tracks
- tools: specific tools, libraries, or software mentioned
- nuances: subtle details that distinguish this from similar frameworks
- related_frameworks: other frameworks this connects to or depends on

Return ONLY a JSON object. No markdown, no extra text.

CONTEXT:
"""
    prompt += rag[:6000]

    result = call_ollama(
        f"Deep-dive extract on '{fw_name}'. Return ONLY valid JSON object.",
        prompt,
        max_tokens=4000,
    )
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        print(f"    ✓ {len(parsed.get('components', []))} components, "
              f"{len(parsed.get('methods', []))} methods")
        return parsed
    else:
        print(f"    ✗ Parse failed, using raw text")
        return {"name": fw_name, "raw_text": result[:2000]}


# ── Pass 2b: Orthogonal angle queries ────────────────────────────
def query_angle(angle_name: str, angle_query: str) -> list:
    print(f"\n  📐 Angle: {angle_name}")

    rag = query_lightrag(angle_query)

    prompt = f"""Extract ALL named frameworks, methodologies, or systems from Koray Gubur's writing.

Focus specifically on: {angle_name.upper().replace('_', ' ')} angle.

For each framework found:
- name: exact name Koray uses
- definition: 1-2 sentence summary
- confidence: "core" / "secondary" / "emerging"

IMPORTANT: Only include frameworks NOT already in this list (these are known):
- Holistic SEO
- Topical Authority
- Semantic SEO
- Entity-based SEO Projects
- Topical Maps
- SaaS SEO
- Theoretical SEO
- Flywheel Model

Return ONLY a JSON array of NEW framework objects. If none found, return [].

CONTEXT:
"""
    prompt += rag[:6000]

    result = call_ollama(
        "Extract NEW frameworks only. Return ONLY valid JSON array.",
        prompt,
        max_tokens=3000,
    )
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, list):
        if parsed:
            names = [f.get("name", "?") for f in parsed]
            print(f"    ✓ {len(parsed)} new: {', '.join(names)}")
            return parsed
        else:
            print(f"    No new frameworks found")
            return []
    else:
        print(f"    ✗ Parse failed")
        return []


# ── Pass 2c: Framework adjacency query ───────────────────────────
def query_adjacent(fw_name: str) -> list:
    """Query for frameworks that are RELATED to but DISTINCT from this one."""
    print(f"\n  🔗 Adjacent to: {fw_name}")

    rag = query_lightrag(
        f"What specific frameworks, methods, or sub-systems does Koray Gubur describe "
        f"that are related to or built on top of {fw_name}? "
        f"What are the sub-components or specialized applications?"
    )

    prompt = f"""Find frameworks or named methods that are RELATED to "{fw_name}" but DISTINCT from it.

These are sub-frameworks, applications, or specialized variants, NOT the main framework itself.

For each:
- name: exact name
- relationship: how it relates to "{fw_name}" (e.g., "sub-component", "application", "variant")
- definition: 1 sentence

Return ONLY a JSON array. If none found, return [].

CONTEXT:
"""
    prompt += rag[:5000]

    result = call_ollama(
        "Find sub-frameworks. Return ONLY valid JSON array.",
        prompt,
        max_tokens=2000,
    )
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, list):
        if parsed:
            names = [f.get("name", "?") for f in parsed]
            print(f"    ✓ {len(parsed)} adjacent: {', '.join(names)}")
            return parsed
        else:
            return []
    else:
        return []


# ── Main ─────────────────────────────────────────────────────────
def main():
    start = time.time()

    # Load Pass 1 output for reference
    pass1_path = f"{OUTDIR}/frameworks.json"
    with open(pass1_path) as f:
        pass1 = json.load(f)
    print(f"Loaded Pass 1: {len(pass1['frameworks'])} frameworks")

    all_deep_dives = {}
    all_new_frameworks = []
    seen_names = set(SEED_FRAMEWORKS)

    # Pass 2a: Deep-dive each seed framework
    print("\n═══ PASS 2a: Deep-dive per framework ═══")
    for fw_name in SEED_FRAMEWORKS:
        deep = deep_dive_framework(fw_name)
        all_deep_dives[fw_name] = deep
        time.sleep(1)

    # Pass 2b: Orthogonal angle queries
    print("\n═══ PASS 2b: Orthogonal angle queries ═══")
    for angle_name, angle_query in ANGLE_QUERIES:
        new_fws = query_angle(angle_name, angle_query)
        for fw in new_fws:
            name = fw.get("name", "")
            if name and name not in seen_names:
                all_new_frameworks.append(fw)
                seen_names.add(name)
        time.sleep(1)

    # Pass 2c: Adjacent framework queries
    print("\n═══ PASS 2c: Adjacent framework discovery ═══")
    for fw_name in SEED_FRAMEWORKS:
        adjacent = query_adjacent(fw_name)
        for fw in adjacent:
            name = fw.get("name", "")
            if name and name not in seen_names:
                fw["source"] = f"adjacent-to-{fw_name}"
                all_new_frameworks.append(fw)
                seen_names.add(name)
        time.sleep(1)

    # Assemble Pass 2 output
    output = {
        "pass": 2,
        "architect": pass1["architect"],
        "deep_dives": all_deep_dives,
        "new_frameworks_found": all_new_frameworks,
        "total_new": len(all_new_frameworks),
        "framework_names_after_pass2": sorted(list(seen_names)),
    }

    outpath = f"{OUTDIR}/pass2_deep_dives.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"✅ Pass 2 complete in {elapsed:.0f}s")
    print(f"   Deep-dives: {len(all_deep_dives)} frameworks")
    print(f"   New frameworks found: {len(all_new_frameworks)}")
    if all_new_frameworks:
        print(f"   New names: {', '.join(f.get('name','?') for f in all_new_frameworks)}")
    print(f"   Total frameworks after Pass 2: {len(seen_names)}")
    print(f"   Output: {outpath}")


if __name__ == "__main__":
    main()
