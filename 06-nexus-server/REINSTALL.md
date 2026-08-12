# LightRAG Nexus Reinstall Guide

**Version:** 3.1.0 — Web UI Edition  
**Last Updated:** 2026-05-06  
**GitHub:** https://github.com/stevenau21/lightrag-apps (private)  
**Purpose:** Complete teardown-to-rebuild instructions for the Nexus multi-bot architecture. Follow exactly — skipping steps causes a broken RAG system.  

**Quick deploy on fresh machine:**  
```bash
git clone https://github.com/stevenau21/lightrag-apps.git
cd lightrag-apps
./scripts/setup.sh
```

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Step 1 — Install Python + Create Venv](#step-1--install-python--create-venv)
4. [Step 2 — Install Dependencies](#step-2--install-dependencies)
5. [Step 3 — Ollama Cloud Setup](#step-3--ollama-cloud-setup)
6. [Step 4 — Cloudflare Tunnel](#step-4--cloudflare-tunnel)
7. [Step 5 — Scrape + Chunk Source Content](#step-5--scrape--chunk-source-content)
8. [Step 6 — Build Knowledge Graph (Indexing)](#step-6--build-knowledge-graph-indexing)
9. [Step 7 — Deploy Servers](#step-7--deploy-servers)
10. [Step 7-B — LightRAG Built-in Web UI](#step-7-b--launch-lightrag-built-in-web-ui)
11. [Step 8 — Health Check & Verify](#step-8--health-check--verify)
12. [Step 9 — Cron + Monitoring](#step-9--cron--monitoring)
13. [Troubleshooting](#troubleshooting)
14. [File Inventory](#file-inventory)

---

## 1. Prerequisites

| Requirement | Value | Notes |
|---|---|---|
| OS | Ubuntu 22.04+ (WSL2) | Windows 11 host |
| RAM | 128 GB | Server caches graph artifacts in memory |
| CPU | Intel i9-10900K | Used for graph extraction at index time |
| GPU | GTX 1080 8GB (Windows host) | Runs `nomic-embed-text-v2-moe` embeddings |
| Disk | SSD, ~50 GB free | Workspaces are 20 MB each but grow |
| Python | 3.11.15 | Managed by `uv` — see Step 1 |
| Node.js | 18+ | Required for Playwright scrapers |
| Playwright | `npx playwright install chromium` | Headless browser for scraping |

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Windows Host                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Ollama Cloud │  │ Cloudflared  │  │ GTX 1080 (embeddings)   │  │
│  │ Port 11434   │  │ Docker       │  │                          │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────────┘  │
│         │                 │                                         │
│         │ WSL2 virtual  │ Tunnel ingress rules                    │
│         │ switch        │                                         │
│         │ (drops idle!) │                                         │
└─────────┼───────────────┼─────────────────────────────────────────┘
          │               │
          ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        WSL2 Ubuntu                                     │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    /home/steve/lightrag-apps/                     │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │
│  │  │              nexus_server.py (port 8001)                       │ │
│  │  │  ┌─────────────────────┐  ┌─────────────────────────────────┐ │ │
│  │  │  │ quann-chat (/chat)  │  │ seo-methodology (/seo)          │ │ │
│  │  │  │                     │  │                                 │ │ │
│  │  │  │ Query Classifier    │  │ Query Classifier                │ │ │
│  │  │  │ Citations (20)      │  │ Citations (20)                  │ │ │
│  │  │  │ Conflict Resolution │  │ Conflict Resolution             │ │ │
│  │  │  │ Mode: local/global/ │  │ Mode: local/global/             │ │ │
│  │  │  │      hybrid         │  │      hybrid                     │ │ │
│  │  │  │ Reranker: yes       │  │ Reranker: yes                  │ │ │
│  │  │  │ LLM: gemma4:31b     │  │ LLM: deepseek-v4-pro:cloud     │ │ │
│  │  │  │                     │  │                                 │ │ │
│  │  │  │ workspace/          │  │ workspace/                      │ │ │
│  │  │  │ (169 entities)      │  │ (from holisticseo.digital)      │ │ │
│  │  │  │ scrape_site.py      │  │ scrape_site.py                  │ │ │
│  │  │  │ index_quann*.py     │  │ index_seo.py                    │ │ │
│  │  │  │ precompute_*.py     │  │                                 │ │ │
│  │  │  │ health_check.py     │  │                                 │ │ │
│  │  │  └─────────────────────┘  └─────────────────────────────────┘ │ │
│  │  │ │ Conflict Resolution│   │    │ │ Conflict Resolution│       │ │ │
│  │  │ │ Mode: local/global/ │   │    │ │ Mode: local/global/│      │ │ │
│  │  │ │      hybrid         │   │    │ │      hybrid        │     │ │ │
│  │  │ │ + reranker (no)    │   │    │ │ + reranker (yes)   │     │ │ │
│  │  │ └───────────────┘   │    │ └───────────────┘              │ │ │
│  │  │                     │    │                                │ │ │
│  │  │ data/               │    │ data/                          │ │ │
│  │  │ workspace/          │    │ workspace/                       │ │ │
│  │  │ scrape_site.py      │    │ scrape_site.py                 │ │ │
│  │  │ index_quann.py      │    │ index_seo.py                   │ │ │
│  │  │ index_quann_        │    │                                │ │ │
│  │  │   precomp.py        │    │                                │ │ │
│  │  │ precompute_         │    │                                │ │ │
│  │  │   embeddings.py     │    │                                │ │ │
│  │  │ cron_scrape.sh      │    │ cron_scrape.sh                 │ │ │
│  │  │ health_check.py     │    │ health_check.py                │ │ │
│  │  └─────────────────────┘    └─────────────────────────────────┘ │ │
│  │                                                                    │ │
│  │  nexus_shared.py — shared across both:                             │ │
│  │    - classify_query()                                              │ │
│  │    - CONFLICT_RESOLUTION_INSTRUCTION                                │ │
│  │    - extract_citations()                                           │ │
│  │                                                                    │ │
│  │  has_changed.py — md5 diff for smart cron                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### API Flow

```
Browser → chat.quann.homes → Cloudflare Tunnel → WSL2 :8001
                                              → aquery_data() with mode selection
                                              → structured data (entities/relations/chunks)
                                              → extract_citations() → context + [ref:N]
                                              → Ollama Cloud (gemma4:31b-cloud)
                                              → reply + mode_used + citations[]
```

---

## Step 1 — Install Python + Create Venv

### 1.1 Install `uv` (Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### 1.2 Install Python 3.11.15

```bash
uv python install 3.11.15
# Verify: uv python find 3.11.15
```

### 1.3 Create virtual environment

```bash
mkdir -p /home/steve/lightrag-apps
uv venv /home/steve/lightrag-env --python 3.11.15
```

**⚠️ CRITICAL:** The venv path **must** be exactly `/home/steve/lightrag-env`. All `server.py` files and systemd units hardcode this path.

---

## Step 2 — Install Dependencies

### 2.1 Core packages

```bash
/home/steve/lightrag-env/bin/pip install -r requirements.txt
```

Or manually:

```bash
/home/steve/lightrag-env/bin/pip install \
  "lightrag-hku==1.4.15" \
  "fastapi==0.136.1" \
  "uvicorn==0.46.0" \
  "httpx==0.28.1" \
  "requests==2.33.1" \
  "sentence-transformers==5.4.1" \
  "numpy==2.4.4" \
  "torch==2.5.1+cu121" \
  "transformers==5.7.0" \
  "pyjwt==2.12.1" \
  "bcrypt==5.0.0" \
  "aiofiles==25.1.0" \
  "python-multipart==0.0.27"
```

**New dependencies** (`pyjwt`, `bcrypt`, `aiofiles`, `python-multipart`) are required by the LightRAG built-in web UI (`lightrag-server` CLI).

**⚠️ CRITICAL:** Lock `lightrag-hku==1.4.15`. The `aquery_data()` API with `reference_id` fields was added in this version. Newer/older versions may break citations.

### 2.2 Node.js + Playwright (for scrapers)

```bash
# Node 18+ must be installed
npm install -g playwright
npx playwright install chromium
```

### 2.3 Verify CUDA (for local embeddings)

```bash
# This system uses a GTX 1080 on the Windows host for embeddings
# The `torch==2.5.1+cu121` wheel works with CUDA 12.1
# Verify: python -c "import torch; print(torch.cuda.is_available())"
# Expected: True (if run from Windows host Ollama)
# WSL does NOT need GPU — embeddings happen via Ollama on Windows host
```

---

## Step 3 — Ollama Cloud Setup

### 3.1 Windows host Ollama

Install Ollama on Windows. The WSL servers connect to it via the virtual switch IP (typically `192.168.4.148`).

### 3.2 Configure Ollama Cloud API Key

Create `/home/steve/lightrag-apps/.env`:

```bash
# DO NOT COMMIT THIS FILE
# Get key from: https://ollama.com/settings/api-keys
OLLAMA_API_KEY=your_key_here
```

The indexers (`index_quann.py`, `index_seo.py`) and the servers use this key implicitly through the Ollama Cloud API. The `ollama-forwarder.py` script also uses the same endpoint.

### 3.3 Verify models are available

```bash
curl http://192.168.4.148:11434/api/tags | python3 -m json.tool
```

Expected models:
- `nomic-embed-text-v2-moe:latest` (913 MB) — **server embedding model**
- `nomic-embed-text:v1.5` (261 MB) — **indexer embedding model**
- `gemma4:31b-cloud` (0 MB, cloud) — **quann-chat LLM + indexer LLM**
- `deepseek-v4-pro:cloud` (0 MB, cloud) — **seo-methodology LLM**

### 3.4 WSL2 Connection Fix

The WSL2 virtual switch drops idle TCP connections. This is why servers use:
- **quann-chat:** `requests` with `_TCPKeepAliveAdapter` (10s idle / 5s interval / 3 probes)
- **seo-methodology:** Raw `http.client` with fresh socket per call + keepalive

**⚠️ NEVER** remove the `Connection: close` headers or the keepalive socket options. Doing so causes 90-second hangs on every second Ollama call.

---

## Step 4 — Cloudflare Tunnel

### 4.1 Docker container

```bash
docker run -d \
  --name cloudflared \
  --restart always \
  -v /mnt/c/Users/steve/n8n-deploy/data/cloudflared:/home/nonroot/.cloudflared \
  cloudflare/cloudflared:latest tunnel run --token <YOUR_TOKEN>
```

### 4.2 Config file

File: `/mnt/c/Users/steve/n8n-deploy/data/cloudflared/config.yaml`

```yaml
tunnel: n8n-tunnel
credentials-file: /home/nonroot/.cloudflared/375fb7b7-0b11-4e3f-bcba-9729cf109864.json
no-autoupdate: true
protocol: http2

ingress:
  - hostname: n8n.quann.homes
    service: http://n8n:5678
  - hostname: ollama.quann.homes
    service: http://host.docker.internal:11434
  - hostname: opencode.quann.homes
    service: http://host.docker.internal:4096
  - hostname: quanbot.quann.homes
    service: http://host.docker.internal:8000
  - hostname: dify.quann.homes
    service: http://host.docker.internal:80
  - hostname: chat.quann.homes
    service: http://host.docker.internal:8001
  - hostname: rag.quann.homes
    service: http://host.docker.internal:8001
  - service: http_status:404
```

Both `rag.quann.homes` and `chat.quann.homes` route to the same Nexus server (port 8001) — same classifier, reranker, and citation pipeline.

**⚠️ IMPORTANT:** `seo.quann.homes` is **NOT** in this config. It has never had a public ingress rule. If you need it public, add:
```yaml
  - hostname: seo.quann.homes
    service: http://host.docker.internal:8002
```

---

## Step 5 — Scrape + Chunk Source Content

### 5.1 quann-chat (App #1)

```bash
cd /home/steve/lightrag-apps/quann-chat
mkdir -p data

# Scrape quann.homes sitemap
./lightrag-env/bin/python3 scrape_site.py
# Output: data/quann_chunks.jsonl
```

The scraper uses Playwright (Node.js) to render each page, scroll for lazy content, and chunk sentences into ~800 char blocks.

### 5.2 seo-methodology (App #2)

```bash
cd /home/steve/lightrag-apps/seo-methodology
mkdir -p data

# Scrape holisticseo.digital hardcoded URLs
./lightrag-env/bin/python3 scrape_site.py
# Output: data/holisticseo_chunks.jsonl
```

---

## Step 6 — Build Knowledge Graph (Indexing)

This is the **Context Compiler** phase — runs once per document batch. The i9 CPU does entity/relationship extraction using the cloud LLM.

### 6.1 quann-chat: Precompute embeddings + index

```bash
cd /home/steve/lightrag-apps/quann-chat

# Step A: Precompute embeddings (sequential, avoids rate limits)
./lightrag-env/bin/python3 precompute_embeddings.py
# Output: data/quann_embeddings.npy (shape: N×768)

# Step B: Index into LightRAG with precomputed embeddings
./lightrag-env/bin/python3 index_quann_precomp.py
# Creates: workspace/ with all graph artifacts
```

**Why precompute?** The Ollama embedding API on a GTX 1080 handles ~1 req/sec. With 200+ chunks, sequential calls take ~3 minutes. Precomputing once avoids re-embedding on every cron run.

### 6.2 seo-methodology: Direct index (no precompute)

```bash
cd /home/steve/lightrag-apps/seo-methodology

# Index directly (embeddings computed inline)
./lightrag-env/bin/python3 index_seo.py
# Creates: workspace/ with all graph artifacts
```

### 6.3 What gets created (workspace files)

After indexing, verify these files exist:

```
workspace/
  vdb_entities.json              # Entity vector DB (~5 MB)
  vdb_relationships.json         # Relationship vector DB (~6 MB)
  vdb_chunks.json                # Chunk vector DB (~1 MB)
  graph_chunk_entity_relation.graphml  # Knowledge graph (~1 MB)
  kv_store_full_entities.json    # Entity descriptions
  kv_store_full_relations.json   # Relationship descriptions
  kv_store_llm_response_cache.json     # LLM cache (~6 MB)
  kv_store_text_chunks.json      # Chunk metadata
  kv_store_doc_status.json       # Document tracking
  kv_store_entity_chunks.json    # Entity→chunk mapping
  kv_store_relation_chunks.json  # Relation→chunk mapping
```

**⚠️ CRITICAL:** If `vdb_entities.json` is < 1 KB or missing, the graph extraction failed. The most common cause is the indexer using a model that doesn't support the `/v1/chat/completions` format. Both indexers MUST use `gemma4:31b-cloud` (or another model with function-calling support).

---

## Step 7 — Deploy Servers

### 7.1 Write systemd units

**`/etc/systemd/system/quann-chat.service`:**

```ini
[Unit]
Description=Quann Chat LightRAG Server (App #1)
After=network.target

[Service]
Type=simple
User=steve
WorkingDirectory=/home/steve/lightrag-apps/quann-chat
Environment=PATH=/home/steve/lightrag-env/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/steve/lightrag-env/bin/python3 /home/steve/lightrag-apps/quann-chat/server.py
Restart=always
RestartSec=10
StartLimitIntervalSec=0
StandardOutput=journal
StandardError=journal

NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/seo-methodology.service`:**

```ini
[Unit]
Description=SEO Methodology - LightRAG + GPU Reranker (App #2)
After=network.target

[Service]
Type=simple
User=steve
WorkingDirectory=/home/steve/lightrag-apps/seo-methodology
ExecStart=/home/steve/lightrag-env/bin/python3 /home/steve/lightrag-apps/seo-methodology/server.py
Restart=always
RestartSec=10
StartLimitIntervalSec=0
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 7.2 Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now quann-chat seo-methodology
```

### 7.3 Verify

```bash
curl -s http://localhost:8001/health | python3 -m json.tool
curl -s http://localhost:8002/health | python3 -m json.tool
```

Expected:
```json
{"status": "healthy", "service": "quann-chat", "version": "2.0.0", "rag_ready": true}
{"status": "healthy", "service": "seo-methodology", "version": "2.0.0", "rag_ready": true, "reranker_loaded": true}
```

---

## Step 7-B — Launch LightRAG Built-in Web UI

LightRAG ships with a **production React dashboard** (`lightrag-server` CLI) that shares the SAME workspace as your Nexus server — no duplicate indexing.

### What it gives you

| Feature | Description |
|---|---|
| **Chat** | Query your KG in real time through a clean UI |
| **Document Upload** | Drag-and-drop PDFs, txt, markdown to index |
| **Knowledge Graph Explorer** | Cytoscape.js — 896 nodes, 957 edges for quann-chat |
| **Mermaid Diagrams** | Auto-generated flow/sequence/ER diagrams from the KG |
| **Swagger API** | Full `/docs` for direct API access |
| **Health Dashboard** | `/health` shows workspace path, LLM config, models |

### Launch

```bash
mkdir -p /tmp/lightrag-ui && cd /tmp/lightrag-ui

cat > .env << 'EOF'
WORKING_DIR=/home/steve/lightrag-apps/quann-chat/workspace
HOST=0.0.0.0
PORT=8010
LLM_BINDING=ollama
LLM_BINDING_HOST=http://192.168.4.148:11434
LLM_MODEL=gemma4:31b-cloud
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://192.168.4.148:11434
EMBEDDING_MODEL=nomic-embed-text-v2-moe
EMBEDDING_DIM=768
WEBUI_TITLE=Quann Chat
WEBUI_DESCRIPTION=Production knowledge graph RAG
TOP_K=20
EOF

source /home/steve/lightrag-env/bin/activate
lightrag-server
```

Open `http://localhost:8010/webui/` in your browser.

**⚠️ CRITICAL:** The embedding model MUST match what was used to build the workspace. For this repo, that's `nomic-embed-text-v2-moe` (768-dim). Using `nomic-embed-text` (also 768-dim but different embedding space) will silently fail all retrieval queries with `"No relevant context found"`.

If the server exits with `ModuleNotFoundError`, install the missing dependency and try again. The required packages are in `requirements.txt`.

---

## Step 8 — Health Check & Verify

### 8.1 Quick local tests

```bash
# Local mode test (fact lookup)
curl -s http://localhost:8001/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "what is Quans phone number"}' | python3 -m json.tool

# Expected: mode_used="local", citations array with 20 entries

# Global mode test (overview)
curl -s http://localhost:8001/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "how does the home buying process work"}' | python3 -m json.tool

# Expected: mode_used="global", citations array

# Hybrid mode test (comparison)
curl -s http://localhost:8001/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Katy vs Houston for home buyers"}' | python3 -m json.tool

# Expected: mode_used="hybrid", citations array

# Mode override test
curl -s http://localhost:8001/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "what is Quans email", "mode": "global"}' | python3 -m json.tool

# Expected: mode_used="global" (forced override)
```

### 8.2 Production health check script

Run the full browser-emulation health check:

```bash
/home/steve/lightrag-env/bin/python3 /home/steve/lightrag-apps/quann-chat/health_check.py
```

This tests: CORS preflight → health endpoint → actual chat with RAG retrieval.

---

## Step 9 — Cron + Monitoring

### 9.1 Daily re-index cron (quann-chat only)

The quann-chat data changes daily (new blog posts, etc.). SEO methodology is static (reference material).

```bash
# Add to root crontab or user crontab with sudo systemctl restart permissions
0 3 * * * /home/steve/lightrag-apps/quann-chat/cron_scrape.sh >> /home/steve/lightrag-apps/quann-chat/cron.log 2>&1
```

### 9.2 What cron_scrape.sh does

```
1. Run scrape_site.py → data/quann_chunks.jsonl
2. Run has_changed.py → md5 diff check
3. If changed:
   a. Run precompute_embeddings.py → data/quann_embeddings.npy
   b. Run index_quann_precomp.py --workspace workspace_new
   c. Atomic swap: workspace → workspace_old, workspace_new → workspace
   d. systemctl restart quann-chat
4. If unchanged: exit (no restart)
```

**⚠️ CRITICAL:** The atomic swap ensures zero downtime. The server holds handles to the old workspace; the restart picks up the new one.

### 9.3 Monitoring

```bash
# Check logs
sudo journalctl -u quann-chat -f
sudo journalctl -u seo-methodology -f

# Check health
watch -n 5 'curl -s http://localhost:8001/health && echo && curl -s http://localhost:8002/health'
```

---

## Troubleshooting

### "aquery_data_failed status=None"

The `aquery_data()` call failed to return a success response. Check:
1. Is the workspace valid? (`vdb_chunks.json` > 1 KB)
2. Is `_rag.aquery_data()` using `only_need_context=False`?
3. Are there any exceptions in `journalctl -u <service>`?

### "workspace_corrupted_or_empty vdb=False"

The workspace directory exists but `vdb_chunks.json` is missing or < 1 KB. Causes:
- Indexer crashed before completing
- Wrong indexer model used (see 6.3)
- `shutil.rmtree()` wiped it during a failed re-index

**Fix:** Re-run the indexer (Step 6). If using cron, check `workspace_old` for a backup.

### SEO server crashes on startup (port 8002 already in use)

```bash
# Find and kill the zombie process
sudo fuser -k 8002/tcp
sudo systemctl restart seo-methodology
```

This happens when systemd's `RestartSec=10` isn't long enough for the old process to fully release the port.

### Ollama timeout / "Read timed out"

The WSL2 virtual switch dropped the connection. Verify:
1. TCP keepalive is configured (see 3.4)
2. `Connection: close` header is present
3. Windows host Ollama is running (`curl http://192.168.4.148:11434`)

### Reranker fails to load

```bash
# Check the snapshot exists
ls -la /home/steve/.cache/huggingface/hub/models--mixedbread-ai--mxbai-rerank-base-v1/snapshots/
# Expected: 800f24c113213a187e65bde9db00c15a2bb12738/

# If missing, download it:
python3 -c "from sentence_transformers import CrossEncoder; CrossEncoder('mixedbread-ai/mxbai-rerank-base-v1')"
```

The server falls back to no reranking if the model is missing, but retrieval quality degrades.

### Citations are empty (`citations: []`)

Two causes:
1. `aquery_data()` returned empty data — check that `entities`, `relationships`, or `chunks` exist in the response
2. `reference_id` fields are missing — this means the LightRAG version is wrong. Verify `lightrag-hku==1.4.15`.

### LLM response has no `[ref:N]` inline citations

The conflict-resolution prompt is in the system message, but the LLM may ignore it. The prompt explicitly instructs:
> "Every factual claim must cite its source using the [ref:N] format"

If the LLM consistently ignores this, the model may not support following complex system prompts well. `gemma4:31b-cloud` and `deepseek-v4-pro:cloud` both handle it correctly.

---

## File Inventory

### Source Code (all hand-written, not generated)

| File | Purpose | Lines |
|---|---|---|
| `nexus_shared.py` | Query classifier, conflict prompt, citation extractor, app factory | ~610 |
| `quann-chat/server.py` | FastAPI server v2.0.0 with Nexus retrieval (thin config) | ~54 |
| `seo-methodology/server.py` | FastAPI server v2.0.0 with reranker (thin config) | ~49 |
| `quann-chat/scrape_site.py` | Playwright scraper for quann.homes | ~143 |
| `seo-methodology/scrape_site.py` | Playwright scraper for holisticseo.digital | ~126 |
| `quann-chat/index_quann.py` | Full index with live embeddings | ~133 |
| `quann-chat/index_quann_precomp.py` | Index with precomputed embeddings | ~134 |
| `quann-chat/precompute_embeddings.py` | Sequential embedding precomputation | ~47 |
| `seo-methodology/index_seo.py` | Full index with live embeddings | ~117 |
| `has_changed.py` | MD5 diff for smart cron | ~24 |
| `quann-chat/health_check.py` | Production browser-emulation health check | ~106 |
| `quann-chat/cron_scrape.sh` | Daily scrape+index cron script | ~36 |
| `ollama-forwarder.py` | TCP forwarder (WSL2→Windows host) | ~147 |
| `widgets/widget.js` | Generic chat widget embed script | ~80 |
| `widgets/chat-iframe.html` | Generic chat widget HTML | ~120 |
| `scripts/setup.sh` | Fresh-machine deploy script | ~66 |
| `.env.example` | Config template for new deployments | ~60 |

### Data Files (generated)

| File | Size | Source |
|---|---|---|
| `quann-chat/data/quann_chunks.jsonl` | ~194 KB | scraper output |
| `quann-chat/data/quann_embeddings.npy` | ~619 KB | precompute_embeddings.py |
| `quann-chat/data/quann_chunks.md5` | 32 bytes | has_changed.py |
| `seo-methodology/data/holisticseo_chunks.jsonl` | ~143 KB | scraper output |
| `seo-methodology/data/holisticseo_chunks.md5` | 32 bytes | has_changed.py |

### Workspace Files (generated by LightRAG)

| File | Size | Purpose |
|---|---|---|
| `vdb_entities.json` | ~5 MB | Entity vector database |
| `vdb_relationships.json` | ~6 MB | Relationship vector database |
| `vdb_chunks.json` | ~1 MB | Chunk vector database |
| `graph_chunk_entity_relation.graphml` | ~1 MB | Knowledge graph (GraphML format) |
| `kv_store_full_entities.json` | ~60 KB | Full entity descriptions |
| `kv_store_full_relations.json` | ~100 KB | Full relationship descriptions |
| `kv_store_llm_response_cache.json` | ~6 MB | LLM response cache (speeds up re-queries) |
| `kv_store_text_chunks.json` | ~248 KB | Chunk text content |
| `kv_store_doc_status.json` | ~140 KB | Document ingestion status |
| `kv_store_entity_chunks.json` | ~204 KB | Entity→chunk index |
| `kv_store_relation_chunks.json` | ~240 KB | Relation→chunk index |

### System Config

| File | Purpose |
|---|---|
| `/etc/systemd/system/quann-chat.service` | systemd unit for App #1 |
| `/etc/systemd/system/seo-methodology.service` | systemd unit for App #2 |
| `/mnt/c/Users/steve/n8n-deploy/data/cloudflared/config.yaml` | Cloudflare tunnel ingress rules |

---

## Dependency Lock

These exact versions are verified working. Do not upgrade without testing.

```
lightrag-hku==1.4.15      # aquery_data() API required
fastapi==0.136.1
uvicorn==0.46.0
httpx==0.28.1
requests==2.33.1
sentence-transformers==5.4.1
numpy==2.4.4
torch==2.5.1+cu121
transformers==5.7.0
pyjwt==2.12.1             # lightrag-server CLI
bcrypt==5.0.0             # lightrag-server CLI
aiofiles==25.1.0          # lightrag-server CLI
python-multipart==0.0.27  # lightrag-server CLI
```

---

## Future Roadmap

Things tracked for future work — not yet implemented.

### Web UI for Nexus (browser-based chat + document upload)

Currently, `rag.quann.homes` exposes the Nexus chat API but has no browser interface. Visitors see "Not Found" unless they hit `POST /chat` programmatically.

**Goal:** A simple HTML chat UI served from the Nexus server itself (`GET /`). Users can:
- Type questions and see Nexus-classified responses with citations
- Upload documents (PDFs, txt, markdown) to index into the KG
- No Telegram dependency — self-contained web app

**Why it's not built yet:** The primary use case is Telegram bots. A web UI adds value only when non-Telegram users need access. Until then, the API is documented at `/docs` and works fine for integrations.

**Implementation note:** FastAPI can serve a single-page HTML app natively — no extra server needed. The Nexus server (`server.py`) just needs a `GET /` route returning an HTML template with a chat form that calls `POST /chat` via fetch. Document upload can reuse the LightRAG `lightrag-server` upload pipeline adapted to Nexus's workspace. ~50 lines of HTML + ~30 lines of Python.

---

## Change Log

| Date | Version | Change |
|---|---|---|
| 2026-05-06 | 3.2.0 | Added `rag.quann.homes` tunnel route → Nexus. Shut down bare LightRAG UI (bypassed Nexus pipeline). Added Future Roadmap section. |
| 2026-05-05 | 2.0.0 | Added query classifier, citations, conflict resolution. `aquery_data()` replaces `aquery()`. Nexus-style retrieval. |
| 2026-05-04 | 1.2.0 | Added precomputed embeddings for quann-chat indexer. MD5 diff for smart cron. |
| 2026-05-03 | 1.1.0 | Added reranker (`mxbai-rerank-base-v1`) to seo-methodology. |
| 2026-05-02 | 1.0.0 | Initial deploy. Basic `hybrid` mode, `only_need_context=True`, no citations. |

---

**To update this document after any change:**
1. Edit the **Change Log** section
2. Update the **Dependency Lock** if package versions changed
3. Update **File Inventory** if new files were added or removed
4. Verify **Step 6 — Build Knowledge Graph** still works by running the indexer on a clean workspace
5. Commit: `git add REINSTALL.md && git commit -m "docs: reinstall guide v2.0.0"`
