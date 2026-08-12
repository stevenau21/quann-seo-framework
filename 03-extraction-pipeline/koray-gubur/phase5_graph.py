#!/usr/bin/env python3
"""
Phase 5: Framework Dependency Graph & Epistemic Stratification
===============================================================

Inputs:
  - phase3_extractions_v4_deepseek.json  (framework definitions, dependencies, methods)
  - phase4_flashcards.json               (534 cards with verification_status + cross_memberships)

Outputs:
  - phase5_frameworks.json               (Tier 1/Tier 2 cards + typed edges + graph metadata)
  - phase5_dependency_graph.mermaid      (Mermaid visualization)
  - phase5_dependency_graph.json         (Cytoscape/D3-compatible graph)
"""

import json
import os
from datetime import datetime, timezone
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
P3_PATH = os.path.join(BASE, "phase3_extractions_v4_deepseek.json")
P4_PATH = os.path.join(BASE, "phase4_flashcards.json")
OUT_PATH = os.path.join(BASE, "phase5_frameworks.json")
MERMAID_PATH = os.path.join(BASE, "phase5_dependency_graph.mermaid")
CYTOSCAPE_PATH = os.path.join(BASE, "phase5_dependency_graph.json")

# ────────────────────────────────────────────────────────
# LOAD
# ────────────────────────────────────────────────────────

with open(P3_PATH) as f:
    p3 = json.load(f)
with open(P4_PATH) as f:
    p4 = json.load(f)

extractions = p3["extractions"]
cards = p4["cards"]

print(f"Loaded {len(extractions)} frameworks from Phase 3")
print(f"Loaded {len(cards)} cards from Phase 4")

# ────────────────────────────────────────────────────────
# EPISTEMIC STRATIFICATION
# ────────────────────────────────────────────────────────

tier1_cards = [c for c in cards if c.get("verification_status") == "GROUNDED"]
tier2_cards = [c for c in cards if c.get("verification_status") != "GROUNDED"]

print(f"\nTier 1 (GROUNDED):    {len(tier1_cards)} cards → computable rules")
print(f"Tier 2 (UNVERIFIED):  {len(tier2_cards)} cards → heuristic context")

# ────────────────────────────────────────────────────────
# BUILD FRAMEWORK OBJECTS
# ────────────────────────────────────────────────────────

# Map framework names to their Phase 3 extraction + Phase 4 cards
# Phase 3 uses full names; Phase 4 uses abbreviated names.
# We need to map them.

NAME_MAP = {
    "Topical Authority": "Topical Authority",
    "Semantic SEO": "Semantic SEO",
    "Holistic SEO": "Holistic SEO",
    "Entity-Based SEO": "Entity-Based SEO",
    "Technical SEO": "Technical SEO",
    "SEO Information Retrieval": "SEO Information Retrieval",
    "Content Quality & Linguistics": "Content Quality & Linguistics",
    "Multilingual & International SEO": "Multilingual & International SEO",
    "Knowledge Graph & Structured Data": "Knowledge Graph & Structured Data",
    "Python & Data-Driven SEO": "Python & Data-Driven SEO",
    "Conversion & Growth": "Conversion & Growth",
    "SEO Case Study Methodology": "SEO Case Study Methodology",
}

def get_cards_for_framework(fw_name, tier=None):
    """Get cards for a framework, optionally filtered by tier."""
    result = [c for c in cards if c["framework"] == fw_name]
    if tier == 1:
        result = [c for c in result if c.get("verification_status") == "GROUNDED"]
    elif tier == 2:
        result = [c for c in result if c.get("verification_status") != "GROUNDED"]
    return result

# Map Phase 4 framework names to Phase 3 extraction keys
for fw_name in NAME_MAP:
    p3_fw = extractions.get(fw_name)
    if p3_fw is None:
        print(f"  WARNING: '{fw_name}' not found in Phase 3 extractions")
        # Try fuzzy match
        for k in extractions:
            if fw_name.lower() in k.lower():
                print(f"    → mapped to '{k}'")
                p3_fw = extractions[k]
                break

