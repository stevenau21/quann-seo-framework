---
name: lightrag-sitemap-ingestion
description: Incremental ingestion from sitemaps into LightRAG — fetch sitemap, detect changes via lastmod, insert only changed pages, trigger processing. Covers document lifecycle and URL tracking requirements.
---

# LightRAG Sitemap Ingestion

## When to use
Any time you're ingesting website content into LightRAG via sitemap, especially when incremental updates matter (avoid re-processing unchanged pages).

## LightRAG document lifecycle

Documents flow through four states:

```
/content/text  →  "pending"  →  /documents/scan  →  "processing"  →  "processed"
  (insert)         (stored)       (batch trigger)      (LLM extracting)    (entities in graph)
```

**Key endpoints on the LightRAG WebUI backend** (e.g., port 8012):

| Endpoint | Method | Purpose |
|---|---|---|
| `/documents/text` | POST `{"text":"...","url":"..."}` | Insert raw text. Returns `track_id`. Status becomes "pending". |
| `/documents/scan` | POST | Triggers batch processing of all pending documents. Returns `track_id`. |
| `/documents/status_counts` | GET | Shows how many docs in each state. |

## CRITICAL: file_path = real page URL

When inserting via the WebUI API, the `track_id` is generated server-side, and the document's `file_path` comes from the `url` field in the request. **Always use the real page URL as the file_path.** Example:

```python
# CORRECT
requests.post("http://127.0.0.1:8012/documents/text", json={
    "text": page_content,
    "url": "https://holisticseo.digital/theoretical-seo/knowledge-panel/"
})

# WRONG — fake URLs make incremental updates impossible
requests.post("http://127.0.0.1:8012/documents/text", json={
    "text": page_content,
    "url": "/chunk/0030"  # Can't map sitemap entries back to this
})
```

Without real URLs, incremental updates can't work because you can't map "this sitemap entry changed" → "delete these existing chunks."

## Incremental sitemap sync architecture

### Change detection via sitemap lastmod

Most sitemaps include `<lastmod>` timestamps per URL:

```xml
<url>
  <loc>https://example.com/page</loc>
  <lastmod>2026-05-01</lastmod>
</url>
```

### State file format

Store a JSON file mapping URL → lastmod:

```json
{
  "https://example.com/page-a": "2026-05-01",
  "https://example.com/page-b": "2025-11-15"
}
```

### Sync algorithm

```
1. Parse sitemap.xml → {url: lastmod}
2. Load previous state from state.json
3. Diff:
   - New URL (not in state)        → insert
   - Changed URL (lastmod differs) → delete old chunks + insert new
   - Same lastmod                   → skip
   - Deleted URL (in state, not sitemap) → delete chunks
4. Save new state to state.json
5. If any inserts/deletes happened → POST /documents/scan
```

### Why this is cheap

- Typical day with no changes: **3 seconds** (fetch sitemap → compare → exit)
- When 3 pages change: only those 3 are fetched and processed
- Each page is independent — processing page A does not touch page B's entities

## Ingestion script structure

```python
import requests, json, re, time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

SITEMAP_INDEX = "https://example.com/sitemap_index.xml"
BACKEND = "http://127.0.0.1:8012"
STATE_FILE = "sitemap_state.json"

def parse_sitemaps(index_url):
    """Parse sitemap index and all sub-sitemaps into {url: lastmod}"""
    ...

def load_state():
    try: return json.load(open(STATE_FILE))
    except FileNotFoundError: return {}

def save_state(state):
    json.dump(state, open(STATE_FILE, 'w'), indent=2)

def scrape_page(url):
    """Fetch URL, extract text content"""
    html = requests.get(url, timeout=15).text
    soup = BeautifulSoup(html, 'html.parser')
    # Remove nav, footer, scripts, etc.
    for tag in soup(['nav','footer','script','style','header']):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)

def insert_text(url, content):
    r = requests.post(f"{BACKEND}/documents/text", json={
        "text": content,
        "url": url
    })
    return r.json().get("track_id")

def trigger_scan():
    return requests.post(f"{BACKEND}/documents/scan").json()

# Main sync loop
def sync():
    current = parse_sitemaps(SITEMAP_INDEX)
    previous = load_state()

    changed = 0
    for url, lastmod in current.items():
        if url not in previous or previous[url] != lastmod:
            content = scrape_page(url)
            insert_text(url, content)
            changed += 1
            time.sleep(0.5)  # polite scraping

    if changed > 0:
        trigger_scan()
        print(f"Triggered scan for {changed} changed pages")

    save_state(current)
```

