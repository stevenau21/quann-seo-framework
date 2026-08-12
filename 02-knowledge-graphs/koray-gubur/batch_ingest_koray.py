#!/usr/bin/env python3
"""Batch ingest Koray Gubur's holisticseo.digital corpus (396 URLs) into LightRAG SEO Methodology notebook.
Strategy: 5 pages per batch → insert → scan → poll until processed → next batch.
"""

import requests
import re
import time
import sys
import json
import os

BACKEND = "http://127.0.0.1:8012"
BATCH_SIZE = 5
URLS_FILE = "/home/steve/lightrag-apps/knowledge-synthesis/koray_sitemap_urls.txt"
STATE_FILE = "/home/steve/lightrag-apps/seo-methodology/ingest_state.json"
LOG_FILE = "/home/steve/lightrag-apps/seo-methodology/koray_ingest.log"

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def extract_content(url):
    """Fetch URL and extract readable text content."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; KnowledgeGraphBot/1.0; +research)"
        }
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        html = r.text

        # Strip scripts, styles, nav, footer, header
        for tag_pattern in [r'<script[^>]*>.*?</script>', r'<style[^>]*>.*?</style>',
                            r'<nav[^>]*>.*?</nav>', r'<footer[^>]*>.*?</footer>',
                            r'<header[^>]*>.*?</header>', r'<noscript[^>]*>.*?</noscript>']:
            html = re.sub(tag_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:50000]  # Truncate to 50K chars max
    except Exception as e:
        log(f"  ⚠ Failed to extract {url}: {e}")
        return None

def insert_text(url, content):
    """Insert text into LightRAG backend."""
    try:
        r = requests.post(f"{BACKEND}/documents/text", json={
            "text": content,
            "url": url
        }, timeout=30)
        data = r.json()
        return data.get("track_id")
    except Exception as e:
        log(f"  ⚠ Insert failed for {url}: {e}")
        return None

def trigger_scan():
    """Trigger processing of pending documents."""
    try:
        r = requests.post(f"{BACKEND}/documents/scan", timeout=30)
        return r.json().get("track_id")
    except Exception as e:
        log(f"  ⚠ Scan trigger failed: {e}")
        return None

def get_status():
    """Get document processing status."""
    try:
        r = requests.get(f"{BACKEND}/documents/status_counts", timeout=10)
        return r.json()
    except Exception as e:
        log(f"  ⚠ Status check failed: {e}")
        return None

def wait_for_processing(timeout=600):
    """Poll until all pending documents are processed or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        status = get_status()
        if status is None:
            time.sleep(10)
            continue

        pending = status.get("pending", 0)
        processing = status.get("processing", 0)
        processed = status.get("processed", 0)

        if pending == 0 and processing == 0:
            return True

        log(f"  Status: {pending} pending, {processing} processing, {processed} processed")
        time.sleep(15)

    log(f"  ⚠ Timeout after {timeout}s — some docs may still be pending")
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
    # Load URLs
    with open(URLS_FILE) as f:
        all_urls = [line.strip() for line in f if line.strip()]

    log(f"=== START: {len(all_urls)} URLs, batch size {BATCH_SIZE} ===")

    state = load_state()
    log(f"State: {len(state)} URLs previously tracked")

    total_inserted = 0
    total_errors = 0
    errors = []

    for batch_start in range(0, len(all_urls), BATCH_SIZE):
        batch = all_urls[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(all_urls) + BATCH_SIZE - 1) // BATCH_SIZE
        log(f"\n--- Batch {batch_num}/{total_batches} ({len(batch)} URLs) ---")

        batch_inserted = 0
        for url in batch:
            log(f"  Fetching: {url}")
            content = extract_content(url)
            if content is None:
                total_errors += 1
                errors.append(f"FETCH:{url}")
                continue

            log(f"    → {len(content)} chars, inserting...")
            track_id = insert_text(url, content)
            if track_id:
                batch_inserted += 1
                total_inserted += 1
                state[url] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                total_errors += 1
                errors.append(f"INSERT:{url}")

            time.sleep(0.3)  # Polite to backend

        if batch_inserted > 0:
            log(f"  Triggering scan for {batch_inserted} new docs...")
            scan_id = trigger_scan()
            if scan_id:
                log(f"  Scan triggered: {scan_id}, waiting for processing...")
                wait_for_processing(timeout=600)
            else:
                log(f"  ⚠ Scan failed — will retry on next batch")

        save_state(state)
        log(f"  Batch done. Total: {total_inserted} inserted, {total_errors} errors")

    log(f"\n=== COMPLETE: {total_inserted} inserted, {total_errors} errors ===")

    if errors:
        log(f"Error URLs: {errors[:20]}...")

    # Final scan to catch anything missed
    log("Final scan...")
    trigger_scan()
    wait_for_processing(timeout=900)

    # Final status
    final_status = get_status()
    log(f"Final status: {json.dumps(final_status, indent=2)}")

if __name__ == "__main__":
    main()
