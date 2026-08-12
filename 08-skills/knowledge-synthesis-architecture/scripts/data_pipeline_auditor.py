#!/usr/bin/env python3
"""
Deterministic Knowledge Graph Auditor — Phase 6 Prep Pipeline
=============================================================
Runs a FIXED query matrix against a LightRAG instance,
extracts structural patterns from KG responses,
computes the Semantic Delta against the 534-card flashcard baseline,
and outputs deterministic patch files.

USAGE:
  python3 data_pipeline_auditor.py \\
    --target http://localhost:8014 \\
    --baseline /path/to/phase4_flashcards.json \\
    --out-dir /path/to/output/

  python3 data_pipeline_auditor.py --dry-run

Same queries every run → same results. No ad-hoc prompting.
This is the ONLY way to query KGs for cross-reference — never
run manual curl queries against LightRAG for pipeline work.
"""

import argparse, json, os, sys, time, re, hashlib, itertools
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

# ══════════════════════════════════════════════════════════════
# FIXED QUERY MATRIX — immutable, 10 queries, never changed
# ══════════════════════════════════════════════════════════════

QUERY_MATRIX = [
    {
        "id": "Q1-workflow",
        "query": "What is the complete step-by-step workflow for building topical authority? From defining the central entity to publishing content. Every single step in order.",
        "mode": "hybrid",
        "category": "workflow",
        "target": "numbered_steps"
    },
    {
        "id": "Q2-quarice-vector",
        "query": "What is the contextual vector in the Quarice Framework? How do you construct contextual vectors for an article? What is the relationship between contextual vector and question generation?",
        "mode": "hybrid",
        "category": "quarice",
        "target": "contextual_vector"
    },
    {
        "id": "Q3-quarice-structure",
        "query": "What is contextual hierarchy and contextual structure in the Quarice Framework? How do you decide the heading order and semantic layers of an article?",
        "mode": "hybrid",
        "category": "quarice",
        "target": "contextual_hierarchy"
    },
    {
        "id": "Q4-quarice-connection",
        "query": "What are contextual connections and contextual bridges in the Quarice Framework? How do you link between articles? What are contextual borders and how do they work?",
        "mode": "hybrid",
        "category": "quarice",
        "target": "contextual_connection"
    },
    {
        "id": "Q5-content-brief",
        "query": "What is the complete content brief template? Every section, every component that goes into a semantic content brief. How is it different for root seeds vs nodes?",
        "mode": "hybrid",
        "category": "content_brief",
        "target": "template_structure"
    },
    {
        "id": "Q6-topical-map",
        "query": "What is the complete topical map creation process? From source context to central search intent to core/outdoor partition to title tags to URL structure. Every step with its purpose.",
        "mode": "hybrid",
        "category": "topical_map",
        "target": "map_process"
    },
    {
        "id": "Q7-linguistics",
        "query": "What is the data-driven linguistics methodology? Text graphs, n-grams, distributional semantics, seconds modeling, query processing. How do you apply corpus linguistics to SEO?",
        "mode": "hybrid",
        "category": "linguistics",
        "target": "corpus_methods"
    },
    {
        "id": "Q8-content-network",
        "query": "What is the semantic content network? The root/seed/node architecture, PageRank distribution, information trees, crawl paths. How do you structure a website for topical authority?",
        "mode": "hybrid",
        "category": "content_network",
        "target": "network_architecture"
    },
    {
        "id": "Q9-frameworks",
        "query": "What are ALL the frameworks, methods, techniques, processes, and models that Koray teaches? List every named framework with a one-sentence description of what it covers.",
        "mode": "hybrid",
        "category": "frameworks",
        "target": "framework_inventory"
    },
    {
        "id": "Q10-action-directives",
        "query": "What are the specific action directives for each phase of the SEO workflow? What must you DO at each step? What are the non-negotiable rules? What are the common mistakes?",
        "mode": "hybrid",
        "category": "directives",
        "target": "action_rules"
    },
]


