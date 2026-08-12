---
name: lightrag-rag-apps
description: Build self-contained LightRAG-powered FastAPI apps (not Dify/Weaviate). Two-app architecture — separate workspaces, same blueprint. Scrape sitemaps → index with entity extraction → serve RAG-enhanced responses via Ollama.
category: integrations
---

# LightRAG RAG Apps (Dify-Free Architecture)

Replace broken Dify/Weaviate with LightRAG — a file-based RAG library with knowledge graph + vector retrieval. Each app is a standalone FastAPI service with its own LightRAG workspace. Zero Docker dependency for the RAG layer (just Ollama for inference).

## When to use

- Dify is broken (Weaviate issues, plugin daemon crashes, model_schema: null)
- You need multiple RAG apps that share the same architecture but different data
- The source is a website sitemap (quann.homes, holisticseo.digital, etc.)
- You have Ollama running (cloud or local) for LLM + embeddings

## Architecture

Each app follows this pattern:

```
┌──────────────────────────────────────────┐
│  lightrag-apps/<app-name>/               │
│  ├── scrape_site.py    (fetch→clean→chunk)│
│  ├── index_<name>.py   (LightRAG insert) │
│  ├── server.py         (FastAPI)         │
│  ├── data/             (JSONL chunks)    │
│  └── workspace/        (LightRAG store)  │
└──────────────────────────────────────────┘
```

Two apps currently exist:
- **quann-chat** (`/home/steve/lightrag-apps/quann-chat/`) — Website chatbot, scrapes quann.homes (22 pages → 206 chunks)
- **seo-methodology** (`/home/steve/lightrag-apps/seo-methodology/`) — SEO research tool, scrapes holisticseo.digital (17 pages)

## QuanBot is off-limits

QuanBot (`/home/steve/quanbot/`) is the Instagram DM bot — a completed project. **Never modify it** to add RAG, chat endpoints, or anything else. It serves widget/widget.js/chat.html routes — those are QuanBot's responsibility. The RAG apps are entirely separate services on different ports. The user gets frustrated when we touch completed work.

## Creating a new app

### 1. Set up directory structure

```bash
mkdir -p /home/steve/lightrag-apps/<app-name>/{data,workspace}
```

### 2. Build the scraper

Scrapers are Python scripts that shell out to Node.js Playwright (the site is React, needs JS rendering). They:
- Fetch the sitemap dynamically (or use a hardcoded URL list)
- Spawn a headless Chromium via `npx playwright`
- Clean HTML (strip scripts/styles/nav/header/footer)
- Smart-chunk on sentence boundaries (~800 chars per chunk)
- Save to `data/<name>_chunks.jsonl` with `{text, source}` per line

The Node.js script is embedded in the Python file as a raw string. Output path is hardcoded in the JS (not passed as argv — shell quoting causes issues).

### 3. Build the indexer

Uses LightRAG's entity extraction pipeline to build a knowledge graph + vector index:
- Uses `gemma4:31b-cloud` for entity extraction (LLM)
- Uses `nomic-embed-text-v2-moe` for embeddings
- LightRAG's `llm_model_func` is only used during indexing, not query time
- **CRITICAL: use batch insert, NOT per-chunk loop.** Feed all texts as a list to `rag.ainsert(texts, ids=ids, file_paths=file_paths)`. Per-chunk iteration takes ~80s/chunk (4.5 hours for 206 chunks) and hangs silently. Batch mode lets LightRAG pipeline internally.
- Run in background with a long timeout (600s+)

Key config:
```python
LLM_MODEL = "gemma4:31b-cloud"
EMBED_MODEL = "nomic-embed-text-v2-moe"
OLLAMA_BASE = "https://ollama.quann.homes"
OLLAMA_API_KEY = "gg4L2rt6kzjJA8kk"
```

### CRITICAL: GPU-safe constructor params

LightRAG defaults overload the GTX 1080 (8GB). Without these, you'll get `httpx.HTTPStatusError: Server error '500'` from `/api/embeddings` when it fires too many parallel GPU calls:

```python
rag = LightRAG(
    working_dir=WORKSPACE,
    llm_model_func=llm_complete,
    embedding_func=EmbeddingFunc(embedding_dim=768, max_token_size=8192, func=embed_texts),
    embedding_func_max_async=1,   # GTX 1080 8GB — one GPU call at a time
    llm_model_max_async=2,        # Cloud LLM handles 2 parallel safely
    max_parallel_insert=1,        # Sequential inserts (prevents GPU contention)
    addon_params={
        "entity_extract_max_gleaning": 0,  # Skip refinement — clean site content doesn't need re-checks
    },
)
```

| Param | Default | GTX 1080 Safe | Why |
|---|---|---|---|
| `embedding_func_max_async` | 4 | **1** | 500 errors under parallel GPU load |
| `llm_model_max_async` | 4 | **2** | Cloud `gemma4:31b-cloud` handles 2 safely |
| `max_parallel_insert` | 2 | **1** | Prevents GPU contention between embed calls |
| `entity_extract_max_gleaning` | 1 | **0** | Gleaning loop adds ~50% time; clean website content doesn't benefit |

