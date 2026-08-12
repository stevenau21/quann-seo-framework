#!/usr/bin/env python3
"""
Phase 3 (Rebuilt): Direct Document Extraction
=============================================
Uses Phase 2's entity-to-document mapping to find the right docs,
then feeds FULL document content to Ollama for extraction.

Key differences from failed v1 and v2:
- v1 (Phase 3 extract): fed first 2000 chars of random docs → "Skip to content" = all "not found"
- v2 (retrieval.py): would re-query LightRAG = unnecessary indirection
- THIS (v3): uses entity→doc mapping from Phase 2, feeds FULL docs, hypothesis-driven

The enterprise architecture:
  Phase 2 discovered → WHAT frameworks exist (by graph structure)
  Phase 3 confirms →    WHAT each framework IS (by reading the source)

No sampling. No truncation. No blind guessing.
"""

import json
import time
import httpx
import re
from collections import defaultdict, Counter
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
WORKSPACE = "/home/steve/lightrag-apps/koray-gubur/workspace"
DOCS_PATH = f"{WORKSPACE}/kv_store_full_docs.json"
ENTITIES_PATH = f"{WORKSPACE}/kv_store_full_entities.json"
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "deepseek-v4-flash:cloud"  # 1M context window — feed ALL matching docs
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"

# ── Curated framework list from Phase 2 community detection ──────
# These are the actual distinct frameworks we discovered, 
# deduplicated from the 12 overlapping communities.

FRAMEWORK_QUERIES = {
    "Topical Authority": [
        "topical authority", "topical map", "topical coverage", 
        "topical authority course", "semantic content network"
    ],
    "Semantic SEO": [
        "semantic seo", "semantic search", "semantic content",
        "semantic structure", "semantic html"
    ],
    "Holistic SEO": [
        "holistic seo", "holistic seo & digital", "holistic seo process",
        "holistic approach"
    ],
    "Entity-Based SEO": [
        "entity-based seo", "entity-based search", "entity optimization",
        "entity seo", "entity-oriented search"
    ],
    "Technical SEO": [
        "technical seo", "technical infrastructure", "crawl budget",
        "page speed", "core web vitals"
    ],
    "SEO Information Retrieval": [
        "information retrieval", "ranking signals", "ranking factors",
        "search engine algorithms", "rankbrain", "page rank"
    ],
    "Content Quality & Linguistics": [
        "content quality", "content writing", "linguistic quality",
        "thin content", "content depth", "e-a-t"
    ],
    "Multilingual & International SEO": [
        "multilingual seo", "international seo", "multi regional",
        "hreflang", "localization"
    ],
    "Knowledge Graph & Structured Data": [
        "knowledge graph", "knowledge panel", "structured data",
        "schema", "entity disambiguation"
    ],
    "Python & Data-Driven SEO": [
        "python seo", "data science", "nltk", "scrapy",
        "log file analysis", "a/b test"
    ],
    "Conversion & Growth": [
        "flywheel model", "conversion rate", "b2p marketing",
        "content marketing", "inbound marketing"
    ],
    "SEO Case Study Methodology": [
        "seo case stud", "case study methodology", "seo project",
        "seo research"
    ],
}

EXTRACTION_PROMPT = """You are analyzing a collection of documents from SEO expert Koray Gubur's writings.

These documents have been identified as the most relevant sources for understanding:
FRAMEWORK: {framework_name}

Read the documents below and extract EVERYTHING about this framework:

1. DEFINITION: How does Koray define "{framework_name}"? What is it?
   (2-3 sentences using his own terminology and framing)

2. CORE CONCEPTS: What are the key ideas, principles, or pillars?
   (List 5-10 specific named concepts)

3. METHODS & TECHNIQUES: What specific steps, procedures, or how-to 
   instructions does Koray provide? Include numbered steps if available.

4. EVOLUTION: How has this framework changed or developed over time?
   Are there versions, iterations, or historical context?

5. DEPENDENCIES: What other frameworks, concepts, or disciplines does 
   this depend on or draw from?

6. UNIQUE POSITION: What makes Koray's version of "{framework_name}" 
   different from generic SEO advice or competing approaches?

7. EVIDENCE & CITATIONS: What sources, patents, research, or practitioners 
   does Koray cite to support this framework?

8. NUANCES & EDGE CASES: Subtle details, exceptions, or warnings that 
   Koray emphasizes.

Be THOROUGH. These are the PRIMARY SOURCES. Extract everything.
If the documents don't cover a section, write "not covered in these documents."

DOCUMENTS:
{documents}

Return ONLY a JSON object with keys: definition, core_concepts, methods, 
evolution, dependencies, unique_position, evidence, nuances."""


def call_ollama(system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> str:
    for attempt in range(3):
        try:
            with httpx.Client(timeout=300.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "temperature": 0.2,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    },
                )
                resp.raise_for_status()
                content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                if content:
                    return content.strip()
        except Exception as e:
            if attempt == 2:
                return f"ERROR: {e}"
            time.sleep(3)
    return ""


def try_parse_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except:
        pass
    for pattern in [r'```(?:json)?\s*(.*?)```', r'```\s*(.*?)```']:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return None


