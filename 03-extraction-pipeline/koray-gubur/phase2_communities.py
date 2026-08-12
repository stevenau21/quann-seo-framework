#!/usr/bin/env python3
"""
Phase 2: Community Detection + LLM Naming
==========================================
Takes Phase 1's clean graph (1,043 entities, 1,434 edges) and:
1. Builds a weighted NetworkX graph
2. Runs Louvain community detection
3. For each community, uses Ollama to name it as a framework
4. Output: phase2_communities.json with named framework candidates
"""

import json
import time
import httpx
import networkx as nx
from networkx.algorithms.community import louvain_communities
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"
INPUT_PATH = f"{OUTDIR}/phase1_clean_graph.json"


def call_ollama(system: str, user: str, max_tokens: int = 2000) -> str:
    for attempt in range(3):
        try:
            with httpx.Client(timeout=120.0) as client:
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
                return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return ""


def name_community(entities: list[str], centrality: list[str]) -> dict:
    """Use Ollama to name a community and extract framework metadata."""
    
    # Show most central + random sample
    top_entities = centrality[:20]
    sample = list(dict.fromkeys(top_entities + entities[:40]))[:40]
    
    prompt = f"""Analyze this cluster of SEO-related concepts from Koray Gubur's writings.
These co-occur frequently across his documents, suggesting they form a coherent framework.

Central concepts: {', '.join(centrality[:10])}

Full entity list in this cluster:
{chr(10).join(f'- {e}' for e in sample)}

Task:
1. Give this cluster a FRAMEWORK NAME — what overarching framework or methodology 
   does this cluster represent? Use Koray's own terminology when possible.
2. Write a 2-3 sentence DEFINITION of this framework.
3. Identify the CORE CONCEPTS (the 3-5 most important entities that define it).
4. Identify the METHODS (any step-by-step procedures or techniques visible).
5. Rate CONFIDENCE: "high" (clearly a named framework), "medium" (coherent cluster), 
   or "low" (loose collection of ideas).

Return ONLY a JSON object:
{{"name": "...", "definition": "...", "core_concepts": [...], "methods": [...], "confidence": "..."}}"""

    result = call_ollama(
        "You are a knowledge graph analyst naming SEO framework clusters. Return ONLY valid JSON.",
        prompt,
        max_tokens=1000,
    )
    
    # Parse
    try:
        import re
        # Try direct
        try:
            return json.loads(result.strip())
        except:
            pass
        # Try markdown fence
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', result, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try JSON object
        match = re.search(r'\{[\s\S]*\}', result)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    
    return {"name": "Unnamed Cluster", "definition": "", "core_concepts": centrality[:5], "methods": [], "confidence": "low"}


def main():
    print("═══ Phase 2: Community Detection ═══\n")
    
    # Load clean graph
    print("Loading Phase 1 graph...")
    with open(INPUT_PATH) as f:
        graph_data = json.load(f)
    
    entities = graph_data["entities"]
    edges = graph_data["edges"]
    print(f"  Entities: {len(entities)}")
    print(f"  Edges: {len(edges)}")
    
    # Build NetworkX graph
    print("\nBuilding NetworkX graph...")
    G = nx.Graph()
    
    # Add nodes with attributes
    for name, stats in entities.items():
        G.add_node(name, **stats)
    
    # Add weighted edges
    for edge in edges:
        G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
    
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    
    # Community detection
    print("\nRunning Louvain community detection...")
    # Convert to undirected weighted for Louvain
    communities = louvain_communities(G, weight="weight", seed=42)
    communities = list(communities)
    print(f"  Communities found: {len(communities)}")
    
    # Assign community IDs
    community_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            community_map[node] = i
    
    # Analyze each community
    print("\nAnalyzing communities...")
    community_analysis = []
    
    for comm_id, comm_nodes in enumerate(communities):
        # Subgraph for centrality
        sub = G.subgraph(comm_nodes)
        
        # Betweenness centrality
        try:
            bc = nx.betweenness_centrality(sub, weight="weight")
        except:
            bc = {n: 0 for n in comm_nodes}
        
        # Sort by centrality
        ranked = sorted(bc.items(), key=lambda x: x[1], reverse=True)
        central_entities = [n for n, _ in ranked[:15]]
        
        # Entity types in community
        types = Counter(G.nodes[n].get("type", "concept") for n in comm_nodes)
        
        # Total mentions and docs
        total_mentions = sum(G.nodes[n].get("mention_count", 0) for n in comm_nodes)
        
        # Internal edge density
        internal_edges = sum(1 for e in edges if e["source"] in comm_nodes and e["target"] in comm_nodes)
        density = internal_edges / (len(comm_nodes) * (len(comm_nodes) - 1) / 2) if len(comm_nodes) > 1 else 0
        
        analysis = {
            "community_id": comm_id,
            "size": len(comm_nodes),
            "type_distribution": dict(types),
            "total_mentions": total_mentions,
            "internal_edges": internal_edges,
            "density": round(density, 4),
            "central_entities": central_entities,
            "all_entities": sorted(comm_nodes),
        }
        community_analysis.append(analysis)
    
    # Sort by size
    community_analysis.sort(key=lambda x: x["size"], reverse=True)
    
    # Print summary
    print(f"\n{'ID':>3} {'Size':>5} {'Edges':>6} {'Density':>8} {'Types'}")
    print(f"{'─'*3} {'─'*5} {'─'*6} {'─'*8} {'─'*40}")
    for a in community_analysis:
        types_str = ", ".join(f"{t}:{c}" for t, c in Counter(a["type_distribution"]).most_common(4))
        print(f"{a['community_id']:3d} {a['size']:5d} {a['internal_edges']:6d} {a['density']:8.4f} {types_str}")
    
    # LLM naming for top communities (size >= 5)
    print("\n════ LLM Naming ════")
    named_communities = []
    
    for analysis in community_analysis:
        if analysis["size"] < 5:
            # Too small, just use central entity as name
            analysis["framework"] = {
                "name": analysis["central_entities"][0] if analysis["central_entities"] else "Unknown",
                "definition": f"Small cluster of {analysis['size']} related concepts",
                "core_concepts": analysis["central_entities"][:5],
                "methods": [],
                "confidence": "low",
            }
            named_communities.append(analysis)
            continue
        
        print(f"\n  Naming community {analysis['community_id']} ({analysis['size']} entities)...")
        
        framework = name_community(
            analysis["all_entities"],
            analysis["central_entities"],
        )
        
        analysis["framework"] = framework
        named_communities.append(analysis)
        
        print(f"    → {framework.get('name', '?')} ({framework.get('confidence', '?')})")
        time.sleep(1)  # Rate limit
    
    # Output
    output = {
        "metadata": {
            "phase": 2,
            "operation": "community_detection",
            "date": datetime.now().isoformat(),
            "algorithm": "louvain",
            "communities_found": len(communities),
            "named_communities": len(named_communities),
        },
        "communities": named_communities,
        "graph_stats": {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "density": round(nx.density(G), 4),
        },
    }
    
    outpath = f"{OUTDIR}/phase2_communities.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Phase 2 complete → {outpath}")
    print(f"   Communities: {len(named_communities)}")
    print(f"   Named frameworks: {sum(1 for c in named_communities if c['size'] >= 5)}")


if __name__ == "__main__":
    main()
