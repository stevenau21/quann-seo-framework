#!/usr/bin/env python3
"""
Phase 3.1 — Doc ID Reconstruction
===================================
The Phase 3 pipeline discovered framework-relevant documents via keyword scoring
but only stored the COUNT (docs_analyzed), not the actual doc_ids.

This script deterministically re-runs the same find_relevant_docs() function
from phase3_direct.py and injects the actual doc_ids into each framework's metadata.

No LLM calls — purely deterministic keyword scoring.
"""

import json
import sys
import importlib.util
from pathlib import Path

WORKSPACE = "/home/steve/lightrag-apps/koray-gubur/workspace"
OUTDIR = Path("/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur")
PHASE3_OUT = OUTDIR / "phase3_extractions_v4_deepseek.json"
PHASE3_BACKUP = OUTDIR / "phase3_extractions_v4_deepseek.backup.json"

# Import the find_relevant_docs function from phase3_direct.py
spec = importlib.util.spec_from_file_location(
    "phase3",
    str(OUTDIR / "phase3_direct.py")
)
phase3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase3)

FRAMEWORK_QUERIES = phase3.FRAMEWORK_QUERIES

def main():
    # Load existing Phase 3 output
    print("Loading Phase 3 data...")
    with open(PHASE3_OUT) as f:
        data = json.load(f)

    extractions = data["extractions"]

    # Load raw data for scoring
    print("Loading KV store data...")
    with open(f"{WORKSPACE}/kv_store_full_docs.json") as f:
        docs_data = json.load(f)
    with open(f"{WORKSPACE}/kv_store_full_entities.json") as f:
        entities_data = json.load(f)

    print(f"  {len(docs_data)} documents, {len(entities_data)} entity sets")

    # Backup
    import shutil
    shutil.copy(PHASE3_OUT, PHASE3_BACKUP)
    print(f"  Backed up to {PHASE3_BACKUP}")

    # For each framework, re-run scoring and inject doc_ids
    updated = 0
    for fw_name, fw_data in extractions.items():
        if not isinstance(fw_data, dict):
            continue

        keywords = FRAMEWORK_QUERIES.get(fw_name)
        if not keywords:
            print(f"  ⚠ {fw_name}: no keywords in FRAMEWORK_QUERIES, skipping")
            continue

        relevant_docs = phase3.find_relevant_docs(keywords, entities_data, docs_data)

        # Filter out docs with <200 chars (same logic as original script)
        filtered_docs = []
        for doc_id in relevant_docs:
            content = docs_data.get(doc_id, {}).get("content", "")
            if isinstance(content, str) and len(content) >= 200:
                filtered_docs.append(doc_id)

        existing_count = fw_data.get("_metadata", {}).get("docs_analyzed", 0)
        meta = fw_data.setdefault("_metadata", {})
        meta["doc_ids"] = filtered_docs
        meta["doc_count_corrected"] = len(filtered_docs)

        print(f"  ✓ {fw_name}: {len(filtered_docs)} doc_ids (was counting {existing_count})")
        updated += 1

    # Save
    with open(PHASE3_OUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated {updated}/{len(extractions)} frameworks with doc_ids")
    print(f"   Output: {PHASE3_OUT}")
    print(f"   Backup: {PHASE3_BACKUP}")

    # Summary
    total_docs = set()
    for fw_data in extractions.values():
        if isinstance(fw_data, dict):
            total_docs.update(fw_data.get("_metadata", {}).get("doc_ids", []))
    print(f"   Total unique docs referenced: {len(total_docs)}")

if __name__ == "__main__":
    main()
