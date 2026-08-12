#!/usr/bin/env python3
"""Daily health check for all services connected to Quan's infrastructure.
Runs silently — only reports via daily summary, not individual messages.

Checks:
1. Nexus server (port 8001) — both quann-chat + seo-methodology notebooks
2. quann.homes — is the site reachable?"""

import subprocess, json, sys, requests
from datetime import datetime, timezone

OK = "✅"
FAIL = "❌"

results = []
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def check_http(name, url, expected_status=200):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == expected_status:
            return f"{OK} {name} — healthy"
        return f"{FAIL} {name} — HTTP {r.status_code}"
    except Exception as e:
        return f"{FAIL} {name} — {type(e).__name__}: {str(e)[:100]}"

def check_nexus(port=8001):
    """Check Nexus server — single endpoint covering both notebooks."""
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=15)
        data = r.json()
        rows = []

        for nb_name in ("quann-chat", "seo-methodology"):
            info = data.get("notebooks", {}).get(nb_name, {})
            rag_ok = info.get("rag_ready", False)
            reranker = info.get("reranker_loaded", False)
            doc = info.get("doc_status", {})

            if rag_ok:
                if doc is None:
                    doc = {}
                pending = doc.get("pending", 0)
                processed = doc.get("processed", 0)
                failed = doc.get("failed", 0)
                total = doc.get("all", 0)
                pct = round(processed / total * 100) if total > 0 else 0

                parts = [f"{processed}/{total} processed ({pct}%)"]
                if pending:
                    parts.append(f"{pending} pending")
                if failed:
                    parts.append(f"{failed} failed")

                if not reranker:
                    parts.append("reranker NOT loaded")

                symbol = OK if (pct > 50 and not failed) else "⚠️"
                rows.append(f"{symbol} {nb_name} — RAG ready, {', '.join(parts)}")
            else:
                rows.append(f"{FAIL} {nb_name} — RAG not ready")

        return "\n".join(rows)

    except Exception as e:
        return f"{FAIL} Nexus server (port {port}) — {type(e).__name__}: {str(e)[:100]}"

# Check quann.homes
results.append(check_http("quann.homes", "https://quann.homes"))
results.append(check_http("quann.homes contact page", "https://quann.homes/contact-us"))

# Check Nexus RAG server (both notebooks)
results.append(check_nexus(8001))

# Print report
print(f"## Daily Health Report — {timestamp}\n")
for r in results:
    print(r)

all_ok = all(line.startswith(OK) for line in results)
print(f"\n**Status:** {'All systems healthy' if all_ok else 'Some systems need attention'}")
sys.exit(0 if all_ok else 1)
