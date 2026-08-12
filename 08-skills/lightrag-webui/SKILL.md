---
name: lightrag-webui
description: Launch LightRAG's built-in Web UI against an existing knowledge graph workspace. Covers dependency installation, .env configuration, embedding model matching, and diagnostic steps.
category: integrations
---

# LightRAG Built-in Web UI Launcher

LightRAG ships with a full production web dashboard (React + Vite, chat, knowledge graph visualizer, document upload, API docs) — accessible via the `lightrag-server` CLI.

## Trigger conditions
- "Launch LightRAG UI"
- "Open the LightRAG dashboard"
- "lightrag webui"
- Any mention of LightRAG + UI/web interface/dashboard

## Prerequisites
- LightRAG installed in venv (version >= 1.4.15)
- Existing LightRAG workspace with indexed data (workspace directory with `.json` + `.graphml` files)

## Step 1: Install missing dependencies

The `lightrag-server` CLI pulls in auth and file-handling deps that may not be in the venv:

```bash
source <venv>/bin/activate
pip install pyjwt bcrypt aiofiles python-multipart
```

## Step 2: Create .env in a working directory

Create a `.env` pointing at the **existing** workspace. **CRITICAL**: match the embedding model to whatever was used to index the data.

```env
WORKING_DIR=/path/to/existing/workspace
HOST=0.0.0.0
PORT=8010

LLM_BINDING=ollama
LLM_BINDING_HOST=http://<ollama-host>:11434
LLM_MODEL=<same-model-as-existing-server>

EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://<ollama-host>:11434
EMBEDDING_MODEL=<SAME-AS-INDEXED>    # ← MUST match original
EMBEDDING_DIM=768

WEBUI_TITLE=<Name>
TOP_K=20
```

## Step 3: Pull embedding model on Ollama host

The embedding model must be pulled on the Ollama server:

```bash
curl -s -X POST http://<ollama-host>:11434/api/pull \
  -d '{"model": "<embed-model>", "stream": false}'
```

## Step 4: Launch

```bash
cd /tmp/lightrag-ui-test   # directory containing .env
source <venv>/bin/activate
lightrag-server
```

Verify: `curl http://localhost:8010/health` should return `{"status":"healthy"}`.

## Pitfalls

### PITFALL 1: Embedding model mismatch — silent zero results
The most common failure. If the workspace was indexed with `nomic-embed-text-v2-moe` but `.env` says `nomic-embed-text`, retrieval returns `"No relevant context found"` with **no error**. Same embedding dimension (768) means no dimension mismatch error — just a completely different vector space producing zero similarity matches.

**Fix**: Check what embedding model the indexing pipeline used, and set `EMBEDDING_MODEL` to the **exact same** model name.

### PITFALL 2: ModuleNotFoundError cascade
`lightrag-server` imports the full API module tree on startup. Missing deps fail one at a time:
- `pyjwt` → auth module
- `bcrypt` → password hashing
- `aiofiles` → document upload routes
- `python-multipart` → form data handling

Install all four at once to avoid repeated restarts.

### PITFALL 3: Stale notifications from prior failed launches
When launching via `background=true` with `watch_patterns`, failed attempts generate delayed notifications. The running server's confirmation (`ss -tlnp | grep <port>`) is the authoritative source — ignore old errors from prior PIDs.

## Verification

```bash
# Health check
curl -s http://localhost:8010/health | python3 -m json.tool

# Test query
curl -s -X POST http://localhost:8010/query \
  -H 'Content-Type: application/json' \
  -d '{"query": "test query", "mode": "mix"}' | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(f'Response: {d[\"response\"][:300]}')
print(f'References: {len(d[\"references\"])}')
"
```

## Unified Multi-Notebook Proxy (via Nexus)

For exposing LightRAG UIs for **multiple notebooks** through `rag.quann.homes` without new DNS records, mount them as sub-paths via the Nexus FastAPI server. **Do NOT use a separate middleman proxy** (like `lightrag_unified_ui.py` on 8010) — it adds complexity and hangs. Nexus proxies directly to each `lightrag-server` instance.

