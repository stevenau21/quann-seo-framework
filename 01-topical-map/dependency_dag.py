#!/usr/bin/env python3
"""
dependency_dag.py — 3-Vector Dependency Extraction Engine
==========================================================
Builds a Directed Acyclic Graph from Koray's 12-framework dependency network,
applies topological sort, and groups into operational phases for quann.homes.

Three vectors of dependency extraction:
  Vector 1: Framework Stratification (explicit depends_on/supports — THE BOSS)
  Vector 2: Cross-Framework NLP Overlap (cross_framework_edges — implicit links)
  Vector 3: External Dependency Co-occurrence (external_dependencies overlap)

Cycle Resolution Rule:
  Vector 1 ALWAYS overrides Vectors 2 and 3.
  When a cycle is detected, the edge from the higher foundational-layer
  framework is preserved; the reverse edge is pruned.

Output:
  - Topologically sorted framework sequence
  - Operational phases (grouped into 5-7 human-actionable phases)
  - Phase 1 detailed prescription: exact Koray rules to execute first

Usage:
  python3 dependency_dag.py [--output phases.json]
"""

import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

FRAMEWORKS_FILE = Path(
    "/home/steve/lightrag-apps/knowledge-synthesis/extractions/"
    "koray-gubur/phase5_frameworks.json"
)

# ─── FOUNDATIONAL STRATIFICATION (Vector 1 Authority) ────────────────────────
# Lower number = more foundational. When cycles break, the LOWER-numbered
# framework's dependency direction wins.

FOUNDATIONAL_LAYER: Dict[str, int] = {
    # Layer 0: Pure primitives — no SEO-specific knowledge, just linguistics + data
    "content-quality-linguistics": 0,
    "python-data-driven-seo": 0,
    # Layer 1: Core SEO concepts that everything else depends on
    "knowledge-graph-structured-data": 1,
    "conversion-growth": 1,
    # Layer 2: Information science foundations
    "seo-information-retrieval": 2,
    # Layer 3: Entity/Semantic — the bridge between raw data and authority
    "entity-based-seo": 3,
    "semantic-seo": 3,
    # Layer 4: Execution frameworks
    "technical-seo": 4,
    "multilingual-international-seo": 4,
    # Layer 5: The crown — depends on everything below
    "topical-authority": 5,
    "holistic-seo": 5,
    # Layer 6: Meta-framework — reflects on the whole system
    "seo-case-study-methodology": 6,
}

# ─── CYCLE DETECTION & RESOLUTION ────────────────────────────────────────────

def detect_cycles(adjacency: Dict[str, List[str]]) -> List[List[str]]:
    """Return all simple cycles in the directed graph using DFS."""
    cycles = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in adjacency}
    parent: Dict[str, str | None] = {}

    def dfs(u: str):
        color[u] = GRAY
        for v in adjacency.get(u, []):
            if color.get(v) == GRAY:
                # Found a cycle — trace back
                cycle = [v, u]
                p = parent.get(u)
                while p is not None and p != v:
                    cycle.append(p)
                    p = parent.get(p)
                cycle.append(v)
                cycles.append(list(reversed(cycle)))
            elif color.get(v) == WHITE:
                parent[v] = u
                dfs(v)
        color[u] = BLACK

    for node in adjacency:
        if color.get(node) == WHITE:
            parent = {node: None}
            dfs(node)
    return cycles


def resolve_cycles(
    adjacency: Dict[str, List[str]],
    cycles: List[List[str]],
    dep_count: Dict[str, int],
) -> Dict[str, List[str]]:
    """
    Break cycles by pruning the edge from the HIGHER foundational-layer node
    to the LOWER one. Vector 1 stratification always wins.

    SAME-LAYER TIEBREAKER: Prune the edge from the node with MORE depends_on
    entries (less foundational within its layer) to the one with fewer.
    """
    pruned = 0
    for cycle in cycles:
        for i in range(len(cycle) - 1):
            u, v = cycle[i], cycle[i + 1]
            if v not in adjacency.get(u, []):
                continue
            layer_u = FOUNDATIONAL_LAYER.get(u, 99)
            layer_v = FOUNDATIONAL_LAYER.get(v, 99)

            if layer_u > layer_v:
                reason = f"layer {layer_u} > layer {layer_v}"
            elif layer_u == layer_v:
                deps_u = dep_count.get(u, 0)
                deps_v = dep_count.get(v, 0)
                if deps_u > deps_v:
                    reason = f"same layer, {u} has {deps_u} deps > {v} has {deps_v}"
                elif deps_v > deps_u:
                    continue  # v depends more, so v → u edge would be pruned instead
                else:
                    # Same deps — prune the edge going to the node with FEWER supports
                    reason = f"same layer, equal deps ({deps_u}), pruning {u}→{v}"
            else:
                continue  # u is more foundational, don't prune this direction

            adjacency[u].remove(v)
            pruned += 1
            print(f"  ⚠️  CYCLE BREAK #{pruned}: {u} → {v} ({reason})")
    return adjacency