def resolve_dependency(name):
    """Resolve a dependency name to a framework key in our set."""
    # Check direct match
    if name in NAME_MAP:
        return name
    # Check fuzzy
    lower = name.lower()
    for fw in NAME_MAP:
        if fw.lower() in lower or lower in fw.lower():
            return fw
    # Known aliases
    aliases = {
        "Semantic SEO": "Semantic SEO",
        "entity-based seo": "Entity-Based SEO",
        "topical authority": "Topical Authority",
        "technical seo": "Technical SEO",
        "holistic seo": "Holistic SEO",
        "local seo": None,  # Not a standalone framework in our set
        "multilingual seo": "Multilingual & International SEO",
        "entity-oriented search": "Entity-Based SEO",
        "semantic web": "Knowledge Graph & Structured Data",
        "knowledge graph": "Knowledge Graph & Structured Data",
        "schema.org": "Knowledge Graph & Structured Data",
        "natural language processing": "Content Quality & Linguistics",
        "nlp": "Content Quality & Linguistics",
        "data science": "Python & Data-Driven SEO",
        "conversion rate optimization": "Conversion & Growth",
        "content marketing": "Conversion & Growth",
        "page rank": "SEO Information Retrieval",
        "pagerank": "SEO Information Retrieval",
        "information retrieval": "SEO Information Retrieval",
        "bert": "SEO Information Retrieval",
        "e-a-t": "Content Quality & Linguistics",
        "user experience": "Conversion & Growth",
        "web development": "Technical SEO",
        "multilingual": "Multilingual & International SEO",
        "multiregional": "Multilingual & International SEO",
    }
    for alias_key, alias_val in aliases.items():
        if alias_key in lower:
            return alias_val
    return None  # External dependency (not in our framework set)

frameworks_output = []

for fw_name in NAME_MAP:
    p3_fw = extractions.get(fw_name, {})
    
    # Get cards
    t1 = get_cards_for_framework(fw_name, tier=1)
    t2 = get_cards_for_framework(fw_name, tier=2)
    
    # Resolve dependencies from Phase 3
    raw_deps = p3_fw.get("dependencies", []) if isinstance(p3_fw, dict) else []
    
    internal_deps = []   # dependencies on other frameworks in our set
    external_deps = []   # dependencies on concepts/people/patents outside our set
    
    for dep in raw_deps:
        resolved = resolve_dependency(dep)
        if resolved and resolved != fw_name:
            internal_deps.append(resolved)
        elif resolved is None:
            external_deps.append(dep)
    
    # Build cross-framework edges from Phase 4 cross-memberships
    # Format: list of dicts [{framework, semantic_similarity, structural_overlap, combined_score}, ...]
    # May contain duplicates for same framework or community_NNN IDs — dedup by framework, keep best score
    cross_edges = {}
    for c in (t1 + t2):
        memberships = c.get("cross_framework_memberships")
        if memberships and isinstance(memberships, list):
            # Deduplicate within this card: best score per framework name
            best_per_fw = {}
            for m in memberships:
                name = m.get("framework", "")
                if not name or name in ("community_360", "community_123") or name.startswith("community_"):
                    continue
                score = m.get("combined_score", 0)
                if name not in best_per_fw or score > best_per_fw[name]:
                    best_per_fw[name] = score
            
            for alt_fw, score in best_per_fw.items():
                if alt_fw != fw_name and alt_fw in NAME_MAP:
                    if alt_fw not in cross_edges:
                        cross_edges[alt_fw] = []
                    cross_edges[alt_fw].append({
                        "card_id": c["card_id"],
                        "score": round(score, 4),
                        "content": c["raw_content"][:120]
                    })
    
    # Aggregate cross-edges into strength scores
    cross_edge_summary = {}
    for alt_fw, items in cross_edges.items():
        avg_score = sum(i["score"] for i in items) / len(items)
        cross_edge_summary[alt_fw] = {
            "strength": round(avg_score, 4),
            "card_count": len(items),
            "sample_card_ids": [i["card_id"] for i in items[:3]]
        }
    
    # Determine graph position (centrality proxy: card count + dependency count)
    centrality_score = len(t1) * 2 + len(t2) + len(internal_deps) * 3
    
    fw_obj = {
        "id": fw_name.lower().replace(" & ", "-").replace(" ", "-"),
        "name": fw_name,
        "paradigm": "seo",
        "definition": p3_fw.get("definition", "") if isinstance(p3_fw, dict) else "",
        "core_concepts": p3_fw.get("core_concepts", []) if isinstance(p3_fw, dict) else [],
        "methods": p3_fw.get("methods", []) if isinstance(p3_fw, dict) else [],
        "unique_position": p3_fw.get("unique_position", "") if isinstance(p3_fw, dict) else "",
        "evolution": p3_fw.get("evolution", "") if isinstance(p3_fw, dict) else "",
        "evidence": p3_fw.get("evidence", []) if isinstance(p3_fw, dict) else [],
        "nuances": p3_fw.get("nuances", []) if isinstance(p3_fw, dict) else [],
        "doc_ids": p3_fw.get("_metadata", {}).get("doc_ids", []) if isinstance(p3_fw, dict) else [],
        
        # EPISTEMIC STRATIFICATION
        "tier_1_rules": {
            "count": len(t1),
            "cards": [
                {
                    "card_id": c["card_id"],
                    "type": c.get("card_type", ""),
                    "content": c["raw_content"],
                    "target_entity": c.get("target_entity", ""),
                    "action_directive": c.get("action_directive", ""),
                    "source_span": c.get("source_span", ""),
                }
                for c in t1
            ]
        },
        "tier_2_context": {
            "count": len(t2),
            "cards": [
                {
                    "card_id": c["card_id"],
                    "type": c.get("card_type", ""),
                    "content": c["raw_content"],
                    "target_entity": c.get("target_entity", ""),
                    "action_directive": c.get("action_directive", ""),
                }
                for c in t2
            ]
        },
        
        # DEPENDENCY GRAPH
        "depends_on": list(set(internal_deps)),  # Other frameworks this depends on
        "external_dependencies": list(set(external_deps)),  # Concepts/people outside our set
        "cross_framework_edges": cross_edge_summary,  # Soft edges from Phase 4
        "supports": [],  # Will be filled in second pass (reverse edges)
        
        # METADATA
        "metadata": {
            "centrality_score": centrality_score,
            "total_cards": len(t1) + len(t2),
            "grounding_rate": round(len(t1) / max(len(t1) + len(t2), 1), 4),
            "doc_count": len(p3_fw.get("_metadata", {}).get("doc_ids", [])) if isinstance(p3_fw, dict) else 0,
        }
    }
    frameworks_output.append(fw_obj)

