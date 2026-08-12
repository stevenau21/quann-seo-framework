#!/usr/bin/env python3
"""
Phase 3: Targeted Framework Extraction
=======================================
For each community from Phase 2, finds the documents where its entities appear,
then does HYPOTHESIS-DRIVEN extraction. Instead of asking "what frameworks?", 
we ask "here are documents we believe discuss X — extract everything about X."

Output: phase3_extractions.json with deep framework descriptions.
"""

import json
import time
import httpx
import os
from collections import Counter, defaultdict
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
WORKSPACE = "/home/steve/lightrag-apps/koray-gubur/workspace"
DOCS_PATH = f"{WORKSPACE}/kv_store_full_docs.json"
ENTITIES_PATH = f"{WORKSPACE}/kv_store_full_entities.json"
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"

PHASE2_PATH = f"{OUTDIR}/phase2_communities.json"

# ── Merge overlapping communities ────────────────────────────────

def merge_communities(communities):
    """Merge communities with overlapping framework names."""
    merged = []
    used = set()
    
    # Sort by size descending
    communities = sorted(communities, key=lambda x: x["size"], reverse=True)
    
    # Extract framework names
    def get_fw_name(comm):
        return comm.get("framework", {}).get("name", "").lower()
    
    # Group by similar names
    for i, comm in enumerate(communities):
        if i in used:
            continue
        
        name = get_fw_name(comm)
        group = [comm]
        used.add(i)
        
        # Find overlapping communities
        for j, other in enumerate(communities):
            if j in used:
                continue
            
            other_name = get_fw_name(other)
            
            # Check name overlap
            name_words = set(name.split())
            other_words = set(other_name.split())
            overlap = name_words & other_words
            
            # Significant word overlap = same framework
            if len(overlap) >= 3 or (
                len(overlap) >= 2 and len(overlap) / min(len(name_words), len(other_words)) > 0.5
            ):
                group.append(other)
                used.add(j)
        
        # Merge
        if len(group) > 1:
            merged_entities = []
            merged_central = []
            for g in group:
                merged_entities.extend(g["all_entities"])
                merged_central.extend(g["central_entities"])
            
            merged_comm = {
                "community_id": f"merged_{i}",
                "size": len(merged_entities),
                "central_entities": list(dict.fromkeys(merged_central))[:20],
                "all_entities": list(dict.fromkeys(merged_entities)),
                "sub_communities": len(group),
                "framework": group[0]["framework"],  # Keep first name
                "type_distribution": {},
            }
            # Combine type distributions
            combined_types = Counter()
            for g in group:
                for t, c in g.get("type_distribution", {}).items():
                    combined_types[t] += c
            merged_comm["type_distribution"] = dict(combined_types)
            
            merged.append(merged_comm)
        else:
            merged.append(comm)
    
    # Sort by size
    merged.sort(key=lambda x: x["size"], reverse=True)
    
    return merged


# ── Doc-to-community mapping ─────────────────────────────────────

def map_docs_to_communities(communities, entities_data, docs_data):
    """For each community, find which documents contain its entities."""
    
    # Build entity->docs index
    entity_docs = defaultdict(set)
    for doc_id, entry in entities_data.items():
        for name in entry.get("entity_names", []):
            entity_docs[name.lower().strip()].add(doc_id)
    
    # For each community, find docs
    community_docs = {}
    for comm in communities:
        # Only process communities with size >= 5
        if comm["size"] < 5:
            continue
        
        all_entities = [e.lower().strip() for e in comm["all_entities"]]
        docs = set()
        entity_hits = Counter()
        
        for entity in all_entities:
            entity_doc_set = entity_docs.get(entity, set()) | entity_docs.get(entity.title(), set())
            if entity_doc_set:
                docs.update(entity_doc_set)
                entity_hits[entity] = len(entity_doc_set)
        
        community_docs[comm["community_id"]] = {
            "community": comm,
            "docs": sorted(docs),
            "doc_count": len(docs),
            "top_entity_hits": entity_hits.most_common(10),
        }
    
    return community_docs


# ── Targeted extraction ──────────────────────────────────────────