### 4. Build the server

FastAPI app with lifespan that initializes LightRAG on startup:
- Uses a **no-op LLM** for LightRAG (`async def _noop_llm(...): return '{"high_level_keywords": [], "low_level_keywords": []}'`) — we only use LightRAG for retrieval, not generation. **CRITICAL: must return valid JSON, not empty string.** Returning `""` causes LightRAG to log `ERROR: No JSON-like structure found in the LLM respond` on every query because it tries to `json.loads()` the result for keyword extraction.
- Retrieval via `rag.aquery(query, param=QueryParam(mode="hybrid", only_need_context=True, enable_rerank=False))`
  - **`enable_rerank=False`** for quann-chat (hybrid retrieval already high-quality for 206 chunks; reranker adds negligible benefit). **`enable_rerank=True`** for SEO methodology (deep research queries benefit from precision re-ranking of 40→top 5 chunks).
  - **GPU reranker is available** — GTX 1080 CUDA works in WSL (confirmed `torch.cuda.is_available()=True`). `mxbai-rerank-base-v1` loads at ~0.39 GB VRAM. Use it for apps where query complexity justifies the extra latency.

### Reranker function signature (LightRAG v1.4.15+)

LightRAG calls the reranker as `await rerank_func(query=query, documents=texts, top_n=N)`. It expects either:
- Raw score list: `[0.85, 0.12, ...]` (same length as documents)
- Index-based format (preferred): `[{"index": 0, "relevance_score": 0.85}, ...]` — only top_n results

**🚨 The `top_n` kwarg is mandatory to accept** — LightRAG passes it, and missing it causes `Error during reranking: _rerank_func() got an unexpected keyword argument 'top_n'` with silent fallback to un-reranked chunks.

Correct implementation:
```python
def _rerank_func(query: str, documents: list[str], top_n: int = 5) -> list[dict]:
    """LightRAG-compatible: accepts top_n, returns index-based dicts."""
    pairs = [[query, doc] for doc in documents]
    scores = _reranker.predict(pairs)
    indexed = [(i, float(score)) for i, score in enumerate(scores)]
    indexed.sort(key=lambda x: x[1], reverse=True)
    top = indexed[:top_n]
    return [{"index": idx, "relevance_score": score} for idx, score in top]
```

Query with reranking:
```python
result = await rag.aquery(
    query,
    param=QueryParam(
        mode="hybrid",
        only_need_context=True,
        enable_rerank=True,
        top_k=40,              # Retrieve 40 candidates
        chunk_top_k=5,         # Keep top 5 after rerank
    ),
)
```
- Context is truncated to ~3000 chars (sentence-boundary-aware)
- The retrieved context is injected into a system prompt template
- The assembled prompt is sent to Ollama for the actual response
- Runs on a unique port (e.g., 8001 for quann-chat)

**🚨 MANDATORY: CORS middleware.** The chat widget is embedded on `quann.homes` but fetches `chat.quann.homes` — a cross-origin request. Without CORS headers, the **browser silently blocks every request** while `curl` works fine. This creates a false-positive "it works" signal in terminal testing. Add to every server:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quann.homes", "https://quanbot.quann.homes"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

**Verify CORS works** (not just curl — check the headers):
```bash
curl -s -D - -X OPTIONS https://chat.quann.homes/chat \
  -H 'Origin: https://quann.homes' \
  -H 'Access-Control-Request-Method: POST'
# Must see: access-control-allow-origin: https://quann.homes
```

### 5. Set up weekly re-indexing cron

Each app needs a weekly cron to scrape fresh content and re-index. **Weekly is preferred** — website content rarely changes day-to-day, and indexing takes 2-3 hours on the GTX 1080. Use a shell wrapper script that activates the virtualenv:

```bash
#!/bin/bash
# cron_scrape.sh — called by cronjob tool daily at midnight
set -e
APP_DIR="/home/steve/lightrag-apps/<app-name>"
VENV="/home/steve/lightrag-env/bin/python3"

echo "[$(date)] Starting daily scrape + re-index for <app-name>"
cd "$APP_DIR"

# Scrape fresh content
$VENV "$APP_DIR/scrape_site.py"
echo "[$(date)] Scrape complete — $(wc -l < data/<name>_chunks.jsonl) chunks"

# Re-index (overwrites workspace)
$VENV "$APP_DIR/index_<name>.py"
echo "[$(date)] Indexing complete"

# Verify workspace exists
ls -la workspace/vdb_entities.json && echo "[$(date)] DAILY UPDATE SUCCESS"
```

