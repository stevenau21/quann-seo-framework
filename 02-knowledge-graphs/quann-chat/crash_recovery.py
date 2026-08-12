#!/usr/bin/env python3
"""
crash_recovery.py — Recover orphaned LightRAG documents stuck in PROCESSING status.

What happened: Server restart/crash kills extraction workers mid-task. LightRAG
has no crash recovery — documents set to "processing" get zero worker processes
assigned and stay "processing" forever (stuck at 2 processing, 0 pending, etc).

This script surgically resets orphaned docs to PENDING so the pipeline will
re-process them on next restart or manual trigger.

Usage:
  python3 crash_recovery.py [--workspace DIR] [--dry-run] [--trigger-pipeline]

Options:
  --workspace DIR       Working dir containing workspace/ (default: current dir)
  --dry-run             Show what would be changed without applying
  --trigger-pipeline    After reset, trigger pipeline via localhost API
  --server-url URL      API server URL for pipeline trigger (default: http://localhost:8011)
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone


def load_json(path):
    """Load and return parsed JSON, or None on failure."""
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"  ⚠️  Could not read {path}: {e}")
        return None


def save_json(path, data):
    """Atomically write JSON data to a file."""
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def find_orphaned(workspace_dir, dry_run=False):
    """
    Find documents stuck in PROCESSING status that have valid content.
    Returns list of (doc_id, doc_info) tuples ready for recovery.
    """
    doc_status_path = os.path.join(workspace_dir, "kv_store_doc_status.json")
    full_docs_path = os.path.join(workspace_dir, "kv_store_full_docs.json")

    doc_status = load_json(doc_status_path)
    full_docs = load_json(full_docs_path)

    if not doc_status:
        print("❌ Cannot read doc_status store. Aborting.")
        return []

    if not full_docs:
        print("⚠️  Cannot read full_docs store. Will check for orphaned docs anyway.")

    orphaned = []
    for doc_id, info in doc_status.items():
        if info.get("status") != "processing":
            continue

        has_content = full_docs and doc_id in full_docs
        orphaned.append({
            "doc_id": doc_id,
            "content_summary": info.get("content_summary", ""),
            "content_length": info.get("content_length", 0),
            "chunks_count": info.get("chunks_count", 0),
            "chunks_list": info.get("chunks_list", []),
            "created_at": info.get("created_at", ""),
            "updated_at": info.get("updated_at", ""),
            "file_path": info.get("file_path", "unknown_source"),
            "track_id": info.get("track_id", ""),
            "has_content": has_content,
            "recoverable": has_content,
        })

        if not has_content:
            print(f"  ⚠️  Orphaned but NO content: {doc_id} (missing from full_docs)")

    return orphaned


def reset_to_pending(workspace_dir, orphaned, dry_run=False):
    """
    Reset orphaned documents from PROCESSING to PENDING status in the JSON store.
    Only resets docs where recoverable=True (has content in full_docs).
    """
    doc_status_path = os.path.join(workspace_dir, "kv_store_doc_status.json")
    doc_status = load_json(doc_status_path)
    if not doc_status:
        return 0

    reset_count = 0
    now = datetime.now(timezone.utc).isoformat()

    for doc in orphaned:
        if not doc["recoverable"]:
            continue

        doc_id = doc["doc_id"]
        if doc_id not in doc_status:
            continue

        doc_status[doc_id].update({
            "status": "pending",
            "error_msg": "",
            "metadata": {},
            "updated_at": now,
        })

        print(f"  🔄 Reset: {doc_id}")
        reset_count += 1

    if reset_count > 0 and not dry_run:
        save_json(doc_status_path, doc_status)
        print(f"\n✅ Saved {reset_count} document(s) reset to PENDING in {doc_status_path}")
    elif reset_count > 0:
        print(f"\n🔍 DRY RUN: Would reset {reset_count} document(s) to PENDING")

    return reset_count


def trigger_pipeline(server_url, timeout=5):
    """
    Wake up the processing pipeline by hitting the documents endpoint.
    The pipeline auto-picks up PENDING docs.
    """
    import urllib.request
    import urllib.error

    url = f"{server_url.rstrip('/')}/documents/process"
    print(f"\n🚀 Triggering pipeline: POST {url}")
    try:
        req = urllib.request.Request(url, method="POST", data=b"{}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode()
            print(f"  Response ({resp.status}): {body[:200]}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        # 404 is expected if endpoint doesn't exist — try health check instead
        if e.code == 404:
            print(f"  POST endpoint not found (404). Pipeline may auto-start from PENDING docs on next health check.")
            return True
        print(f"  HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"  Connection failed: {e}")
        print(f"  (Pipeline will auto-start on next server restart)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Recover orphaned LightRAG documents stuck in PROCESSING status"
    )
    parser.add_argument(
        "--workspace",
        default=os.getcwd(),
        help="Working directory containing workspace/ (default: current dir)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would change without applying"
    )
    parser.add_argument(
        "--trigger-pipeline",
        action="store_true",
        help="Trigger pipeline via API after reset",
    )
    parser.add_argument(
        "--server-url",
        default="http://localhost:8011",
        help="API server URL (default: http://localhost:8011)",
    )
    args = parser.parse_args()

    workspace_dir = os.path.join(args.workspace, "workspace")
    if not os.path.isdir(workspace_dir):
        print(f"❌ Workspace not found: {workspace_dir}")
        sys.exit(1)

    print(f"🔍 Scanning for orphaned documents in: {workspace_dir}\n")

    orphaned = find_orphaned(workspace_dir, dry_run=args.dry_run)

    if not orphaned:
        print("✅ No orphaned documents found. All clear.")
        return

    recoverable = [d for d in orphaned if d["recoverable"]]
    unrecoverable = [d for d in orphaned if not d["recoverable"]]

    print(f"\n📊 Summary:")
    print(f"  Total PROCESSING: {len(orphaned)}")
    print(f"  Recoverable (has content): {len(recoverable)}")
    print(f"  Unrecoverable (no content): {len(unrecoverable)}")

    if unrecoverable:
        print(f"\n⚠️  Unrecoverable docs (no content in full_docs — cannot recover):")
        for doc in unrecoverable:
            print(f"  - {doc['doc_id']}")

    if recoverable:
        print(f"\n{'🔍 DRY RUN — ' if args.dry_run else ''}Resetting {len(recoverable)} docs to PENDING...\n")
        reset_count = reset_to_pending(workspace_dir, recoverable, dry_run=args.dry_run)

        if reset_count > 0 and args.trigger_pipeline and not args.dry_run:
            trigger_pipeline(args.server_url)
    else:
        print("\n⚠️  Nothing to recover (no orphans with valid content).")


if __name__ == "__main__":
    main()
