#!/usr/bin/env python3
"""Autonomous LightRAG pipeline recovery — runs silently, auto-heals failures.
Only reports when it actually fixes something or finds a persistent problem.

Triggers:
- FAILED chunks: reset to pending, write recovery files, restart scan
- Stuck pipeline: high pending + 0 processing = trigger scan
- Persistent failures (same chunks failing repeatedly): escalate to user
"""

import json, os, time, sys, requests
from datetime import datetime

NOTEBOOKS = {
    "quann-chat": {"port": 8011, "workspace": "/home/steve/lightrag-apps/quann-chat/workspace"},
    "seo-methodology": {"port": 8012, "workspace": "/home/steve/lightrag-apps/seo-methodology/workspace"},
}

STATE_FILE = "/home/steve/lightrag-apps/.pipeline_recovery_state.json"
ALERT_THRESHOLD = 3  # Alert user after N consecutive failures on same chunk

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"recovery_counts": {}, "persistent_failures": {}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_nb(name, cfg, state):
    """Check one notebook, auto-recover if needed. Returns report lines."""
    reports = []
    nb_state = state.setdefault(name, {"last_recoveries": [], "total_recovered": 0})
    
    try:
        # Get current status
        r = requests.get(f"http://127.0.0.1:{cfg['port']}/documents/status_counts", timeout=10)
        sc = r.json().get("status_counts", {})
    except Exception as e:
        return [f"⚠️ {name}: UNREACHABLE — {e}"]
    
    pending = sc.get("pending", 0)
    processing = sc.get("processing", 0)
    failed = sc.get("failed", 0)
    processed = sc.get("processed", 0)
    total = sc.get("all", 0)
    
    # Case 1: FAILED chunks exist — auto-recover
    if failed > 0:
        try:
            r = requests.get(f"http://127.0.0.1:{cfg['port']}/documents/doc_status", timeout=10)
            doc_status = r.json()
        except:
            return [f"⚠️ {name}: can't read doc_status ({failed} failed)"]
        
        recovered = 0
        now = time.time()
        
        for k, v in doc_status.items():
            val = v
            if isinstance(v, str):
                try: val = json.loads(v)
                except: pass
            if isinstance(val, dict) and val.get("status", "").upper() == "FAILED":
                # Check for persistent failures
                fail_id = f"{name}:{k}"
                pstate = state.get("persistent_failures", {}).get(fail_id, {"count": 0, "last_error": ""})
                pstate["count"] += 1
                pstate["last_error"] = str(val.get("error", ""))[:200]
                state.setdefault("persistent_failures", {})[fail_id] = pstate
                
                if pstate["count"] >= ALERT_THRESHOLD:
                    reports.append(f"🔴 {name}: chunk {k[:30]}... FAILED {pstate['count']}x — {pstate['last_error'][:100]}")
                else:
                    # Reset to pending
                    val["status"] = "pending"
                    doc_status[k] = val
                    recovered += 1
        
        if recovered > 0:
            # Write recovery files
            input_dir = os.path.join(cfg["workspace"], "input")
            os.makedirs(input_dir, exist_ok=True)
            for i, (k, v) in enumerate(doc_status.items()):
                val = v if not isinstance(v, str) else json.loads(v) if v else {}
                if isinstance(val, dict) and val.get("status") == "pending" and f"{name}:{k}" in state.get("persistent_failures", {}):
                    pass  # Already handled above
                elif isinstance(val, dict) and val.get("status") == "pending" and recovered > 0:
                    content = val.get("content_summary", val.get("content", ""))
                    ref = val.get("reference", val.get("file_path", k))
                    fname = f"recover_{i:04d}_{str(ref)[:40].replace('/','_').replace(':','_')}.txt"
                    with open(os.path.join(input_dir, fname), 'w') as f:
                        f.write(f"# Recovery: {ref}\n\n{content}")
            
            # POST back and trigger scan
            requests.post(f"http://127.0.0.1:{cfg['port']}/documents/doc_status", json=doc_status, timeout=10)
            requests.post(f"http://127.0.0.1:{cfg['port']}/documents/scan", timeout=10)
            
            nb_state["total_recovered"] = nb_state.get("total_recovered", 0) + recovered
            nb_state["last_recoveries"].append({
                "time": datetime.now().isoformat(),
                "count": recovered,
                "errors": [str(val.get("error", ""))[:100] for _, v in doc_status.items() 
                          if isinstance(v, dict) and v.get("status","").upper()=="FAILED"][:5]
            })
            reports.append(f"🩹 {name}: recovered {recovered} failed → pending, scan triggered (total recovered: {nb_state['total_recovered']})")
    
    # Case 2: Lots pending but nothing processing — stuck pipeline
    if pending > 50 and processing == 0:
        try:
            requests.post(f"http://127.0.0.1:{cfg['port']}/documents/scan", timeout=10)
            reports.append(f"🔄 {name}: {pending} pending, 0 processing — scan kicked")
        except:
            reports.append(f"⚠️ {name}: {pending} pending, 0 processing — scan FAILED")
    
    # Healthy status line (always include for context)
    pct = round(processed / total * 100) if total > 0 else 0
    reports.append(f"✅ {name}: {processed}/{total} ({pct}%), {pending} queued, {failed} failed, {processing} processing")
    
    return reports

def main():
    state = load_state()
    all_reports = []
    
    for name, cfg in NOTEBOOKS.items():
        reports = check_nb(name, cfg, state)
        all_reports.extend(reports)
    
    save_state(state)
    
    # Only print if there's something worth reporting (not just healthy status)
    has_issues = any(not line.startswith("✅") for line in all_reports)
    if has_issues:
        print("\n".join(all_reports))
    
    # Exit 0 = healthy, 1 = recovered something, 2 = persistent failures
    has_persistent = any("🔴" in line for line in all_reports)
    has_recovery = any("🩹" in line for line in all_reports) or any("🔄" in line for line in all_reports)
    if has_persistent:
        sys.exit(2)
    elif has_recovery:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