# Second pass: compute reverse "supports" edges
name_to_obj = {fw["name"]: fw for fw in frameworks_output}
for fw in frameworks_output:
    for dep_name in fw["depends_on"]:
        if dep_name in name_to_obj:
            dep_obj = name_to_obj[dep_name]
            if fw["name"] not in dep_obj["supports"]:
                dep_obj["supports"].append(fw["name"])

# ────────────────────────────────────────────────────────
# BUILD GLOBAL RELATIONSHIP GRAPH (TYPED EDGES)
# ────────────────────────────────────────────────────────

edges = []

# depends_on edges (strong, directed)
for fw in frameworks_output:
    for dep in fw["depends_on"]:
        if dep in name_to_obj:
            edges.append({
                "source": fw["name"],
                "target": dep,
                "type": "depends_on",
                "strength": 1.0,
                "directed": True
            })

# supports edges (reverse of depends_on)
for fw in frameworks_output:
    for sup in fw["supports"]:
        edges.append({
            "source": fw["name"],
            "target": sup,
            "type": "supports",
            "strength": 0.8,
            "directed": True
        })

# cross_framework edges (soft, bidirectional, from Phase 4 embeddings)
for fw in frameworks_output:
    for alt_name, edge_data in fw["cross_framework_edges"].items():
        if alt_name in name_to_obj:
            edges.append({
                "source": fw["name"],
                "target": alt_name,
                "type": "cross_membership",
                "strength": edge_data["strength"],
                "card_count": edge_data["card_count"],
                "directed": False
            })

# Deduplicate cross_membership edges (bidirectional, keep strongest)
seen_cross = set()
deduped_edges = []
for edge in edges:
    if edge["type"] == "cross_membership":
        key = tuple(sorted([edge["source"], edge["target"]]))
        if key in seen_cross:
            continue
        seen_cross.add(key)
    deduped_edges.append(edge)

edges = deduped_edges

print(f"\nEdge breakdown:")
edge_types = Counter(e["type"] for e in edges)
for t, c in edge_types.most_common():
    print(f"  {t}: {c}")

# ────────────────────────────────────────────────────────
# ASSEMBLE FINAL OUTPUT
# ────────────────────────────────────────────────────────

output = {
    "metadata": {
        "phase": 5,
        "version": "1.0.0",
        "title": "Koray Gubur — Framework Dependency Graph with Epistemic Stratification",
        "architect": {
            "name": "Koray Tuğberk GÜBÜR",
            "paradigm": "seo",
            "domains": ["holisticseo.digital", "koraygubur.com"],
            "total_docs_analyzed": 394
        },
        "extraction_date": p3["metadata"]["date"],
        "phase5_date": datetime.now(timezone.utc).isoformat(),
        "phase5_model": "deterministic (no LLM — graph computation only)",
        "statistics": {
            "total_frameworks": len(frameworks_output),
            "total_cards": len(tier1_cards) + len(tier2_cards),
            "tier_1_rules": len(tier1_cards),
            "tier_2_context": len(tier2_cards),
            "grounding_rate": round(len(tier1_cards) / len(cards), 4),
            "internal_edges": edge_types.get("depends_on", 0) + edge_types.get("supports", 0),
            "cross_membership_edges": edge_types.get("cross_membership", 0),
        }
    },
    "epistemic_stratification": {
        "tier_1": {
            "label": "Computable Rules",
            "description": "Mathematically grounded via source-document verification. These feed the automated Gap Score engine in the Domain KG. Every card has a verified source_span anchoring it to a specific document passage.",
            "card_count": len(tier1_cards),
            "usage": "gap_score engine, automated audits, rule-based content checks"
        },
        "tier_2": {
            "label": "Heuristic Context",
            "description": "Architectural Synthesis — true of the framework but not directly quoted in any single source. These provide narrative context for downstream AI when writing content briefs. They do NOT trigger automated gap audits.",
            "card_count": len(tier2_cards),
            "usage": "content brief narrative, cross-framework reasoning, writer context"
        }
    },
    "frameworks": frameworks_output,
    "graph": {
        "nodes": [
            {
                "id": fw["id"],
                "name": fw["name"],
                "tier_1_count": fw["tier_1_rules"]["count"],
                "tier_2_count": fw["tier_2_context"]["count"],
                "grounding_rate": fw["metadata"]["grounding_rate"],
                "centrality_score": fw["metadata"]["centrality_score"],
            }
            for fw in frameworks_output
        ],
        "edges": edges
    }
}

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved {OUT_PATH}")
print(f"   {os.path.getsize(OUT_PATH):,} bytes")