def extract_framework(comm_docs, framework_name):
    """Deep-extract a single framework from its relevant documents."""
    
    comm = comm_docs["community"]
    doc_ids = comm_docs["docs"][:15]  # Limit to 15 docs
    central = comm.get("central_entities", [])[:10]
    
    print(f"\n  Extracting: {framework_name}")
    print(f"    Entities: {len(comm['all_entities'])}")
    print(f"    Docs: {len(doc_ids)} of {comm_docs['doc_count']}")
    print(f"    Central: {', '.join(central[:5])}")
    
    # Load documents
    with open(DOCS_PATH) as f:
        all_docs = json.load(f)
    
    # Assemble context
    context_parts = []
    total_chars = 0
    for doc_id in doc_ids:
        if doc_id in all_docs:
            content = all_docs[doc_id].get("content", "")
            # Extract relevant portions
            excerpt = content[:2000]  # First 2000 chars
            context_parts.append(f"--- Document ---\n{excerpt}\n")
            total_chars += len(excerpt)
            if total_chars > 12000:
                break
    
    context = "\n".join(context_parts)
    
    prompt = f"""This is a deep extraction of Koray Gubur's "{framework_name}" framework.

Based on the documents below (from Koray's writings), extract EVERYTHING about this framework:

1. DEFINITION: What is it? How does Koray define it? (2-3 sentences)
2. COMPONENTS: What are the sub-components, pillars, or building blocks?
3. METHODS: What specific techniques, steps, or procedures does he describe? 
   Include numbered steps if available.
4. EVOLUTION: How has this framework evolved? Any versions or iterations?
5. METRICS: What does he measure or track for this framework?
6. CONTEXT: When/why was this framework created? What problem did it solve?
7. NUANCES: Subtle distinctions Koray makes that set this apart from generic versions.
8. DEPENDENCIES: What other frameworks or concepts does this depend on?
9. UNIQUE_TERMS: Specific vocabulary or coinages unique to Koray's version.

Be thorough. If a section has no information, mark it as "not found."

DOCUMENTS:
{context[:12000]}

Return ONLY a JSON object with the keys: definition, components, methods, evolution, 
metrics, context, nuances, dependencies, unique_terms."""

    for attempt in range(3):
        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "temperature": 0.3,
                        "max_tokens": 3000,
                        "messages": [
                            {"role": "system", "content": "You extract detailed SEO framework information. Return ONLY valid JSON."},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
                resp.raise_for_status()
                result = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse
                import re
                try:
                    parsed = json.loads(result.strip())
                except:
                    match = re.search(r'\{[\s\S]*\}', result)
                    if match:
                        parsed = json.loads(match.group(0))
                    else:
                        parsed = {"error": "parse_failed", "raw": result[:500]}
                
                return parsed
        except Exception as e:
            if attempt == 2:
                return {"error": str(e)}
            time.sleep(2)
    
    return {"error": "all_attempts_failed"}


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("═══ Phase 3: Targeted Extraction ═══\n")
    
    # Load Phase 2 results
    print("Loading Phase 2 communities...")
    with open(PHASE2_PATH) as f:
        phase2 = json.load(f)
    
    communities = phase2["communities"]
    print(f"  {len(communities)} total communities")
    print(f"  {sum(1 for c in communities if c['size'] >= 5)} with size >= 5")
    
    # Merge overlapping communities
    print("\nMerging overlapping communities...")
    merged = merge_communities(communities)
    print(f"  {len(merged)} after merging (from {len(communities)})")
    
    # Load entity data for doc mapping
    print("\nLoading entity data...")
    with open(ENTITIES_PATH) as f:
        entities_data = json.load(f)
    
    # Map docs to communities
    print("Mapping documents to communities...")
    community_docs = map_docs_to_communities(merged, entities_data, {})
    
    print(f"\n  Community → Doc mapping:")
    for cid, cd in sorted(community_docs.items(), key=lambda x: x[1]["doc_count"], reverse=True):
        name = cd["community"].get("framework", {}).get("name", "?")
        print(f"    {cid}: {cd['doc_count']:3d} docs → {name}")
    
    # Targeted extraction for each community
    print("\n════ Targeted Extraction ════")
    extractions = []
    
    for cid, cd in community_docs.items():
        name = cd["community"].get("framework", {}).get("name", "?")
        if cd["doc_count"] == 0:
            print(f"\n  Skipping {name}: no documents mapped")
            continue
        
        extraction = extract_framework(cd, name)
        
        extractions.append({
            "community_id": cid,
            "framework_name": name,
            "doc_count": cd["doc_count"],
            "entity_count": cd["community"]["size"],
            "extraction": extraction,
        })
        
        # Intermediate save
        with open(f"{OUTDIR}/phase3_extractions.json", "w") as f:
            json.dump({
                "metadata": {
                    "phase": 3,
                    "date": datetime.now().isoformat(),
                    "total_extractions": len(extractions),
                },
                "extractions": extractions,
            }, f, indent=2)
        
        time.sleep(1)
    
    print(f"\n✅ Phase 3 complete")
    print(f"   Extractions: {len(extractions)}")


if __name__ == "__main__":
    main()