```
Internet → Cloudflare Tunnel → Nexus (:8001) → /explore       → Landing page (served by Nexus)
                                              → /chat          → Chat endpoint
                                              → /ui/quann-chat/webui/*        → :8011
                                              → /ui/seo-methodology/webui/*   → :8012
                                              → /graph/*    ─┐
                                              → /documents/* ─┤ root-relative API calls
                                              → /query       ─┘ (routed via cookie)
```

### Setup
1. Install deps: `pip install pyjwt bcrypt aiofiles python-multipart httpx`
2. Create `.env` files for each notebook's LightRAG instance — each on its own port (8011, 8012, …)
3. Create **systemd services** for each `lightrag-server` backend so they survive reboots:
   ```ini
   # /etc/systemd/system/lightrag-<nbname>.service
   [Unit]
   Description=LightRAG WebUI for <nbname>
   After=network.target

   [Service]
   Type=simple
   User=steve
   WorkingDirectory=/tmp/lightrag-ui-envs/<nbname>
   EnvironmentFile=/tmp/lightrag-ui-envs/<nbname>/.env
   ExecStart=/home/steve/lightrag-env/bin/lightrag-server
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```
   Then: `sudo systemctl enable --now lightrag-<nbname>.service`
4. Add proxy routes in `nexus_server.py` for `/ui/{nb}/webui/` sub-paths (see `nexus-subpath-proxy` skill). Also add a catch-all route (`/{path:path}`) that handles root-relative API calls like `/graph/label/popular`.
5. Restart Nexus: `sudo systemctl restart nexus-server`
6. **No DNS changes needed** — uses existing `rag.quann.homes` domain

### CRITICAL: Cookie-based notebook routing

LightRAG's SPA makes **root-relative API calls** (`/graph/label/popular`, `/documents/status_counts`, `/query`) that lose the notebook prefix (e.g., `/ui/quann-chat/`). The `Referer` header can't be relied upon because the SPA changes the browser URL during client-side navigation.

**Fix**: Set a `lightrag_nb` cookie on every proxied response, then use it to detect the notebook:
```python
# In proxy function — set cookie on every response:
response.set_cookie(
    key="lightrag_nb",
    value=notebook_name,  # "quann-chat" or "seo-methodology"
    max_age=86400,
    path="/",
    samesite="lax"
)

# Notebook detection (fallback chain):
def _detect_notebook(request):
    # 1. Cookie (survives SPA navigation)
    nb = request.cookies.get("lightrag_nb")
    if nb: return nb
    # 2. URL path (/ui/{nb}/...)
    path = request.url.path
    m = re.match(r"^/ui/([^/]+)", path)
    if m: return m.group(1)
    # 3. Referer header (initial page load)
    ref = request.headers.get("referer", "")
    m = re.search(r"/ui/([^/]+)/webui", ref)
    if m: return m.group(1)
    return None
```

The cookie must be set:
- On the redirect from `/ui/{nb}/webui` → `/ui/{nb}/webui/`
- On all proxied responses (HTML, JS, CSS, API JSON)

### CRITICAL: Asset path rewriting + API routing

The React dashboard generates HTML with **root-relative asset paths**:
```html
<script src="/webui/assets/index.js"></script>
<link href="/webui/assets/index.css">
<link rel="icon" href="favicon.png">
```

When loaded at `rag.quann.homes/ui/quann-chat/webui/`, the browser resolves these as `rag.quann.homes/webui/assets/...` — which **doesn't route through the proxy**. Result: blank white page, JS never loads.

The proxy MUST rewrite these in HTML responses:
```python
html = html.replace('"/webui/', f'"/ui/{notebook_name}/webui/')
html = html.replace("'/webui/", f"'/ui/{notebook_name}/webui/")
html = html.replace('href="favicon.png"', f'href="/ui/{notebook_name}/webui/favicon.png"')
```

Additionally, root-relative API calls like `/graph/label/popular` must be routed to the correct backend. These calls come with the `lightrag_nb` cookie intact, so the catch-all proxy route reads the cookie and forwards to the right port.

### PITFALL 4: Zombie processes cause silent crash loops (ports "already in use")

When `lightrag-server` is run as a systemd service with `Restart=on-failure`, a previous instance may leave a zombie child process holding the port. Each restart attempt fails with `[Errno 98] address already in use`, and systemd retries indefinitely — creating a silent crash loop. The service shows as `active` for a few seconds between crashes, and `systemctl status` appears normal between restarts.