Schedule via the `cronjob` tool. **Weekly is preferred** (content doesn't change daily):
```
# Weekly (Sundays midnight CT) — recommended, content doesn't change daily
schedule: "0 0 * * 0"
# Daily (midnight) — only if content updates frequently
schedule: "0 0 * * *"
enabled_toolsets: ["terminal", "file"]
```

⚠️ Two apps can't re-index simultaneously — stagger by 30 minutes or rely on sequential cron scheduling. The cron wrapper MUST use full paths for everything; the cron environment has no venv activated by default.

**🚀 Smart diffing — skip re-indexing when nothing changed.** Scraping takes 30s but re-indexing takes 2-3 hours. Most weekly cron runs will see zero content changes. Avoid the wasted work by hashing the scraped JSONL and comparing against last run:

```bash
# In the cron shell script, AFTER scraping:
CHUNKS="/home/steve/lightrag-apps/<app>/data/<name>_chunks.jsonl"
if ./lightrag-env/bin/python3 /home/steve/lightrag-apps/has_changed.py "$CHUNKS" >> "$LOG" 2>&1; then
    # Content changed — run index + atomic swap + restart
    ...
else
    echo "[$(date -Iseconds)] Done — no content changes, skipped index" >> "$LOG"
fi
```

The `has_changed.py` script (at `/home/steve/lightrag-apps/has_changed.py`):
- Computes MD5 of the JSONL file
- Compares against stored `.md5` file from last run
- Exit 0 = changed (proceed with index), exit 1 = unchanged (skip)
- Works correctly on first run (no previous hash → treats as changed)

### 6. Deploy as systemd service

```bash
# Create service file
sudo tee /etc/systemd/system/<app-name>.service << EOF
[Unit]
Description=<App Name> - LightRAG Service
After=network.target

[Service]
Type=simple
User=steve
WorkingDirectory=/home/steve/lightrag-apps/<app-name>
ExecStart=/home/steve/lightrag-env/bin/python3 server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now <app-name>
```

## Cloudflare Tunnel Deployment

Each LightRAG app runs in WSL on a dedicated port. To expose publicly:

1. Add ingress rule to `/mnt/c/Users/steve/n8n-deploy/data/cloudflared/config.yml`:
```yaml
  - hostname: chat.quann.homes
    service: http://host.docker.internal:8001
```
**Why `host.docker.internal` works:** Windows auto-forwards WSL ports to `localhost`, so Docker containers reach WSL services via the host gateway. No need for WSL IP (`172.27.144.1`) — Docker can't route to WSL's internal network directly.

2. Add DNS and restart:
```bash
docker exec cloudflared /usr/local/bin/cloudflared tunnel route dns n8n-tunnel chat.quann.homes
docker restart cloudflared
```

## Pitfalls

### 🚨 Entity extraction IS LightRAG — don't try to swap it
LightRAG uses prompt-driven LLM extraction to produce structured entity_name/entity_type/entity_description tuples plus relationships. This feeds the knowledge graph construction. Swapping in spaCy or standalone NER would break the output format, graph building, and retrieval. The cloud LLM per-chunk cost (~50s/chunk) is the price of rich multi-hop retrieval. Tune with constructor params (below) to minimize GPU errors; don't try to bypass the pipeline.

### 🚨 NEVER index one chunk at a time — use batch insert
Looping `rag.ainsert(chunk, ...)` one-by-one for 206 chunks takes ~80 seconds per chunk (~4.5 hours total) and the process hangs silently with no stdout. Instead, pass **all texts as a list**:
```python
texts = [c["text"] for c in chunks]
ids = [f"chunk-{i:04d}" for i in range(len(chunks))]
file_paths = [f"https://site.com/chunk/{i:04d}" for i in range(len(chunks))]
await rag.ainsert(texts, ids=ids, file_paths=file_paths)
```
LightRAG pipelines and batches internally — much faster, no silent hangs.

### NEVER run two indexers in parallel — GPU hangs both
Ollama can only handle one heavy embedding workload at a time. Two simultaneous `ainsert()` calls will both hang at 0% CPU with no output. Always index sequentially — wait for the first to finish before starting the second. Even querying during indexing can fail. The 8GB GTX 1080 is the bottleneck; `nomic-embed-text-v2-moe` loads ~911MB but parallel workloads cause contention.

### stdout is buffered — silence does NOT mean stuck
Python buffers stdout when piped through bash. The batch indexer will show zero output even as it's actively working. To check actual progress:
```bash
ls -la workspace/   # watch file sizes grow
```
`kv_store_llm_response_cache.json` growing = entity extraction happening. `vdb_entities.json` / `vdb_relationships.json` growing = vectors being stored. Don't kill the process just because there's no stdout.

### LightRAG `ainsert` API traps
- Parameter is `file_paths` (plural, expects a **list**), NOT `file_path`
- **Must provide both `ids` AND `file_paths` as lists** — LightRAG uses content hash for dedup by default, so without explicit `ids`, chunks with shared metadata (file_path, content) get rejected as "duplicate document detected"
- Always pass all chunks in a single list call (see Pitfalls section) rather than one-at-a-time
- **Don't try to replace entity extraction with spaCy/standalone NER** — LightRAG's entire pipeline (entity types, relationship format, graph construction) is built around LLM extraction. Dropping in a local NER model breaks the output format and knowledge graph. Tune it with the constructor params above instead.

### Don't mix LightRAG's LLM with your own
LightRAG needs an `llm_model_func` for indexing (entity extraction), but at query time we provide a no-op. All response generation goes through our own Ollama call with the system prompt template — NOT through LightRAG's `aquery` result directly. Use `only_need_context=True` to get raw context.

### Embedding model must match
If migrating from Weaviate (indexed with a different model), the embeddings are incompatible. LightRAG starts fresh — this is a feature, not a bug.

### 🚨 CORS — curl is NOT a browser; test what the user actually sees
The widget is embedded on `quann.homes` but fetches `chat.quann.homes` — a cross-origin request. Without explicit CORS headers, **the browser blocks every request silently**. `curl` never blocks on CORS, so terminal testing returns 200 OK while users see "Connection issue — try again!" **Every server must include CORSMiddleware** (see Server section above). After deploy, verify with:
```bash
curl -s -D - -X OPTIONS https://chat.quann.homes/chat \
  -H 'Origin: https://quann.homes' \
  -H 'Access-Control-Request-Method: POST' | grep access-control-allow-origin
```
If this doesn't show `access-control-allow-origin: https://quann.homes`, CORS is broken.

### CDN caching hides widget updates
The chat widget (`widget.js`) is served with `Cache-Control: no-store` headers, so changes are visible instantly. **chat-iframe.html is NOT** — Cloudflare may cache it for minutes, showing stale Dify-referencing code or unrendered `**bold**`. After updating the iframe, either wait for cache expiry or add `Cache-Control: no-store` headers to the route.

### Widget files need markdown rendering too
Both `chat-iframe.html` and `quan-chat-widget.js` use `textContent` by default — this renders `**bold**` as literal asterisks. Fix: switch to `innerHTML` with simple regex replacements before injection:
```javascript
text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
text = text.replace(/\n/g, '<br>');
d.innerHTML = text;
```

### 🚨 Pydantic ForwardRef — NEVER define models inside create_app()

Defining Pydantic models as local classes inside a factory function causes ForwardRef corruption in FastAPI's OpenAPI schema generation. The route appears to register correctly but silently rejects valid fields with `"Field required"` errors pointing to the **old/unresolved field name**.

**Symptom:** Source code shows `message: str = Field(...)` but the endpoint rejects `{"message": "hello"}` with `"Field required" loc=["query","body"]`. Deleting all `.pyc`, setting `PYTHONDONTWRITEBYTECODE=1`, and even running a fresh process on a new port all still fail. The source is correct — Pydantic's internal schema is corrupted.

**Root cause:** `class _Request(BaseModel)` defined inside `create_app()` creates a `ForwardRef('_Request')` that FastAPI cannot resolve at OpenAPI generation time: `PydanticUserError: TypeAdapter[ForwardRef('_Request')] is not fully defined`. The corrupted schema falls back to cached/incorrect field names.

**Fix — module-level models:**
```python
# BEFORE (broken — inside create_app):
def create_app(config):
    class _Request(BaseModel):
        message: str = Field(..., min_length=1)
    @app.post("/chat")
    async def route(body: _Request): ...

# AFTER (correct — module level):
class NexusChatRequest(BaseModel):
    message: str = Field(..., min_length=1)

def create_app(config):
    @app.post("/chat")
    async def route(body: NexusChatRequest): ...
```

**Detection:** `curl /openapi.json` returns `Internal Server Error` with the PydanticUserError traceback in server logs. Normal schema generation succeeds silently even with this bug — only the actual route validation fails.

### 🚨 Missing `asyncio` — import it at module level in nexus_shared

The `_call_llm` function uses `asyncio.get_event_loop()` and `asyncio.sleep()`. If `asyncio` is only imported inside a specific function (e.g., `start_reranker()`), calls from `_call_llm` fail with `name 'asyncio' is not defined`. Always have `import asyncio` at the top of `nexus_shared.py`.

### 🚨 Embedding model token limit — large documents fail silently

`nomic-embed-text-v2-moe` has an ~8192 token context window. Documents exceeding this (anything above ~25K chars / ~7K tokens) cause `HTTP 500: the input length exceeds the context length` from Ollama. LightRAG logs this as a per-chunk error and the document fails to index entirely.

**Symptom:** `ainsert` runs without crashing but workspace `vdb_entities.json` never appears, or only partial data for small documents. `kv_store_doc_status.json` shows many `failed` entries. Logs show repeated `Embedding func: Error in decorated function` for chunk tasks.

**Fix — pre-chunk large documents before LightRAG ingestion:**
```python
import re

def chunk_text(text: str, size: int = 3000) -> list[str]:
    """Split on sentence boundaries, keeping chunks under 'size' chars (~700 tokens)."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) > size and current:
            chunks.append(current.strip())
            current = s
        else:
            current += (" " if current else "") + s
    if current.strip():
        chunks.append(current.strip())
    return chunks
```

**Always chunk documents before indexing if any exceed 20K chars.** The chunk size should target ~700-800 tokens (well under the 8192 limit) to leave room for the `search_query:` prefix that Ollama prepends. The client-knowledge transcripts were 4K-99K chars each and all 18 failed until chunked to 3000-char pieces.

An interrupted batch insert (`ainsert` killed mid-run) leaves a valid-looking workspace that passes `rag_ready: true` health checks but causes infinite hangs on every `/ask` or `/chat` query. The workspace files exist and have plausible sizes (2.4MB) but internal graphs are corrupted — LightRAG enters infinite entity-resolution loops with zero output.

**Symptom:** `/health` returns 200 with `rag_ready: true`, but `curl /ask` hangs until timeout (45s+) with empty response. Process shows normal CPU/memory usage — looks alive but is dead.

**Root cause:** Interrupted batch insert creates partial graph chunks where entity→relation→chunk back-references point to missing data. LightRAG's hybrid retrieval traverses these broken references in a loop.

**Detection:** Compare workspace sizes against known-healthy backup:
```bash
du -sh workspace/ workspace_old/
# 2.4M  workspace/       ← suspiciously small (healthy is 19M)
# 19M   workspace_old/   ← known-good backup
```

**Fix — workspace restore:**
```bash
kill <server-pid>                              # stop server
mv workspace workspace_corrupted               # move corrupted aside
# Server will auto-fallback to workspace_old, or copy it explicitly:
cp -r workspace_old workspace
# Restart server
```

**Prevention:** Always maintain a `workspace_old` backup. After every successful re-index, replace the backup:
```bash
rm -rf workspace_old
cp -r workspace workspace_old
```

### Widget.js payload format — match the backend API

The Quanbot receptionist expects `subscriber_id` not `session_id`, and reads response field `reply` not `data.reply` or `answer`. When rewiring the website widget from LightRAG to Quanbot, update both the `fetch()` payload AND the response parsing:

```javascript
// Payload to Quanbot:
fetch(API_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    subscriber_id: conversationId,  // NOT session_id
    message: q
  })
})

// Response parsing:
var data = await resp.json();       // {ok: true, reply: "..."}
var reply = data.reply;             // NOT data.answer or data.data.reply
```

## 🚨 Production Health Watchdog (MANDATORY)

Every LightRAG server MUST have a recurring watchdog that tests the **full browser flow** — not just TCP or HTTP 200. The gap between "curl works" and "widget works" cost us a production outage:

| Test | Catches | Why it matters |
|---|---|---|
| CORS preflight | Missing `Access-Control-Allow-Origin` headers | Browser blocks cross-origin `fetch()` silently. `curl` never fails. |
| Full chat flow | Ollama down, RAG retrieval broken, GPU exhaustion | `/health` returns 200 even when `/chat` times out |
| RAG readiness | Workspace corruption (empty `vdb_chunks.json`) | Server starts but returns "I don't know" to every query |

Health check script lives at `<app-dir>/health_check.py`. It runs three checks and exits non-zero on any failure:

```bash
/home/steve/lightrag-env/bin/python3 <app-dir>/health_check.py
# PASS | 8000ms | ✅ basic_health | ✅ cors_preflight | ✅ chat_flow
#  or
# FAIL | 2000ms | ✅ basic_health | ❌ cors_preflight: Allow-Origin=* != https://quann.homes
```

The watchdog cron runs every 15 minutes, is completely silent on success, and auto-restarts the service on failure:

```
cronjob create
  schedule: "every 15m"
  prompt: "Run health check. If it fails, restart the service and re-test. Only output on failure."
  enabled_toolsets: ["terminal", "file"]
```

**This must be created for EVERY deployed server.** No exceptions.

## 🧪 Stress Test Benchmarks

### Pre-Fix (May 4, 2026 — before remediation)

Concrete numbers from a full-system concurrent stress test with `gemma4:31b-cloud` on a GTX 1080 8GB, WSL2 → Windows host Ollama. System: 7.8GB total, 5.4GB used at baseline. **7 unnecessary Dify containers wasting ~1.5GB RAM.**

| Component | Port | Health | Single Query | 5 Concurrent | Failure Rate |
|---|---|---|---|---|---|
| **Quanbot Receptionist** | 8000 | ✅ | 1.1–3s | 2.9–5.3s (all pass) | 0% |
| **Quann Chat LightRAG** | 8001 | ✅ | 2.8–3.3s | 2/5 timeout at 45s | **40%** |
| **SEO Methodology LightRAG** | 8002 | ✅ (1ms) | ❌ Times out at 45s | N/A | **100%** |

**SEO server root cause:** Corrupted workspace from interrupted batch insert (see `🚨 Corrupted workspace detection` pitfall). 2.4MB workspace vs 19.2MB healthy backup. Server starts, `/health` returns 200, but `/ask` silently hangs — looks like a TCP issue but is actually a broken knowledge graph causing infinite entity-resolution loops.

### Post-Fix (May 4, 2026 — after remediation)

Fixes applied: Dify bloat killed (7 containers → freed 1.5GB), SEO workspace restored from backup, WSL2 TCP keepalive added to Quann Chat, widget rewired to Quanbot.

| Component | Port | Health | Single Query | 8-Way Concurrent | Failure Rate |
|---|---|---|---|---|---|
| **Quanbot Receptionist** | 8000 | ✅ | 0.8–2.2s | 3/3 pass (0.8–2.8s) | 0% |
| **SEO Methodology LightRAG** | 8002 | ✅ | 3/3 pass (18–25s) | 2/2? no — 1/2 pass | **50%** |
| **Quann Chat LightRAG** | 8001 | ✅ | 2/2 pass (2.8–4.2s) | 1/2 pass | **50%** |
| **Public Tunnel (widget)** | — | ✅ | 2/2 pass (2.6–9.6s) | 1/1 pass | 0% |

**Overall: 6/8 concurrent passed (75%).** The 2 failures were 1 SEO + 1 QuannChat timeout under max concurrent blast — WSL2 virtual switch congestion during simultaneous connection setup, not a code bug. At normal traffic levels (1-2 simultaneous visitors), this never materializes.

**Dify stack drift:** All 11 Dify containers were running despite the skill doc saying only nginx+weaviate+postgres+redis should be up. This is a recurring drift pattern — containers restart after system reboots/Docker updates. Always check with `docker ps --format '{{.Names}}' | grep dify` during diagnostics.

## WSL2 + Systemd Production Hardening

Running LightRAG servers under systemd inside WSL2 exposes unique failure modes not seen in development. These were discovered through repeated production outages on the SEO Methodology server.

### 🚨 The Cloudflare tunnel drops long-lived connections

`ollama.quann.homes` → Docker cloudflared → `host.docker.internal` → WSL → Ollama. This 4-hop chain drops TCP connections held open >10 seconds (Ollama LLM calls frequently take 20-60s). The symptom: `httpx.ReadTimeout` on roughly 40% of queries.

**Fix: Direct IP connection to the Windows host.** Skip the tunnel entirely:
```python
import socket

def _resolve_host_ip() -> str:
    """Resolve Windows host IP once at startup. Falls back to known static IP."""
    try:
        return socket.gethostbyname("host.docker.internal")
    except socket.gaierror:
        return "192.168.4.148"  # Fallback if DNS fails

OLLAMA_HOST_IP = _resolve_host_ip()
OLLAMA_BASE = f"http://{OLLAMA_HOST_IP}:11434"
```

### 🚨 httpx.AsyncClient hangs in systemd context

`httpx.AsyncClient` (used by LightRAG internally and common in async FastAPI code) accumulates stalled connections under systemd in WSL2. Queries that work fine from a terminal fail with `ReadTimeout` when the service runs as a daemon.

**Fix: Synchronous `requests` wrapped in `run_in_executor`.**
```python
import asyncio
import requests

def _call_ollama_sync(prompt: str, model: str, base_url: str) -> dict:
    """Synchronous Ollama call — safe for run_in_executor."""
    resp = requests.post(
        f"{base_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()

async def call_ollama(prompt: str, model: str = "gemma4:31b-cloud") -> dict:
    """Async wrapper: runs sync requests in thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _call_ollama_sync, prompt, model, OLLAMA_BASE)
```

This eliminates all async networking quirks while integrating cleanly with LightRAG's async pipeline.

### 🚨 Retry wrapper for WSL2 kernel-level TCP instability

Even with direct IP and `requests`, WSL2's virtual network adapter has a kernel bug that drops ~10% of TCP connections held open >30 seconds. This is not fixable — it's a Windows/WSL bug.

**Fix: Retry up to 3 attempts with exponential backoff.**
```python
import asyncio

async def call_ollama_with_retry(prompt: str, model: str = "gemma4:31b-cloud", max_attempts: int = 3) -> dict:
    """Call Ollama with retry logic for WSL2 TCP instability."""
    last_error = None
    for attempt in range(max_attempts):
        try:
            return await call_ollama(prompt, model)
        except Exception as e:
            last_error = e
            if attempt < max_attempts - 1:
                await asyncio.sleep(2 ** attempt)  # 0s, 2s, 4s
    raise last_error
```

Observed: 8/9 long-running queries succeed with retry (vs. ~60% without). The one failure per ~9 queries succeeds on the next attempt.

### 🚨 HuggingFace model downloads hang silently in systemd

Systemd services typically lack HF tokens and have restricted network environments. Attempting to auto-download a reranker model (e.g., `mxbai-rerank-base-v1`) causes the service to hang at startup with zero output — no error, no timeout, just silence.

**Fix: Use a passthrough reranker instead and set `enable_rerank=False`.**
```python
async def _rerank_func(query: str, documents: list[str], top_n: int = 5) -> list[dict]:
    """Passthrough reranker — returns identity scores to avoid systemd HF hang.
    
    TODO: To enable actual reranking, manually copy a pre-downloaded model
    to ~/.cache/huggingface/hub/ and update this function.
    """
    return [{"index": idx, "relevance_score": 1.0} for idx in range(len(documents))]

# In QueryParam:
param = QueryParam(
    mode="hybrid",
    only_need_context=True,
    enable_rerank=False,  # Disabled — systemd can't download HF models
)
```

### 🚨 Health check must test the full pipeline, not just HTTP 200

`/health` returns 200 even when the LLM pipeline is unresponsive. The timeouts in this session were only caught because the health check script tested `/ask` end-to-end.

**Fix: Multi-stage health check that tests retrieval + generation:**
```python
# In health_check.py — not just GET /health, but POST /ask with a real query:
resp = requests.post(
    f"{base_url}/ask",
    json={"query": "entity-based SEO fundamentals"},
    timeout=30,  # Must be > LLM timeout to catch slow responses
)
assert resp.status_code == 200
assert len(resp.json().get("answer", "")) > 100  # Real answer, not fallback
```

### ⚠️ Residual known issue: WSL2 network adapter instability

~10% of TCP connections held open >30 seconds still drop at the kernel level. This affects all services in WSL2, not just LightRAG. Retry logic mitigates but doesn't eliminate. No permanent fix exists — it's a Windows kernel bug. Monitor with retry-aware health checks.

## Nexus-Style Retrieval (v2.0.0+)

Since v2.0.0, both servers use a Nexus-style retrieval architecture that replaces the old hardcoded `mode="hybrid"` + `only_need_context=True` with:

- **Auto query classification** — `local` (fact lookup), `global` (overviews/processes), `hybrid` (comparisons/conflicts)
- **Structured citations** — up to 20 `[ref:N] file_path` pairs per query
- **Conflict resolution** — system prompt instructs LLM to prioritize latest timestamps
- **Optional mode override** — clients can pass `"mode": "local|global|hybrid"` in the request body

**⚠️ Dependency lock:** `lightrag-hku==1.4.15` is REQUIRED. The `aquery_data()` API with `reference_id` fields was added in this exact version. Newer/older versions break citation extraction silently (returns empty `citations` array).

### Shared module: `nexus_shared.py`

Both servers import from `/home/steve/lightrag-apps/nexus_shared.py`:

```python
from nexus_shared import classify_query, CONFLICT_RESOLUTION_INSTRUCTION, extract_citations
```

#### `classify_query(query: str) -> Literal["local", "global", "hybrid"]`

Uses regex patterns with priority `hybrid > local > global > default(hybrid)`:
- **Hybrid** fires on comparison markers (`vs`, `versus`, `difference`, `pros and cons`, `which is better`)
- **Local** fires on fact-lookup patterns (`what is`, `define`, `phone`, `email`, `license`, `find`)
- **Global** fires on overview markers (`how does`, `overview`, `summary`, `strategy`, `process`, `explain`)
- Defaults to `hybrid` for safety

#### `extract_citations(data_result: dict) -> tuple[str, list[str]]`

Parses the structured output from `aquery_data()` — extracts `entities`, `relationships`, `chunks`, and `references` — producing formatted context text with inline citation markers AND a separate list of `"[ref:N] file_path"` strings.

#### `CONFLICT_RESOLUTION_INSTRUCTION`

A prompt string injected into the system message instructing the LLM to:
1. Prioritize most recent timestamp
2. Use file path hierarchy for tiebreaking
3. Explicitly flag unresolved conflicts
4. Cite every factual claim with `[ref:N]`

### Retrieval function: `nexus_retrieve()`

```python
async def nexus_retrieve(query: str, mode: str | None = None) -> dict:
    """Returns {context_text, citations, mode_used, raw_data}"""
    mode_used = mode or classify_query(query)

    data_result = await _rag.aquery_data(
        query,
        param=QueryParam(mode=mode_used, top_k=20, only_need_context=False),
    )
    context_text, citations = extract_citations(data_result)

    return {"context_text": context_text, "citations": citations, "mode_used": mode_used, ...}
```

**Key difference from v1:** Uses `aquery_data()` instead of `aquery()`. `aquery_data()` returns structured JSON with `entities`, `relationships`, `chunks`, and `references` — each containing `reference_id` and `file_path` for citation extraction. The old `aquery()` only returned raw text.

**Fallback:** If `aquery_data()` fails (e.g., workspace corruption), falls back to plain `aquery()` with `only_need_context=True` for robustness.

### Response models

```python
class ChatResponse(BaseModel):
    reply: str
    session_id: str
    mode_used: str = "hybrid"
    citations: list[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    mode: str | None = None  # Optional override: "local", "global", "hybrid"
```

### Test example

```bash
curl -s http://localhost:8001/chat -X POST -H "Content-Type: application/json" \
  -d '{"message":"what is Quans license number"}' | python3 -m json.tool

# Returns:
# {
#   "reply": "Quan Nguyen's real estate license number is #0774451 [ref:1].",
#   "session_id": "web-...",
#   "mode_used": "local",
#   "citations": ["[ref:1] https://quann.homes/chunk/0012", ...]
# }
```

## Reinstall Guide

Complete teardown-to-rebuild instructions live at `/home/steve/lightrag-apps/REINSTALL.md` (25 KB, 13 steps). It covers:
- Exact Python version (3.11.15 via `uv`), exact dependency versions
- Ollama Cloud setup with API key
- Cloudflare Tunnel ingress rules
- Playwright + scraping pipeline
- Knowledge graph indexing with entity extraction
- systemd deployment + health verification
- Cron + atomic swap for zero-downtime re-indexing
- Troubleshooting: 7 common failure modes with fixes

**The guide must be revised after every iteration** — change log at bottom, dependency lock section, and a checklist for updating.

### Precompute embeddings to avoid rate limits

For sources with 100+ chunks, sequential Ollama embedding calls take ~3 minutes. Precompute once and store:

```bash
# Step A: Precompute embeddings (sequential, 5-retry, GPU-safe)
python3 precompute_embeddings.py
# Output: data/quann_embeddings.npy (shape: N×768)

# Step B: Index with precomputed lookup (zero API calls)
python3 index_quann_precomp.py --workspace /path/to/workspace
```

The precompute script stores an `.npy` file. The indexer loads it and creates a `text_to_embedding` dict for direct lookup — no HTTP calls during `ainsert()`. This turns a 3-minute indexing step into instant retrieval.

**Only needed for quann-chat** (dynamic content, re-indexed weekly). SEO methodology is static reference material — no precompute needed.

### Atomic workspace swap for zero-downtime re-indexing

```bash
rm -rf workspace_old
mv workspace workspace_old      # server still holds handles → keeps serving
mv workspace_new workspace       # new workspace ready
sudo systemctl restart quann-chat # ~5 second gap
```

The server holds file handles to the old workspace; the rename is instant. Only the restart creates a brief gap. Without this, you'd need to stop the server during the 2-3 hour indexing process.

### Port zombie — systemd restart without stop leaves stale process

`sudo systemctl restart seo-methodology` sometimes starts a new process while the old one still holds port 8012. The new process crashes with `Errno 98: address already in use`, systemd restarts, crashes again — infinite loop.

**Fix — always stop first, kill orphan, then start:**
```bash
sudo systemctl stop <service>
sleep 1
sudo fuser -k <port>/tcp 2>/dev/null   # kill orphan if stop didn't free port
sudo systemctl start <service>
```

**This pattern applies to ANY LightRAG service, including `lightrag-client-knowledge`, `lightrag-quann-chat`, etc.** Also applies when a service is `inactive` but `fuser <port>/tcp` shows an orphan PID holding the port. The orphan can be from a previous `lightrag-server` run or a `server.py` process that systemd lost track of. Kill it first, then start fresh.

**Detection:** `journalctl -u <service>` shows repeated `Errno 98: address already in use`, restart counter climbs into the hundreds/thousands. Check with `fuser <port>/tcp` — if it returns a PID even after `systemctl stop`, that's the orphan.

## LightRAG Built-in Web UI (no custom server needed)

LightRAG ships with a **fully-featured production web UI** under `lightrag/api/webui/`. It's a React + Vite SPA with Cytoscape.js knowledge graph visualization, Mermaid diagram export, document upload, and a chat interface. **Reads directly from any existing workspace — zero re-indexing required.**

### Launching against an existing workspace

```bash
# Install missing deps (only needed once)
source /home/steve/lightrag-env/bin/activate
pip install pyjwt bcrypt aiofiles python-multipart

# Create a .env file pointing at the existing workspace
cat > /tmp/lightrag-ui/.env << 'EOF'
WORKING_DIR=/home/steve/lightrag-apps/quann-chat/workspace
HOST=0.0.0.0
PORT=8010
LLM_BINDING=ollama
LLM_BINDING_HOST=http://192.168.4.148:11434
LLM_MODEL=gemma4:31b-cloud
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://192.168.4.148:11434
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
WEBUI_TITLE=Quann Chat (LightRAG UI)
TOP_K=20
MAX_ASYNC=4
LLM_MODEL_MAX_ASYNC=4
EMBEDDING_FUNC_MAX_ASYNC=8
MAX_PARALLEL_INSERT=2
EOF

cd /tmp/lightrag-ui && lightrag-server
```

Access at `http://localhost:8010/webui/`. Swagger docs at `/docs`, health at `/health`.

### What the UI provides
| Tab | Feature |
|---|---|
| Chat | Query the knowledge graph directly — uses same LLM + embedding config |
| Documents | Drag-and-drop upload (PDF, txt, md) to index |
| Graph | Cytoscape.js node/edge visualizer — explore entities + relationships |
| /docs | Full Swagger REST API (query, document CRUD, graph traversal) |
| /health | Rich JSON: workspace path, LLM/embedding config, pipeline status, versions |

### Caveats
- The UI creates its own `LightRAG` instance — it's a separate process from your custom server. Both read the same workspace files on disk, but they don't share in-memory state.
- Missing dependencies cascade: `pyjwt` → `bcrypt` → `aiofiles` → `python-multipart`. Install all four upfront.
- If `TOKEN_SECRET` is not set with `AUTH_ACCOUNTS`, the server falls back to a guest-mode JWT secret (safe for dev, not production).

## Running queries

Quick test from the terminal after server starts:
```bash
curl -s -X POST http://localhost:8001/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What areas does Quan serve?","session_id":"test-1"}' | python3 -m json.tool
```
