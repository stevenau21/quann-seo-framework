#!/usr/bin/env python3
"""
Phase 3 (Fixed): LightRAG-Retrieval-Based Extraction
=====================================================
Uses LightRAG's semantic search to find the most relevant content
for each framework, then uses Ollama to structure that content.

Why this works when v1 failed:
- LightRAG's vector search finds semantically relevant passages
- We query by the framework name, getting targeted content
- Ollama only does STRUCTURING, not blind guessing
"""

import json
import time
import httpx
import re
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
LIGHTRAG_URL = "http://localhost:8012"
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"
PHASE2_PATH = f"{OUTDIR}/phase2_communities.json"

# ── Framework definitions from Phase 2 ───────────────────────────
# (curated from the community detection to avoid duplicates)

FRAMEWORKS_TO_EXTRACT = [
    "Topical Authority",
    "Semantic SEO",
    "Holistic SEO",
    "Entity-Based SEO",
    "Technical SEO",
    "Topical Maps",
    "Semantic Content Networks",
    "Frame Semantics",
    "Information Retrieval for SEO", 
    "Knowledge Graph Optimization",
    "Query-Intent Mapping",
    "Signal Reinterpretation (RankBrain-era ranking factors)",
    "Author Rank / Agent Rank",
    "SaaS SEO",
    "Multilingual SEO",
    "Page Speed & Core Web Vitals",
    "Crawl Budget Optimization",
    "Structured Data & Schema Markup",
    "Content Quality & Linguistic Precision",
    "E-A-T & Trustworthiness",
    "Conversion Rate Optimization",
    "Flywheel Model for SEO Growth",
    "SEO Project Management",
    "Python for SEO / Data-Driven SEO",
    "A/B Testing for SEO",
    "Log File Analysis",
]

def query_lightrag(query: str, mode: str = "hybrid") -> str:
    for attempt in range(3):
        try:
            with httpx.Client(timeout=90.0) as client:
                resp = client.post(
                    f"{LIGHTRAG_URL}/query",
                    json={"query": query, "mode": mode},
                )
                resp.raise_for_status()
                result = resp.json().get("response", "")
                if result and len(result) > 100:
                    return result
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return ""


def call_ollama(system: str, user: str, max_tokens: int = 4000) -> str:
    for attempt in range(3):
        try:
            with httpx.Client(timeout=180.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "temperature": 0.3,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                    },
                )
                resp.raise_for_status()
                content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content.strip()
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return ""


def try_parse_json(text: str):
    """Multiple strategies to parse LLM JSON output."""
    # Direct
    try:
        return json.loads(text)
    except:
        pass
    # Markdown fence
    for pattern in [r'```(?:json)?\s*(.*?)```', r'```\s*(.*?)```']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
    # JSON object
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return None