def query_lightrag(target, query, mode="hybrid", timeout=240):
    """Run a single query against a LightRAG instance."""
    payload = json.dumps({"query": query, "mode": mode}).encode("utf-8")
    req = Request(
        f"{target}/query",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", "") or data.get("response", "")
    except Exception as e:
        return f"[ERROR: {e}]"


def extract_structural_patterns(response, category):
    """Extract structural patterns from KG response using regex/key-based methods ONLY.
    NO LLM interpretation. Deterministic extraction only."""
    
    results = {
        "frameworks": [],
        "methods": [],
        "steps": [],
        "directives": [],
        "raw_length": len(response),
    }
    
    # Extract numbered steps (Q1: workflow)
    step_pattern = re.findall(
        r"(?:Step|Phase|Layer)\s*(\d+)[\s:.\-—]+(.+?)(?=(?:Step|Phase|Layer)\s*\d+|$)",
        response, re.IGNORECASE
    )
    if step_pattern:
        results["steps"] = [
            {"number": int(n), "text": t.strip()[:300]}
            for n, t in step_pattern
        ]
    
    # Extract named frameworks
    framework_pattern = re.findall(
        r"(?:Framework|Model|Method|System|Protocol|Architecture):\s*[\"']?([^\"'\n,;]{5,80})[\"']?",
        response
    )
    if framework_pattern:
        results["frameworks"] = list(dict.fromkeys(f.strip() for f in framework_pattern))
    
    # Extract action directives (MUST/SHOULD/NEVER/ALWAYS/DO NOT)
    directive_pattern = re.findall(
        r"(\b(?:MUST|SHOULD|NEVER|ALWAYS|DO NOT|DON'T|YOU MUST|YOU SHOULD|CRITICAL|ESSENTIAL|NON.NEGOTIABLE|RULE|PRINCIPLE)\b[\s:]+)(.+?)(?=(?:\b(?:MUST|SHOULD|NEVER|ALWAYS|DO NOT|DON'T|YOU MUST|YOU SHOULD|CRITICAL|ESSENTIAL)\b|$))",
        response, re.IGNORECASE
    )
    if directive_pattern:
        results["directives"] = [
            {"type": d[0].strip(), "directive": d[1].strip()[:200]}
            for d in directive_pattern
        ]
    
    return results


def load_baseline(baseline_path):
    """Load the 534-card flashcard baseline."""
    with open(baseline_path) as f:
        data = json.load(f)
    cards = data.get("cards", [])
    print(f"  [BASELINE] Loaded {len(cards)} cards from Phase 4 flashcards")
    return cards


def compute_semantic_delta(extracted_raw, baseline_cards):
    """Compute the Semantic Delta: what's new vs. what overlaps."""
    
    def tokenize(text):
        return set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    
    # Build baseline token sets
    baseline_sets = []
    for card in baseline_cards:
        content = card.get("content", "") or card.get("claim", "") or card.get("title", "")
        if not content:
            continue
        baseline_sets.append({
            "card": card,
            "tokens": tokenize(content),
        })
    
    # For each extracted framework/method, compute Jaccard overlap
    new_frameworks = []
    new_methods = []
    enhanced_rules = []
    
    for fw in extracted_raw.get("frameworks", []):
        fw_tokens = tokenize(fw)
        best_score = 0
        for bs in baseline_sets:
            if not fw_tokens or not bs["tokens"]:
                continue
            overlap = len(fw_tokens & bs["tokens"])
            union = len(fw_tokens | bs["tokens"])
            score = overlap / union if union > 0 else 0
            best_score = max(best_score, score)
        
        if best_score < 0.1:
            new_frameworks.append({"framework": fw, "overlap": best_score})
        elif best_score < 0.4:
            enhanced_rules.append({"framework": fw, "overlap": best_score})
    
    print(f"  New frameworks: {len(new_frameworks)}")
    print(f"  New methods: {len(new_methods)}")
    print(f"  Enhanced rules: {len(enhanced_rules)}")
    
    return {
        "new_frameworks": new_frameworks,
        "new_methods": new_methods,
        "enhanced_rules": enhanced_rules,
    }


def generate_patches(delta, extracted, out_dir):
    """Generate the patch markdown file."""
    
    lines = [
        "# Transcript Lecture Patches — Phase 1-5 Enrichment",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Source:** {len(QUERY_MATRIX)} deterministic queries against transcript KG",
        "",
        "## Semantic Delta Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| New Frameworks | {len(delta['new_frameworks'])} |",
        f"| New Methods | {len(delta['new_methods'])} |",
        f"| Enhanced Rules | {len(delta['enhanced_rules'])} |",
        "",
    ]
    
    if delta["new_frameworks"]:
        lines.append("## New Frameworks (Jaccard < 0.1)")
        lines.append("")
        for fw in delta["new_frameworks"]:
            lines.append(f"- **{fw['framework']}** (overlap: {fw['overlap']:.2f})")
        lines.append("")
    
    if delta["enhanced_rules"]:
        lines.append("## Enhanced Rules (Jaccard 0.1-0.4)")
        lines.append("")
        for rule in delta["enhanced_rules"]:
            lines.append(f"- **{rule['framework']}** (overlap: {rule['overlap']:.2f})")
        lines.append("")
    
    lines.append("## Query Execution Log")
    lines.append("")
    lines.append("| Query ID | Response Length | Steps | Frameworks | Directives |")
    lines.append("|---|---|---|---|---|")
    for qr in QUERY_MATRIX:
        ex = extracted.get(qr["id"], {})
        lines.append(
            f"| {qr['id']} | {ex.get('raw_length', 0):,} chars | "
            f"{len(ex.get('steps', []))} | {len(ex.get('frameworks', []))} | "
            f"{len(ex.get('directives', []))} |"
        )
    lines.append("")
    
    # Save patches
    patch_path = os.path.join(out_dir, "phase1-5-lecture-patches.md")
    joined = "\n".join(lines)
    with open(patch_path, "w") as f:
        f.write(joined)
    print(f"  [OUTPUT] Wrote {patch_path} ({len(joined)} bytes)")
    
    # Save raw data
    raw_path = os.path.join(out_dir, "transcript-raw-data.json")
    with open(raw_path, "w") as f:
        json.dump(extracted, f, indent=2, default=str)
    print(f"  [OUTPUT] Wrote {raw_path}")


def update_blueprint(out_dir):
    """Update master-operating-blueprint.json with audit metadata."""
    bp_path = os.path.join(out_dir, "..", "master-operating-blueprint.json")
    # Navigate from 07-content-briefs to root
    bp_path = os.path.abspath(os.path.join(out_dir, "..", "master-operating-blueprint.json"))
    
    if not os.path.exists(bp_path):
        print(f"  [WARN] Blueprint not found at {bp_path}")
        return
    
    with open(bp_path) as f:
        bp = json.load(f)
    
    # Update semantic delta timestamp
    if "data_sources" in bp and "koray_transcripts" in bp["data_sources"]:
        bp["data_sources"]["koray_transcripts"]["semantic_delta"]["generated"] = \
            datetime.now(timezone.utc).isoformat()
    
    with open(bp_path, "w") as f:
        json.dump(bp, f, indent=2)
    
    print(f"  [OUTPUT] Updated {bp_path}")


def main():
    parser = argparse.ArgumentParser(description="Deterministic KG Auditor")
    parser.add_argument("--target", default="http://localhost:8014", help="LightRAG instance URL")
    parser.add_argument("--baseline", required=False, help="Flashcard baseline path")
    parser.add_argument("--out-dir", required=False, help="Output directory for patches")
    parser.add_argument("--dry-run", action="store_true", help="Print query matrix and exit")
    parser.add_argument("--mode", default="full", choices=["full", "query-only", "extract-only"],
                       help="Pipeline mode: full (default), query-only, or extract-only")
    args = parser.parse_args()
    
    if args.dry_run:
        print(f"=== DRY RUN: {len(QUERY_MATRIX)} fixed queries ===")
        for q in QUERY_MATRIX:
            print(f"  [{q['id']}] ({q['mode']}) {q['query'][:80]}...")
        print(f"\nNo changes made.")
        return
    
    target = args.target
    baseline_path = args.baseline
    out_dir = args.out_dir
    
    assert target, "Missing --target"
    assert baseline_path, "Missing --baseline"
    assert out_dir, "Missing --out-dir"
    
    os.makedirs(out_dir, exist_ok=True)
    
    # [1] Load baseline
    print("[1/5] Loading baseline...")
    baseline_cards = load_baseline(baseline_path)
    
    # [2] Run query matrix
    print(f"[2/5] Running fixed query matrix against {target}...")
    extracted = {}
    for i, q in enumerate(QUERY_MATRIX, 1):
        t0 = time.time()
        response = query_lightrag(target, q["query"], q["mode"])
        elapsed = time.time() - t0
        
        patterns = extract_structural_patterns(response, q["category"])
        extracted[q["id"]] = patterns
        
        s = len(patterns["steps"])
        f = len(patterns["frameworks"])
        d = len(patterns["directives"])
        print(f"  [{i}/{len(QUERY_MATRIX)}] {q['id']}... {elapsed:.1f}s, {s} steps, {f} frameworks, {d} directives")
    
    if args.mode == "query-only":
        for qid, data in extracted.items():
            print(f"\n{qid}: {json.dumps(data, indent=2)[:500]}")
        return
    
    # [3] Compute delta
    print("[3/5] Computing Semantic Delta...")
    delta = compute_semantic_delta(extracted, baseline_cards)
    
    # [4] Generate patches
    print("[4/5] Generating patch files...")
    generate_patches(delta, extracted, out_dir)
    
    # [5] Update blueprint
    print("[5/5] Updating master-operating-blueprint.json...")
    update_blueprint(out_dir)
    
    print("\n=== PIPELINE COMPLETE ===")
    print(f"Patches: {os.path.join(out_dir, 'phase1-5-lecture-patches.md')}")
    print(f"Raw data: {os.path.join(out_dir, 'transcript-raw-data.json')}")
    print(f"Updated: master-operating-blueprint.json")


if __name__ == "__main__":
    main()