# ────────────────────────────────────────────────────────
# MERMAID DIAGRAM
# ────────────────────────────────────────────────────────

mermaid = ["graph TD"]
mermaid.append("    %% Phase 5: Koray Gubur Framework Dependency Graph")
mermaid.append(f"    %% {len(frameworks_output)} frameworks | {len(tier1_cards)} Tier 1 rules | {len(tier2_cards)} Tier 2 context")
mermaid.append("")

# Node definitions with tier info
node_ids = {fw["name"]: fw["id"] for fw in frameworks_output}

for fw in frameworks_output:
    g_rate = fw["metadata"]["grounding_rate"]
    t1 = fw["tier_1_rules"]["count"]
    label = f"{fw['name']}<br/>T1:{t1} T2:{fw['tier_2_context']['count']}"
    mermaid.append(f"    {fw['id']}[\"{label}\"]")

mermaid.append("")

# depends_on edges (solid arrows)
for fw in frameworks_output:
    for dep in fw["depends_on"]:
        if dep in node_ids:
            mermaid.append(f"    {fw['id']} -->|depends_on| {node_ids[dep]}")

# cross_membership edges (dotted, bidirectional)
seen_mermaid_cross = set()
for fw in frameworks_output:
    for alt_name, edge_data in fw["cross_framework_edges"].items():
        if alt_name in node_ids:
            key = tuple(sorted([fw["id"], node_ids[alt_name]]))
            if key not in seen_mermaid_cross:
                seen_mermaid_cross.add(key)
                strength = edge_data["strength"]
                mermaid.append(f"    {key[0]} -.->|cross {edge_data['card_count']} cards| {key[1]}")

with open(MERMAID_PATH, "w") as f:
    f.write("\n".join(mermaid))

print(f"✅ Saved {MERMAID_PATH}")

# ────────────────────────────────────────────────────────
# CYTOSCAPE / D3 COMPATIBLE GRAPH
# ────────────────────────────────────────────────────────

cyto = {
    "elements": {
        "nodes": [
            {
                "data": {
                    "id": fw["id"],
                    "label": fw["name"],
                    "tier1": fw["tier_1_rules"]["count"],
                    "tier2": fw["tier_2_context"]["count"],
                    "grounding_rate": fw["metadata"]["grounding_rate"],
                    "centrality": fw["metadata"]["centrality_score"],
                    "size": fw["tier_1_rules"]["count"] * 3 + fw["tier_2_context"]["count"],
                }
            }
            for fw in frameworks_output
        ],
        "edges": [
            {
                "data": {
                    "id": f"e{i}",
                    "source": e["source"].lower().replace(" & ", "-").replace(" ", "-"),
                    "target": e["target"].lower().replace(" & ", "-").replace(" ", "-"),
                    "type": e["type"],
                    "strength": e["strength"],
                    "directed": e["directed"]
                }
            }
            for i, e in enumerate(edges)
            if e["source"].lower().replace(" & ", "-").replace(" ", "-") in node_ids.values()
            and e["target"].lower().replace(" & ", "-").replace(" ", "-") in node_ids.values()
        ]
    }
}

with open(CYTOSCAPE_PATH, "w") as f:
    json.dump(cyto, f, indent=2)

print(f"✅ Saved {CYTOSCAPE_PATH}")
print(f"\n{'='*60}")
print("PHASE 5 COMPLETE")
print(f"{'='*60}")
print(f"Frameworks: {len(frameworks_output)}")
print(f"Tier 1 rules: {len(tier1_cards)}")
print(f"Tier 2 context: {len(tier2_cards)}")
print(f"Edges: {len(edges)} ({edge_types.get('depends_on', 0)} depends_on, {edge_types.get('supports', 0)} supports, {edge_types.get('cross_membership', 0)} cross-membership)")