def extract_framework(name: str) -> dict:
    """Deep-extract one framework using LightRAG retrieval + Ollama structuring."""
    print(f"\n  🔍 {name}")
    
    # ── Query 1: Definition & Core Concepts ──────────────────────
    rag1 = query_lightrag(
        f"What is {name}? How does Koray Gubur define and explain {name}? "
        f"What are the core concepts and principles of {name}?"
    )
    
    if not rag1 or len(rag1) < 200:
        print(f"    ⚠ LightRAG returned insufficient content ({len(rag1)} chars)")
        return {"name": name, "status": "insufficient_rag_context"}
    
    print(f"    RAG1: {len(rag1)} chars")
    
    # ── Query 2: Methods & Implementation ────────────────────────
    rag2 = query_lightrag(
        f"How do you implement {name}? What are the specific steps, methods, "
        f"techniques, and procedures for {name} according to Koray Gubur?"
    )
    print(f"    RAG2: {len(rag2)} chars")
    
    # ── Query 3: Evolution & Context ─────────────────────────────
    rag3 = query_lightrag(
        f"How has {name} evolved over time? What is the history and context "
        f"of {name}? What problem was it created to solve?"
    )
    print(f"    RAG3: {len(rag3)} chars")
    
    # ── Query 4: Relationships & Dependencies ────────────────────
    rag4 = query_lightrag(
        f"What other frameworks, concepts, or methods does {name} depend on "
        f"or relate to? What does {name} contradict or challenge?"
    )
    print(f"    RAG4: {len(rag4)} chars")
    
    # ── Assemble context ─────────────────────────────────────────
    combined = (
        f"=== DEFINITION & CORE CONCEPTS ===\n{rag1[:6000]}\n\n"
        f"=== METHODS & IMPLEMENTATION ===\n{rag2[:4000]}\n\n"
        f"=== EVOLUTION & CONTEXT ===\n{rag3[:4000]}\n\n"
        f"=== RELATIONSHIPS & DEPENDENCIES ===\n{rag4[:4000]}"
    )
    
    # ── Structure with Ollama ────────────────────────────────────
    prompt = f"""You are extracting detailed information about Koray Gubur's "{name}" framework/methodology.

Read the LightRAG context below (four different query angles) and extract a COMPREHENSIVE analysis.

Return ONLY a JSON object with these keys:

{{
  "name": "{name}",
  "definition": "2-3 sentence definition in Koray's own framing",
  "problem_solved": "What was broken that this framework fixes?",
  "core_concepts": ["key concept 1", "key concept 2", ...],
  "components": ["sub-component 1", "sub-component 2", ...],
  "methods": [
    {{"name": "method name", "description": "...", "steps": ["step 1", "step 2"]}}
  ],
  "evolution": "How has this framework evolved over time? v1, v2, etc?",
  "metrics": "What does he measure or track for this framework?",
  "dependencies": ["other framework or concept this depends on"],
  "contradicts": "What conventional wisdom or competing approach does this challenge?",
  "unique_position": "What makes Koray's version of this different from generic approaches?",
  "evidence": ["specific claim 1 with source", "specific claim 2 with source"],
  "confidence": "high|medium|low - how well-supported is this extraction?"
}}

If a field has no information in the context, use an empty string, empty array, or "not mentioned in context" as appropriate.

Be thorough. Extract everything.

LIGHTRAG CONTEXT:
{combined[:14000]}

Return ONLY the JSON object. No markdown fences, no explanation."""

    result = call_ollama(
        "You extract detailed SEO framework information from search results. Return ONLY valid JSON.",
        prompt,
        max_tokens=4000,
    )
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        # Quality check
        has_def = bool(parsed.get("definition") and len(parsed.get("definition", "")) > 50)
        has_core = bool(parsed.get("core_concepts") and len(parsed.get("core_concepts", [])) > 0)
        has_methods = bool(parsed.get("methods") and len(parsed.get("methods", [])) > 0)
        
        quality = sum([has_def, has_core, has_methods])
        parsed["_quality_score"] = quality
        parsed["_rag_context_length"] = len(combined)
        
        print(f"    ✓ Quality: {quality}/3 — def={has_def}, core={has_core}, methods={has_methods}")
        return parsed
    else:
        print(f"    ✗ Parse failed. Saving raw output.")
        return {
            "name": name,
            "status": "parse_failed",
            "_raw_length": len(result) if result else 0,
            "_raw_preview": result[:500] if result else "",
        }


def main():
    print("═══ Phase 3 (Fixed): LightRAG-Retrieval Extraction ═══\n")
    print(f"Frameworks to extract: {len(FRAMEWORKS_TO_EXTRACT)}")
    
    extractions = []
    start = time.time()
    
    for i, name in enumerate(FRAMEWORKS_TO_EXTRACT):
        extraction = extract_framework(name)
        extraction["_order"] = i
        extractions.append(extraction)
        
        # Save after each extraction (checkpoint)
        output = {
            "metadata": {
                "phase": 3,
                "version": "fixed-lightrag-retrieval",
                "date": datetime.now().isoformat(),
                "frameworks_attempted": i + 1,
                "frameworks_total": len(FRAMEWORKS_TO_EXTRACT),
            },
            "extractions": extractions,
        }
        
        outpath = f"{OUTDIR}/phase3_extractions_v2.json"
        with open(outpath, "w") as f:
            json.dump(output, f, indent=2)
        
        # Rate limiting
        time.sleep(2)
    
    # Summary
    elapsed = time.time() - start
    successful = sum(1 for e in extractions if e.get("_quality_score", 0) >= 2)
    failed = sum(1 for e in extractions if e.get("status"))
    
    print(f"\n{'='*60}")
    print(f"✅ Phase 3 complete in {elapsed:.0f}s")
    print(f"   Successful (quality ≥ 2): {successful}/{len(extractions)}")
    print(f"   Failed: {failed}/{len(extractions)}")
    print(f"   Output: {outpath}")


if __name__ == "__main__":
    main()