## Batched ingestion pattern (CRITICAL)

**Never insert all pages then scan once.** For large sites (200+ pages), this overwhelms the backend — it tries to process every document through the LLM simultaneously, memory balloons, and the service crashes. Instead, use **batches of 5**:

```python
BATCH_SIZE = 5

for batch_start in range(0, len(urls), BATCH_SIZE):
    batch = urls[batch_start:batch_start + BATCH_SIZE]
    for url in batch:
        content = extract_content(url)
        insert_text(content, url)
    trigger_scan()  # Scan after each batch
    # Wait for processing to complete before next batch
```

Why 5? The backend processes ~2 documents concurrently. A batch of 5 keeps the pipeline fed (5 pending → 2 processing → 3 processed in ~2 min) without overwhelming memory.

## Backend stability prerequisites

Before ANY ingestion (full or incremental), verify the backend is healthy:

```bash
# Check for crash loops — if > 10, backend is unstable
sudo systemctl show lightrag-<notebook> -p NRestarts
# Fix crash loops before ingesting or extraction will silently fail

# Check for zombie processes blocking ports  
ss -tlnp | grep -E "8011|8012"
sudo kill -9 <zombie_pid>   # Force kill if needed

# Verify health
curl http://127.0.0.1:8012/health  # Should return {"healthy": true}
```

**Stopping the backend for workspace reset:** LightRAG can hang on `systemctl stop`. Use:

```bash
sudo systemctl stop lightrag-<notebook>
sleep 5
# If still running:
sudo systemctl kill lightrag-<notebook>  # Send SIGKILL
sudo systemctl reset-failed lightrag-<notebook>
```

## WSL2 → Ollama connection prerequisite

If Ollama runs on the Windows host and the ingestion backend is in WSL2, **apply TCP keepalive before any ingestion**. WSL2's virtual switch drops idle TCP connections after ~30 seconds, and LLM entity extraction calls take 15-60 seconds — causing silent extraction failures (0 docs processed, all stuck in "pending").

```bash
sudo sysctl -w net.ipv4.tcp_keepalive_time=10
sudo sysctl -w net.ipv4.tcp_keepalive_intvl=5
sudo sysctl -w net.ipv4.tcp_keepalive_probes=3
# Persist: /etc/sysctl.d/99-wsl2-keepalive.conf
```

See `wsl2-ollama-connection-fix` skill for full diagnosis and verification.

**Verify** with a long LLM call before trusting the ingestion pipeline:

```bash
curl -s "http://192.168.4.148:11434/api/generate" -d '{
  "model": "deepseek-v4-pro:cloud",
  "prompt": "Explain SEO in one paragraph.",
  "stream": false, "options": {"num_predict": 200}
}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('response','')), 'chars')"
# Must return >100 chars — if empty, extraction will fail
```

## Extraction model strategy: fast extraction → deep reasoning

For large document sets, using the same model for extraction AND queries is wasteful. Use a two-model strategy:

1. **Extraction phase**: fast model (e.g., `gemma4:31b-cloud`) — entity extraction doesn't need deep reasoning, just pattern recognition. Faster, cheaper, handles large documents without timeout issues.
2. **Reasoning/query phase**: deep model (e.g., `deepseek-v4-pro:cloud`) — complex queries benefit from stronger reasoning.

### Model switching workflow