**Symptoms in the browser**: The WebUI loads (HTML/JS served by the proxy), green "Connected" indicator appears, but the graph shows "Empty(Try Reload Again)" and no API data populates. This happens because the backend is dead despite the proxy being healthy.

**Diagnose**:
```bash
# Check restart count — anything above 10-20 is abnormal:
systemctl show lightrag-<nb>.service -p NRestarts
# e.g., NRestarts=366 or NRestarts=376

# Find what's holding the port:
sudo ss -tlnp | grep <port>
# e.g., "lightrag-server,pid=63438,fd=8" — a zombie from a prior launch
```

**Fix** — kill zombies and restart:
```bash
# Kill zombie processes holding the ports
for port in 8011 8012; do
  pid=$(sudo lsof -ti:$port 2>/dev/null | head -1)
  [ -n "$pid" ] && sudo kill -9 $pid
  sleep 1
done

# Verify ports are free:
sudo ss -tlnp | grep -E "8011|8012" || echo "Ports are free!"

# Restart cleanly:
sudo systemctl restart lightrag-quann-chat lightrag-seo-methodology
```

**Prevention**: The `lightrag-server` process can spawn async subprocesses for embeddings that outlive the parent. Without `KillMode=mixed` in the systemd unit, these become zombies. Consider adding:
```ini
[Service]
KillMode=mixed
TimeoutStopSec=10
```

### PITFALL 6: URL-encoded query params break string-based matching

When intercepting and rewriting specific query parameters (like `label=*`), **string matching on the raw URL will miss what the browser actually sends**. JavaScript's `encodeURIComponent('*')` produces `%2A`, and `URLSearchParams` or `fetch()` will send `label=%2A` — not the literal `label=*`.

**Symptoms**: The label rewrite works in `curl` tests (which send literal `*`) but fails in real browsers. The graph shows the full dataset (or empty) instead of the filtered label.

**Fix**: Use proper query parsing, not string matching:
```python
from urllib.parse import parse_qs, urlencode

parsed = parse_qs(request.url.query)
if parsed.get("label") == ["*"]:  # parse_qs auto-decodes %2A → *
    # Rewrite to top popular label
    label = _top_labels.get(notebook_name, "DEFAULT")
    new_query = dict(parsed)
    new_query["label"] = [label]
    return RedirectResponse(url=f"{request.url.path}?{urlencode(new_query, doseq=True)}")
```

**Verify**: Test BOTH forms:
```bash
curl -s "https://rag.quann.homes/graphs?label=*&max_depth=2" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['nodes']))"
curl -s "https://rag.quann.homes/graphs?label=%2A&max_depth=2" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['nodes']))"
# Both must return the same filtered count (not the full dataset)
```

### PITFALL 5: SPA navigation breaks Referer-based routing

The LightRAG WebUI is a React SPA that uses client-side routing. When the user clicks from the chat page to the graph explorer, the browser URL changes from `…/ui/quann-chat/webui/` to `…/graph`. The `Referer` header no longer contains the notebook name → all API calls 404 → "Nodes are still empty" in the UI.

**Fix**: Use cookies (see above). The cookie persists across all client-side navigation. Test with:
```bash
# Simulate SPA navigation — cookie should still route correctly
curl -s -b "lightrag_nb=quann-chat" https://rag.quann.homes/graph/label/popular | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
# → 300 (or whatever entity count)
```

## Document lifecycle & programmatic ingestion

Documents flow through a state machine:

```
/documents/text  →  "pending"  →  /documents/scan  →  "processing"  →  "processed"
  (POST insert)     (stored raw)   (batch trigger)     (LLM extracting)    (entities in graph)
```

| Endpoint | Method | Body / Purpose |
|---|---|---|
| `/documents/text` | POST | `{"text":"...","url":"..."}` — inserts raw text. URL becomes `file_path`. Returns `track_id`. |
| `/documents/scan` | POST | Triggers batch processing of all pending docs. Returns `track_id`. |
| `/documents/status_counts` | GET | `{"pending": N, "processing": N, "processed": N, "failed": N}` |

