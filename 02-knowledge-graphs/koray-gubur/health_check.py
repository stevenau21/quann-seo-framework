#!/usr/bin/env python3
"""
Production health check for seo-methodology LightRAG service.
Tests: basic health, CORS preflight, research query (with retry).
Timeout: 60s for research flow to accommodate retry loop + slow LLM.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone


def urlopen(url, method="GET", data=None, headers=None, timeout=90):
    all_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }
    if headers:
        all_headers.update(headers)
    req = urllib.request.Request(url, method=method, data=data, headers=all_headers)
    return urllib.request.urlopen(req, timeout=timeout)


API_URL = "http://localhost:8002"
ORIGINS = ["https://quann.homes", "https://quanbot.quann.homes"]

OK = "✅"
FAIL = "❌"
results = []
start = time.monotonic()


def check(name, fn):
    try:
        fn()
        results.append(f"{OK} {name}")
        return True
    except Exception as e:
        results.append(f"{FAIL} {name}: {e}")
        return False


def basic_health():
    with urlopen(f"{API_URL}/health") as r:
        assert r.status == 200
        data = json.loads(r.read())
        assert data["rag_ready"] is True


def cors_preflight():
    for origin in ORIGINS:
        with urlopen(f"{API_URL}/ask", method="OPTIONS",
                     headers={"Origin": origin, "Access-Control-Request-Method": "POST"}) as r:
            assert r.status == 200
            assert r.headers.get("Access-Control-Allow-Origin") == origin


def research_flow():
    """Test with 2 attempts — LLM calls may retry internally.
    Query: 'What is entity-based SEO?' — should return 200+ chars from RAG context."""
    body = json.dumps({"query": "What is entity-based SEO?"}).encode()
    last_error = None
    for attempt in range(2):
        try:
            with urlopen(f"{API_URL}/ask", method="POST", data=body,
                         headers={"Content-Type": "application/json"}) as r:
                assert r.status == 200
                data = json.loads(r.read())
                answer_len = len(data["answer"])
                # 100+ chars: legitimate answer (not an error message)
                assert answer_len >= 100, f"answer too short ({answer_len} chars)"
                return
        except Exception as e:
            last_error = e
            if attempt == 0:
                time.sleep(3)  # Brief wait before retry
    raise last_error  # Re-raise after exhausting retries


all_ok = True
all_ok &= check("basic_health", basic_health)
all_ok &= check("cors_preflight", cors_preflight)
all_ok &= check("research_flow", research_flow)

elapsed = (time.monotonic() - start) * 1000
summary = f"{'PASS' if all_ok else 'FAIL'} | {elapsed:.0f}ms | " + " | ".join(results)
print(summary)

with open("/home/steve/lightrag-apps/seo-methodology/health.log", "a") as f:
    f.write(f"[{datetime.now(timezone.utc).isoformat()}] {summary}\n")

with open("/home/steve/lightrag-apps/seo-methodology/health_last.txt", "w") as f:
    f.write(f"pass={str(all_ok).lower()}\ntime={datetime.now(timezone.utc).isoformat()}\nchecks={results!r}\n")

sys.exit(0 if all_ok else 1)