def find_relevant_docs(framework_keywords, entities_data, docs_data):
    """Find documents containing framework-related entities."""
    # Build entity→docs index
    entity_docs = defaultdict(set)
    for doc_id, entry in entities_data.items():
        for name in entry.get("entity_names", []):
            entity_docs[name.lower().strip()].add(doc_id)
    
    # Score documents by how many framework keywords they match
    doc_scores = Counter()
    doc_entity_hits = defaultdict(list)
    
    for doc_id in docs_data:
        doc_content = docs_data[doc_id].get("content", "").lower()
        doc_entities = entity_docs.get(doc_id, set())
        
        # Keyword hits in content
        for kw in framework_keywords:
            count = doc_content.count(kw.lower())
            if count > 0:
                doc_scores[doc_id] += count
        
        # Entity hits
        doc_entities_set = set()
        for entry in entities_data.values():
            if doc_id == entry.get("_id", ""):
                doc_entities_set = set(e.lower() for e in entry.get("entity_names", []))
                break
        
        matching_entities = [e for e in doc_entities_set if any(kw in e for kw in framework_keywords)]
        doc_entity_hits[doc_id] = matching_entities
        doc_scores[doc_id] += len(matching_entities) * 2  # Entity matches weighted higher
    
    # Get top docs
    top_docs = [doc_id for doc_id, score in doc_scores.most_common(20) if score > 0]
    return top_docs


def extract_framework(fw_name, keywords, docs_data, entities_data):
    """Extract a single framework by finding its source docs and feeding to Ollama."""
    print(f"\n{'='*60}")
    print(f"  🔍 {fw_name}")
    print(f"     Keywords: {', '.join(keywords[:4])}...")
    
    # Find relevant documents
    relevant_docs = find_relevant_docs(keywords, entities_data, docs_data)
    print(f"     Docs found: {len(relevant_docs)}")
    
    if not relevant_docs:
        print(f"     ⚠ No documents found!")
        return {"name": fw_name, "status": "no_docs_found"}
    
    # Assemble full document content (up to 200,000 chars — DeepSeek v4 Flash can handle this)
    doc_contents = []
    total_chars = 0
    for doc_id in relevant_docs:
        content = docs_data[doc_id].get("content", "")
        if len(content) < 200:
            continue
        
        # Find relevant sections — give the full doc but annotate
        doc_contents.append(f"\n### DOCUMENT ###\n{content}")
        total_chars += len(content)
        
        if total_chars > 200000:
            break
    
    combined_docs = "\n".join(doc_contents)
    print(f"     Content: {total_chars:,} chars from {len(doc_contents)} docs")
    
    # Build prompt
    prompt = EXTRACTION_PROMPT.format(
        framework_name=fw_name,
        documents=combined_docs[:200000]
    )
    
    system = f"You are extracting detailed information about Koray Gubur's '{fw_name}' framework from his original writings. Be thorough and precise. Return ONLY valid JSON."
    
    # Call ollama
    result = call_ollama(system, prompt, max_tokens=8000)
    
    parsed = try_parse_json(result)
    if parsed and isinstance(parsed, dict):
        # Quality assessment
        has_def = bool(parsed.get("definition") and len(parsed.get("definition", "")) > 50)
        has_core = bool(parsed.get("core_concepts") and len(parsed.get("core_concepts", [])) >= 2)
        has_methods = bool(parsed.get("methods") and len(str(parsed.get("methods", ""))) > 50)
        
        quality = sum([has_def, has_core, has_methods])
        parsed["_metadata"] = {
            "quality_score": quality,
            "docs_analyzed": len(doc_contents),
            "total_chars": total_chars,
            "has_definition": has_def,
            "has_core_concepts": has_core,
            "has_methods": has_methods,
        }
        
        print(f"     ✓ Quality: {quality}/3")
        return parsed
    else:
        print(f"     ✗ Parse failed ({len(result)} chars raw)")
        return {
            "name": fw_name, 
            "status": "parse_failed",
            "_raw_length": len(result) if result else 0,
            "_raw_preview": result[:300] if result else "",
        }


def main():
    print("═══ Phase 3 (v3): Direct Document Extraction ═══\n")
    
    # Load data
    print("Loading data...")
    with open(DOCS_PATH) as f:
        docs_data = json.load(f)
    with open(ENTITIES_PATH) as f:
        entities_data = json.load(f)
    
    print(f"  {len(docs_data)} documents")
    print(f"  {len(entities_data)} entity sets")
    
    # Extract each framework
    extractions = {}
    all_start = time.time()
    
    for fw_name, keywords in FRAMEWORK_QUERIES.items():
        extraction = extract_framework(fw_name, keywords, docs_data, entities_data)
        extractions[fw_name] = extraction
        
        # Checkpoint after each
        output = {
            "metadata": {
                "phase": 3,
                "version": "v4-deepseek-flash",
                "model": "deepseek-v4-flash:cloud",
                "date": datetime.now().isoformat(),
                "completed": len(extractions),
                "total": len(FRAMEWORK_QUERIES),
            },
            "extractions": extractions,
        }
        
        outpath = f"{OUTDIR}/phase3_extractions_v4_deepseek.json"
        with open(outpath, "w") as f:
            json.dump(output, f, indent=2)
        
        time.sleep(5)  # DeepSeek cloud respects rate limits
    
    # Summary
    elapsed = time.time() - all_start
    successful = sum(1 for e in extractions.values() if e.get("_metadata", {}).get("quality_score", 0) >= 2)
    partial = sum(1 for e in extractions.values() if e.get("_metadata", {}).get("quality_score", 0) == 1)
    failed = sum(1 for e in extractions.values() if "status" in e)
    
    print(f"\n{'='*60}")
    print(f"✅ Phase 3 complete in {elapsed:.0f}s")
    print(f"   High quality (≥2): {successful}/{len(extractions)}")
    print(f"   Partial (1): {partial}/{len(extractions)}")
    print(f"   Failed: {failed}/{len(extractions)}")
    
    for name, ext in extractions.items():
        q = ext.get("_metadata", {}).get("quality_score", 0)
        icon = "✅" if q >= 2 else "⚠️" if q == 1 else "❌"
        status = ext.get("status", f"q={q}")
        print(f"   {icon} {name}: {status}")
    
    print(f"\n   Output: {outpath}")


if __name__ == "__main__":
    main()