```python
def switch_model(model: str) -> bool:
    """Switch LLM_MODEL by editing the backend's .env file."""
    env_file = "/tmp/lightrag-ui-envs/<notebook>/.env"
    with open(env_file) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.startswith("LLM_MODEL="):
            new_lines.append(f"LLM_MODEL={model}\n")
        else:
            new_lines.append(line)

    with open(env_file, "w") as f:
        f.writelines(new_lines)

    # Restart backend to pick up change
    subprocess.run(["sudo", "systemctl", "restart", f"lightrag-<notebook>"],
                   capture_output=True, timeout=30)
    time.sleep(8)
    return True

# Usage during full ingestion:
switch_model("gemma4:31b-cloud")     # Fast for extraction
# ... ingest all pages, wait for extraction ...
switch_model("deepseek-v4-pro:cloud") # Deep for reasoning
```

### Why this matters

Large SEO documents (20-64K chars) hit `httpx.ReadTimeout` with slow models during entity extraction. Each chunk takes >180s with deepseek-v4-pro on these massive docs, exceeding the default timeout. Faster models complete extraction in 30-60s per chunk, avoiding timeouts entirely.

Also set `LLM_TIMEOUT=600` in the .env file as a safety net for the extraction phase.

### Monitoring cron for ingestion health

When running long ingestion jobs, set up a recurring cron to catch failures:

```bash
# 10-min health check cron (18 runs = 3 hours)
cronjob(action='create',
    name='Pipeline Monitor',
    schedule='*/10 * * * *',
    repeat=18,
    prompt='Check backend health, doc status, services. Report failures.')
```

Include a self-destruct cron to stop monitoring after a set period:
```bash
cronjob(action='create',
    name='Stop Monitor',
    schedule='once in 180m',
    prompt='Pause the monitor cron.')
```

```bash
# Check if extraction is actually progressing
curl -s http://127.0.0.1:8012/documents/status_counts
# If processed=0 and pending>100 for >5 minutes, retrigger:
curl -s -X POST http://127.0.0.1:8012/documents/scan

## WordPress sitemap structure

WordPress uses a **sitemap index** (not a single sitemap). The real structure for holisticseo.digital:

```
sitemap_index.xml → 8 sub-sitemaps:
  post-sitemap1.xml (200 URLs)
  post-sitemap2.xml (199 URLs)
  post-sitemap3.xml (200 URLs)
  post-sitemap4.xml (200 URLs)
  post-sitemap5.xml (8 URLs)
  page-sitemap.xml (3 URLs)
  category-sitemap.xml (8 URLs)
  author-sitemap.xml (3 URLs)
  → Total: 821 URLs
```

Parse with namespace-aware XML:
```python
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
root = ET.fromstring(resp.text)
urls = [(el.find("sm:loc", ns).text, el.find("sm:lastmod", ns).text)
        for el in root.findall("sm:url", ns)]
```

## Content extraction: Docling (GPU) vs BeautifulSoup

**PREFER DOCLING** for production ingestion. BeautifulSoup tag-stripping produces noisy, unstructured text that degrades entity extraction quality. Docling provides layout-aware parsing (headings, paragraphs, tables, lists) with GPU acceleration.

### Docling setup

```bash
# Install in the LightRAG environment
/home/steve/lightrag-env/bin/pip install docling

# IMPORTANT: docling may upgrade torch → breaks CUDA. Pin torch back:
/home/steve/lightrag-env/bin/pip install torch==2.5.1+cu121 \
  --extra-index-url https://download.pytorch.org/whl/cu121
/home/steve/lightrag-env/bin/pip install torchvision==0.20.1+cu121 \
  --extra-index-url https://download.pytorch.org/whl/cu121
```

Verify GPU is working after install:
```bash
/home/steve/lightrag-env/bin/python -c "
import torch; from docling.document_converter import DocumentConverter
print(f'CUDA: {torch.cuda.is_available()} GPU: {torch.cuda.get_device_name(0)}')
converter = DocumentConverter(); print('Docling + CUDA: READY')
"
```

### Docling extraction function

```python
from docling.document_converter import DocumentConverter

_converter = None

def get_converter():
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter

def extract_content_docling(url: str, html: str) -> str | None:
    """Extract clean markdown via Docling (GPU-accelerated)."""
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
            f.write(html)
            temp_path = f.name

        result = get_converter().convert(temp_path)
        os.unlink(temp_path)
        return result.document.export_to_markdown().strip()
    except Exception as e:
        print(f"  ⚠ Docling failed: {e}")
        return None
```

**Why Docling**: BeautifulSoup text extraction loses structure (headings become flat text, tables become gibberish). Docling preserves semantic structure as markdown, which LightRAG's entity extraction uses to produce higher-quality knowledge graphs.

### Fallback: BeautifulSoup (legacy)

If Docling is unavailable, fall back to the BS4 approach below. But the quality difference is significant — Docling produces clean markdown while BS4 produces noisy flat text.

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
for tag in soup(["script", "style", "nav", "footer", "header",
                  "aside", "noscript", "iframe", "form"]):
    tag.decompose()
for cls in ["sidebar", "comments-area", "widget-area", "site-footer",
             "site-header", "main-navigation", "comment-list"]:
    for el in soup.find_all(class_=cls):
        el.decompose()

main = soup.find("main") or soup.find("article") or \
       soup.find(class_="entry-content") or soup.find(class_="post-content")
text = main.get_text(separator="\n", strip=True) if main \
       else soup.get_text(separator="\n", strip=True)
```

## Standardized Notebook Structure

After cleanup (2026-05-13), both sitemap-based notebooks use identical naming:

```
quann-chat/
├── incremental_ingest.py   ← diffs sitemap, Docling, inserts new/changed only
├── ingest_state.json       ← {url: {lastmod, ingested_at}}
├── index_quann.py          ← kept for manual full rebuilds (ainsert directly)
├── server.py, health_check.py

seo-methodology/
├── incremental_ingest.py   ← diffs sitemap_index, Docling, inserts new/changed only
├── ingest_state.json       ← {url: {lastmod, ingested_at}}
├── server.py, health_check.py
```

**Cron schedule (both):**
| Notebook | Cron | Time | Script |
|---|---|---|---|
| quann-chat | `dc7353a6793c` | Daily 3 AM CDT | `quann-chat/incremental_ingest.py` |
| seo-methodology | `097454bcc640` | Daily 4 AM CDT | `seo-methodology/incremental_ingest.py` |

**Removed scripts** (old, broken, or superseded):
- `*/scrape_site.py` — Playwright scraper replaced by Docling in incremental_ingest
- `*/cron_scrape.sh` — destructive weekly rebuild (see anti-pattern below)
- `*/index_seo.py`, `*/index_quann_precomp.py`, `*/precompute_embeddings.py` — manual index scripts
- `seo_ingest.py` at root → moved to `seo-methodology/incremental_ingest.py`

## CRITICAL: One graph, one embedding model, forever

**Every operation on a given LightRAG workspace — insertion, entity extraction, query — MUST use the identical embedding model.** Mixing models in the same vector space (e.g., `nomic-embed-text:v1.5` and `nomic-embed-text-v2-moe`) produces vectors in incompatible coordinate systems. Vectors stored with v1.5 are unreachable by v2-moe queries — cosine similarity between different model spaces is mathematically meaningless.

**Symptoms of a mismatch:**
- Test query inside the indexing script "works" (same model used for both embed + query)
- Real queries through the service return garbage (service uses a different model)
- Graph seems healthy but retrieval quality is broken

**The rule:** Pick one model per notebook, use it everywhere. If you must change models, you MUST rebuild the entire workspace from scratch. There is no migration path.

**Current standard (as of 2026-05-13):** `nomic-embed-text-v2-moe` for all three notebooks (quann-chat, seo-methodology, client-knowledge).

## Pitfalls

- **EMBEDDING MODEL MISMATCH** — The `index_quann.py` manual rebuild script used `nomic-embed-text:v1.5` while the running service (port 8011) uses `nomic-embed-text-v2-moe`. This silently broke retrieval — stored vectors from v1.5 are in a different coordinate system than v2-moe query vectors. **Fix:** align the index script's EMBED_MODEL with the service's .env EMBEDDING_MODEL, then fully rebuild the workspace. Always verify with `grep 'EMBED_MODEL' index_*.py` vs `cat /tmp/lightrag-ui-envs/<notebook>/.env | grep EMBEDDING_MODEL`.