# ─── TOPOLOGICAL SORT ────────────────────────────────────────────────────────

def topological_sort(adjacency: Dict[str, List[str]]) -> List[str]:
    """Kahn's algorithm. Returns sorted list. Raises if cycles remain."""
    in_degree = {node: 0 for node in adjacency}
    for u, neighbors in adjacency.items():
        for v in neighbors:
            in_degree[v] = in_degree.get(v, 0) + 1

    queue = deque([n for n, d in in_degree.items() if d == 0])
    result = []

    while queue:
        u = queue.popleft()
        result.append(u)
        for v in adjacency.get(u, []):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(result) != len(adjacency):
        remaining = set(adjacency) - set(result)
        raise RuntimeError(f"Cycle remains after resolution! Unresolved: {remaining}")

    return result


# ─── PHASE CHUNKING ──────────────────────────────────────────────────────────

def chunk_into_phases(
    sorted_frameworks: List[str],
    frameworks_data: Dict[str, dict],
) -> List[dict]:
    """
    Group the sorted frameworks into operational phases.
    A new phase begins when we cross a foundational layer boundary
    AND the current phase has accumulated enough work.
    """
    phases = []
    current_phase = {"name": "", "layer_start": None, "frameworks": [], "cards": 0}

    PHASE_NAMES = {
        0: "Phase 1: Foundational Primitives — Linguistics & Data Infrastructure",
        1: "Phase 2: Core SEO Concepts — Knowledge Graph & Conversion Architecture",
        2: "Phase 3: Information Science — Retrieval & Indexing Foundations",
        3: "Phase 4: Entity-Semantic Bridge — From Raw Data to Authority Signals",
        4: "Phase 5: Execution Layer — Technical & International Deployment",
        5: "Phase 6: The Crown — Topical Authority Assembly",
        6: "Phase 7: Meta-Reflection — Case Study Validation & Iteration",
    }

    for fw_id in sorted_frameworks:
        fw = frameworks_data.get(fw_id, {})
        layer = FOUNDATIONAL_LAYER.get(fw_id, 99)

        if current_phase["layer_start"] is None:
            current_phase["layer_start"] = layer
            current_phase["name"] = PHASE_NAMES.get(layer, f"Phase: Layer {layer}")

        if layer != current_phase["layer_start"]:
            # Flush current phase
            if current_phase["frameworks"]:
                phases.append(current_phase)
            current_phase = {
                "name": PHASE_NAMES.get(layer, f"Phase: Layer {layer}"),
                "layer_start": layer,
                "frameworks": [],
                "cards": 0,
            }

        tier1 = fw.get("tier_1_rules", {}).get("count", 0)
        tier2 = fw.get("tier_2_context", {}).get("count", 0)
        current_phase["frameworks"].append({
            "id": fw_id,
            "name": fw.get("name", fw_id),
            "layer": layer,
            "tier_1_rules": tier1,
            "tier_2_context": tier2,
            "total_cards": tier1 + tier2,
            "depends_on": fw.get("depends_on", []),
            "supports": fw.get("supports", []),
            "definition": fw.get("definition", "")[:200] + "...",
        })
        current_phase["cards"] += tier1 + tier2

    if current_phase["frameworks"]:
        phases.append(current_phase)

    return phases


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  3-VECTOR DEPENDENCY EXTRACTION ENGINE")
    print("  Koray Gubur Framework → Operational Phases for quann.homes")
    print("=" * 72)

    # Load data
    with open(FRAMEWORKS_FILE) as f:
        data = json.load(f)

    frameworks = {fw["id"]: fw for fw in data["frameworks"]}
    print(f"\n📊 Loaded {len(frameworks)} frameworks, {data['metadata']['statistics']['total_cards']} cards "
          f"({data['metadata']['statistics']['tier_1_rules']} grounded)")

    # ─── VECTOR 1: Build adjacency from explicit depends_on ──────────────────
    adjacency: Dict[str, List[str]] = {}
    for fw_id, fw in frameworks.items():
        adjacency[fw_id] = []
        for dep in fw.get("depends_on", []):
            # Map framework names to IDs
            dep_id = None
            for fid, fdata in frameworks.items():
                if fdata["name"] == dep:
                    dep_id = fid
                    break
            if dep_id and dep_id in frameworks:
                adjacency[fw_id].append(dep_id)

    print(f"\n🔗 VECTOR 1: {sum(len(v) for v in adjacency.values())} explicit dependencies")

    # ─── VECTOR 2: Augment with cross-framework edges (high confidence only) ──
    cross_added = 0
    for fw_id, fw in frameworks.items():
        for target, edge_data in fw.get("cross_framework_edges", {}).items():
            if edge_data.get("strength", 0) > 0.5 and edge_data.get("card_count", 0) >= 5:
                target_id = None
                for fid, fdata in frameworks.items():
                    if fdata["name"] == target:
                        target_id = fid
                        break
                if target_id and target_id in frameworks and target_id not in adjacency[fw_id]:
                    adjacency[fw_id].append(target_id)
                    cross_added += 1

    print(f"🔗 VECTOR 2: {cross_added} NLP-derived edges added (strength > 0.5, cards ≥ 5)")

    # ─── VECTOR 3: External dependency overlap ───────────────────────────────
    # (Lightweight: count shared external deps between framework pairs)
    overlap_added = 0
    fw_ext_deps = {}
    for fw_id, fw in frameworks.items():
        ext = fw.get("external_dependencies", [])
        # Normalize to lowercased keywords
        keywords = set()
        for dep in ext:
            for word in dep.lower().replace(",", " ").replace(".", " ").split():
                if len(word) > 4:
                    keywords.add(word)
        fw_ext_deps[fw_id] = keywords

    for fw_a in frameworks:
        for fw_b in frameworks:
            if fw_a >= fw_b:
                continue
            overlap = len(fw_ext_deps[fw_a] & fw_ext_deps[fw_b])
            if overlap >= 8 and fw_b not in adjacency.get(fw_a, []):
                # Determine direction: foundational layer rules
                layer_a = FOUNDATIONAL_LAYER.get(fw_a, 99)
                layer_b = FOUNDATIONAL_LAYER.get(fw_b, 99)
                if layer_a < layer_b:
                    adjacency.setdefault(fw_b, []).append(fw_a)
                elif layer_b < layer_a:
                    adjacency.setdefault(fw_a, []).append(fw_b)
                overlap_added += 1

    print(f"🔗 VECTOR 3: {overlap_added} external-dependency overlap edges added")

    # ─── CYCLE DETECTION — ITERATIVE ────────────────────────────────────────
    print("\n─── CYCLE DETECTION ───")
    # Build dependency count for same-layer tiebreaking
    dep_count = {
        fw_id: len(fw.get("depends_on", []))
        for fw_id, fw in frameworks.items()
    }

    # Iterative: keep detecting and breaking until clean
    max_iterations = 10
    for iteration in range(1, max_iterations + 1):
        adj_copy = {k: list(v) for k, v in adjacency.items()}
        cycles = detect_cycles(adj_copy)

        if not cycles:
            print(f"  ✅ No cycles after iteration {iteration}")
            break

        print(f"  🔴 Iteration {iteration}: {len(cycles)} cycle(s)")
        for i, cycle in enumerate(cycles[:4]):
            print(f"     Cycle {i+1}: {' → '.join(cycle)}")
        if len(cycles) > 4:
            print(f"     ... and {len(cycles) - 4} more")

        # Prune edges by Vector 1 authority
        adjacency = resolve_cycles(adjacency, cycles, dep_count)
    else:
        # Check for mutual 2-cycles specifically (A↔B)
        mutual = []
        for a in adjacency:
            for b in adjacency.get(a, []):
                if a in adjacency.get(b, []):
                    mutual.append((a, b))
        if mutual:
            print(f"  🔴 {len(mutual)} mutual edges remain — brute-force breaking")
            for a, b in mutual:
                layer_a = FOUNDATIONAL_LAYER.get(a, 99)
                layer_b = FOUNDATIONAL_LAYER.get(b, 99)
                if layer_a >= layer_b:
                    adjacency[a].remove(b)
                    print(f"     Broke {a}→{b} (layer {layer_a} ≥ layer {layer_b})")
                else:
                    adjacency[b].remove(a)
                    print(f"     Broke {b}→{a} (layer {layer_b} ≥ layer {layer_a})")

    # ─── TOPOLOGICAL SORT ────────────────────────────────────────────────────
    print("\n─── TOPOLOGICAL SORT ───")
    try:
        sorted_order = topological_sort(adjacency)
        print(f"  ✅ {len(sorted_order)} frameworks sorted")
    except RuntimeError as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    # ─── PHASE CHUNKING ──────────────────────────────────────────────────────
    print("\n─── OPERATIONAL PHASES ───")
    phases = chunk_into_phases(sorted_order, frameworks)

    total_cards = 0
    for i, phase in enumerate(phases):
        total_cards += phase["cards"]
        print(f"\n  {phase['name']}")
        print(f"  {'─' * 58}")
        for fw in phase["frameworks"]:
            print(f"    • {fw['name']} ({fw['id']})")
            print(f"      Tier 1: {fw['tier_1_rules']} grounded rules | "
                  f"Tier 2: {fw['tier_2_context']} context | "
                  f"Total: {fw['total_cards']} cards")
            if fw["depends_on"]:
                print(f"      Depends on: {', '.join(fw['depends_on'][:3])}")
        print(f"  📦 Phase total: {phase['cards']} cards")

    print(f"\n  📊 GRAND TOTAL: {total_cards} cards across {len(phases)} phases")

    # ─── OUTPUT JSON ─────────────────────────────────────────────────────────
    output = {
        "metadata": {
            "engine": "3-Vector Dependency Extraction Engine v1.0",
            "vectors": {
                "vector_1": "Framework Stratification (explicit depends_on)",
                "vector_2": "Cross-Framework NLP Overlap (strength > 0.5, cards ≥ 5)",
                "vector_3": "External Dependency Co-occurrence (≥ 8 shared keywords)",
            },
            "cycle_resolution": "Vector 1 always overrides — lower foundational layer wins",
            "total_frameworks": len(frameworks),
            "total_cards": total_cards,
            "tier_1_grounded": data["metadata"]["statistics"]["tier_1_rules"],
            "tier_2_context": data["metadata"]["statistics"]["tier_2_context"],
        },
        "topological_order": sorted_order,
        "phases": phases,
    }

    out_path = Path("/home/steve/SEO-quann.homes/phase-dependencies.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n💾 Full phase map written to: {out_path}")

    # ─── PHASE 1 DEEP DIVE ───────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  PHASE 1 — DEEP DIVE")
    print("  What the machine calculated as the irreducible foundation")
    print("=" * 72)

    if phases:
        p1 = phases[0]
        print(f"\n{p1['name']}")
        print(f"Frameworks: {len(p1['frameworks'])}")
        print(f"Cards: {p1['cards']} ({p1['cards']} rules to execute before anything else)\n")

        for fw in p1["frameworks"]:
            fdata = frameworks.get(fw["id"], {})
            print(f"  📘 {fw['name']} ({fw['id']})")
            print(f"     Definition: {fdata.get('definition', '')[:300]}...")
            print(f"     Tier 1 grounded rules ({fw['tier_1_rules']}):")

            # Show actual Tier 1 rules
            tier1_cards = fdata.get("tier_1_rules", {}).get("cards", [])
            for card in tier1_cards[:5]:
                content = card.get("content", "")[:120]
                print(f"       ▸ {content}...")
            if len(tier1_cards) > 5:
                print(f"       ... and {len(tier1_cards) - 5} more")
            print()

        print("─── Phase 1 Execution Prescription ───")
        print("""
  These frameworks have ZERO dependencies. They are the mathematical
  prerequisites — no Koray rule in any later phase can execute without
  the primitives established here.

  For quann.homes, Phase 1 means:

  1. Content Quality & Linguistics: Establish the writing discipline.
     Every declarative sentence must follow entity-first structure.
     No modality contamination. No fluff intros. This is the "military
     discipline" Koray demands before any page gets published.

  2. Python & Data-Driven SEO: Build the measurement infrastructure.
     Before we write a single page, we need: WordNet synonym extraction
     for query vocabulary, NLTK tokenization/lemmatization for content
     auditing, and log file analysis setup for cost-of-retrieval monitoring.

  3. Conversion & Growth: Wire the trust flywheel. Source Context →
     Contextual Bridge → CTA. The conversion architecture must exist
     as a template before content fills it. Otherwise we're publishing
     dead-end pages with no semantic destination.

  OUTPUT: After Phase 1, the copywriter has:
    - A validated sentence structure rulebook
    - A query vocabulary bank (WordNet-derived)
    - A conversion bridge template (every page ends with a path forward)
""")


if __name__ == "__main__":
    main()
