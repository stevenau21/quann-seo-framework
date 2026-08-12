#!/usr/bin/env python3
"""
Batch-ingest 88 Koray lecture transcripts into LightRAG (port 8014).
Uses /documents/text endpoint — incremental by MD5 dedup in doc_status.
Follows lightrag-incremental-ingestion skill: never wipe, gleaning=2.
"""
import requests
import time
import json
from pathlib import Path

BACKEND = "http://127.0.0.1:8014"
COURSE_DIR = "/.hermes/Koray Course"
LOG_FILE = "/home/steve/lightrag-apps/koray-lectures/ingest.log"
STATE_FILE = "/home/steve/lightrag-apps/koray-lectures/ingest_state.json"
BATCH_SIZE = 2
SCAN_TIMEOUT = 3600  # 1hr for Pro's ~88s per chunk

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_status():
    try:
        r = requests.get(f"{BACKEND}/documents/status_counts", timeout=10)
        return r.json()
    except Exception as e:
        log(f"  ⚠ Status check failed: {e}")
        return None

def insert_text(filepath, content):
    """Insert text into LightRAG backend."""
    try:
        # Truncate very long files to 80K chars for context window
        truncated = content[:80000]
        r = requests.post(f"{BACKEND}/documents/text", json={
            "text": truncated,
            "url": str(filepath)
        }, timeout=30)
        data = r.json()
        return data.get("track_id")
    except Exception as e:
        log(f"  ⚠ Insert failed for {filepath.name}: {e}")
        return None

def trigger_scan():
    try:
        r = requests.post(f"{BACKEND}/documents/scan", timeout=30)
        return r.json().get("track_id")
    except Exception as e:
        log(f"  ⚠ Scan trigger failed: {e}")
        return None

def wait_for_processing(timeout=1200):
    start = time.time()
    while time.time() - start < timeout:
        status = get_status()
        if status is None:
            time.sleep(10)
            continue
        pending = status.get("pending", 0)
        processing = status.get("processing", 0)
        processed = status.get("processed", 0)
        failed = status.get("failed", 0)
        if pending == 0 and processing == 0:
            return True
        log(f"  Status: {pending} pending, {processing} processing, {processed} processed, {failed} failed")
        time.sleep(20)
    return False

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    course_path = Path(COURSE_DIR)
    txt_files = sorted(course_path.glob("*.txt"))
    log(f"=== START: {len(txt_files)} files, batch size {BATCH_SIZE} ===")
    
    state = load_state()
    log(f"State: {len(state)} files previously tracked")
    
    total_inserted = 0
    total_errors = 0
    skipped = 0
    
    for batch_start in range(0, len(txt_files), BATCH_SIZE):
        batch = txt_files[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(txt_files) + BATCH_SIZE - 1) // BATCH_SIZE
        log(f"\n--- Batch {batch_num}/{total_batches} ({len(batch)} files) ---")
        
        batch_inserted = 0
        for fpath in batch:
            key = str(fpath)
            if key in state:
                log(f"  ⏭️ {fpath.name} (already tracked)")
                skipped += 1
                continue
            
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                if len(content) < 100:
                    log(f"  ⚠ {fpath.name}: too short ({len(content)} chars)")
                    continue
                
                log(f"  → {fpath.name} ({len(content):,} chars)")
                track_id = insert_text(fpath, content)
                if track_id:
                    batch_inserted += 1
                    total_inserted += 1
                    state[key] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    total_errors += 1
            except Exception as e:
                log(f"  ❌ {fpath.name}: {e}")
                total_errors += 1
            
            time.sleep(0.5)
        
        if batch_inserted > 0:
            log(f"  Triggering scan for {batch_inserted} new docs...")
            scan_id = trigger_scan()
            if scan_id:
                log(f"  Scan triggered: {scan_id}, waiting for processing...")
                ok = wait_for_processing(timeout=SCAN_TIMEOUT)
                if not ok:
                    log(f"  ⚠ Timeout — continuing to next batch")
            else:
                log(f"  ⚠ Scan failed")
        
        save_state(state)
        log(f"  Batch done. Total: {total_inserted} inserted, {skipped} skipped, {total_errors} errors")
    
    log(f"\n=== FINAL SCAN ===")
    trigger_scan()
    wait_for_processing(timeout=1800)
    
    final_status = get_status()
    log(f"Final status: {json.dumps(final_status, indent=2)}")
    log(f"\n=== COMPLETE: {total_inserted} inserted, {skipped} skipped, {total_errors} errors ===")

if __name__ == "__main__":
    main()