- **DESTRUCTIVE CRON ANTI-PATTERN** — Never combine an incremental daily cron with a full-rebuild weekly cron on the same workspace. Pattern: daily cron ingests 100+ pages over a week → weekly cron builds a fresh index into `workspace_new` from a subset of URLs → atomically swaps (`mv workspace_new workspace`) → everything the daily cron built is orphaned in `workspace_old`. The weekly cron's atomic swap knows nothing about the incremental data. **Fix:** remove the weekly cron, keep only a single incremental path per graph.
- **Playwright Chromium may not be installed** — `npx playwright install chromium` is required before Playwright scripts work. The snap Chromium is NOT usable by Playwright. If not installed, `chromium.launch()` hangs silently. Docling is preferred for content extraction anyway (GPU-accelerated, structure-preserving).
- **Document extraction: Docling > Playwright** — For the same URL, Docling produces more and higher-quality chunks than Playwright+regex (e.g., 340 vs 206 chunks from 22 pages). Docling uses layout-aware parsing; Playwright just grabs raw HTML that regex strips — losing structure, tables, and sometimes missing entire content sections.

- **Don't use fake file_paths** — once data is in LightRAG with fake URLs (e.g., `/chunk/0030`), incremental updates are impossible. You must wipe the workspace and start over. Always use the real page URL.
- **Processing takes time** — each document needs an LLM call for entity extraction. ~200 pages with deepseek-v4-pro takes 20-40 minutes. 821 pages takes 1-2 hours.
- **Backend crash loops kill ingestion** — if the backend dies 376 times during ingestion, most documents get stuck in "pending" and never extract entities. Fix stability first.
- **Scan is incremental** — triggering `/documents/scan` processes ALL current "pending" docs. If you insert more after the scan starts, trigger again.
- **Don't re-scan unnecessarily** — in incremental mode, if no pages changed, don't call scan. It wastes LLM calls and time.
- **Rate-limit scraping** — add sleeps between page fetches to be polite to the source server.
- **Sitemap XML parsing** — WordPress sitemaps use namespaces; parse with `{http://www.sitemaps.org/schemas/sitemap/0.9}loc` or namespace-aware ET.
- **Model switch hangs on restart** 🆕 — `systemctl restart` during active entity extraction hangs because the extraction pipeline holds open handles. Always `sudo systemctl stop` FIRST, verify it's dead (`sudo systemctl status` shows `inactive`), then `start`. If it hangs on stop for >30s, use `sudo systemctl kill lightrag-<notebook>` (SIGKILL) followed by `sudo systemctl reset-failed lightrag-<notebook>` before starting fresh.

- **403 Forbidden on sitemap fetch** 🆕 — Some servers (e.g., holisticseo.digital) block bare `urllib.request.urlopen()` calls that don't send a User-Agent header. Always use `requests.get(sitemap_url, headers={"User-Agent": "Mozilla/5.0 (compatible; ...)"})` instead. The shared `ingest_sitemap.py` now uses requests everywhere — never `urlopen()`.

- **Gleaning wastes tokens on structured content** 🆕 — LightRAG defaults `entity_extract_max_gleaning=1`, which runs a second LLM pass asking "what did I miss?" — doubling token cost per chunk. For well-structured sitemap content (blog posts, marketing pages), this is wasteful. Set `MAX_GLEANING=0` via systemd override for the `lightrag-server` CLI, or `entity_extract_max_gleaning=0` in `LightRAG()` constructor for Nexus-wrapped servers. Keep gleaning=1 only for unstructured content like conversation transcripts. Add to systemd override:
  ```
  sudo mkdir -p /etc/systemd/system/lightrag-<notebook>.service.d
  sudo tee -a /etc/systemd/system/lightrag-<notebook>.service.d/override.conf <<<'Environment=MAX_GLEANING=0'
  sudo systemctl daemon-reload && sudo systemctl restart lightrag-<notebook>
  ```