**CRITICAL for incremental updates**: Always use the **real page URL** as the `url`/`file_path` — e.g., `https://example.com/page` not `/chunk/0003`. Without real URLs, you can't map sitemap entries back to existing chunks, making incremental updates impossible. See `lightrag-sitemap-ingestion` skill for the full pipeline.

### PITFALL 7: Interrupted ingestion leaves docs "pending" forever

If a `lightrag-server` process crashes while `/documents/scan` is running, newly inserted documents remain in "pending" state. On restart, the scan does NOT auto-resume — someone must manually trigger `/documents/scan` again.

**Diagnose**: `curl http://127.0.0.1:8012/documents/status_counts` — if `pending` is high and `processed` is low, a prior scan was interrupted.

**Fix**: `curl -X POST http://127.0.0.1:8012/documents/scan` and wait. Each pending doc needs an LLM call; ~140 docs ≈ 20-40 min with deepseek-v4-pro.

### PITFALL 8: KG visualizer overloads on large graphs — and hardcoded fallback labels return empty

When the SPA initializes the graph, it calls `GET /graphs?label=*` to fetch all nodes. With 800+ nodes and 900+ edges, Sigma.js on a mobile phone crashes silently — the graph area shows "Empty(Try Reload Again)" despite correct API routing and healthy backends.

Additionally, the label dropdown exposes `entity`, `relationship`, `document` (and sometimes `concept`). These are **NOT real node labels** from the knowledge graph. They come from an SPA fallback path — when `/graph/label/popular` temporarily fails, the JavaScript falls back to hardcoded LightRAG element types:

```js
// In the minified SPA bundle (index-Dutxwtl1.js):
MM.initializeWithDefaults(["entity","relationship","document"])
```

Selecting these sends `GET /graphs?label=entity` which returns **0 nodes** because no actual node in the graph has the label `"entity"`. The user sees an empty graph even though data exists.

**Fix**: Extend the Nexus proxy's label interception to cover ALL hardcoded fallback labels. Intercept `label=*`, `entity`, `relationship`, `document`, and `concept` and substitute with the most popular label (cached from `/graph/label/popular`).

```python
# Global label cache
_top_labels: dict[str, str] = {}

async def _get_top_label(nb_name: str) -> str:
    """Fetch top label from backend, cache per notebook."""
    if nb_name not in _top_labels:
        r = await httpx_get(f"http://{backend}/graph/label/popular?limit=1")
        if r.is_success:
            labels = r.json()
            if labels:
                _top_labels[nb_name] = labels[0]
    return _top_labels.get(nb_name, "")

# In catch-all proxy, before forwarding:
from urllib.parse import parse_qs, urlencode
parsed = parse_qs(request.url.query)
if parsed.get("label") == ["*"]:  # parse_qs handles %2A → *
    top = _top_labels.get(notebook_name, "")
    if top:
        new_query = dict(parsed)
        new_query["label"] = [top]
        # Rebuild URL with substituted label

# The final fix — catch ALL hardcoded SPA fallback labels:
if label_val in ("*", "entity", "relationship", "document", "concept"):
    top = await _get_top_label(nb)
    if top:
        params["label"] = [top]
        query = urllib.parse.urlencode(params, doseq=True)
```

Real labels from the graph (e.g., `Texas`, `Katy`, `Mortgage`) pass through unchanged — only the known-bad defaults get rewritten.

## Key endpoints (LightRAG built-in Web UI)
| Path | What |
|---|---|
| `/webui/` | React chat dashboard + KG visualizer |
| `/docs` | Swagger API docs |
| `/health` | JSON health check |
| `/query` | POST `{"query":"...", "mode":"mix"}` |
| `/graph/label/popular` | Entity labels (used by KG visualizer) |
| `/documents/status_counts` | Document counts per status |
| `/documents/text` | POST — programmatic text insertion |

## Key endpoints (Nexus proxy)
| Path | What |
|---|---|
| `/explore` | Landing page — cards for each notebook |
| `/ui/{notebook}/webui/` | Proxied LightRAG UI for that notebook |
| `/{path:path}` | Catch-all — routes root-relative API calls via `lightrag_nb` cookie
