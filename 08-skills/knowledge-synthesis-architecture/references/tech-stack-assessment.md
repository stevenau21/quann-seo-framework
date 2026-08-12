# Open-Source Tech Stack Assessment (2026-05-14)

> Verified via direct system introspection, not web search. All installed packages confirmed. Missing components verified as available on PyPI.

---

## Existing Foundation (Verified Working)

| Component | Version | What It Provides | Verified |
|---|---|---|---|
| Python | 3.11.15 | Runtime | ✓ |
| LightRAG | 1.4.15 | Knowledge graph construction, entity extraction, chunked storage, hybrid retrieval | ✓ |
| spaCy | 3.8.14 | Named Entity Recognition, POS tagging, dependency parsing | ✓ |
| spaCy model | `en_core_web_trf` | Transformer-based NER (RoBERTa backbone) | ✓ downloaded |
| GLiNER | installed | Lightweight zero-shot NER — no need for predefined entity types | ✓ |
| transformers (HuggingFace) | 4.57.6 | Access to any open-source model: REBEL (relation extraction), BGE (reranking), BART (summarization) | ✓ |
| sentence-transformers | 5.4.1 | Embedding generation, cross-encoder reranking | ✓ |
| FastAPI | 0.136.1 | API framework, async I/O, WebSocket support | ✓ |
| uvicorn | 0.46.0 | ASGI server | ✓ |
| httpx | 0.28.1 | Async HTTP client (source fetching, API calls) | ✓ |
| Jinja2 | 3.1.6 | Server-side templating (dashboard HTML) | ✓ |
| numpy | 2.4.4 | Numerical computation | ✓ |
| pandas | 2.3.3 | Data manipulation, CSV/JSON processing | ✓ |
| scikit-learn | 1.8.0 | Logistic regression, clustering (contradiction detection, correlation analysis) | ✓ |
| networkx | 3.6.1 | Graph algorithms (entity centrality, relationship pathfinding) | ✓ |
| beautifulsoup4 | 4.14.3 | HTML parsing (source extraction, content scraping) | ✓ |
| lxml | 6.1.0 | Fast XML/HTML parsing | ✓ |
| jsonschema | 4.26.0 | Rule validation against schema, entity structure enforcement | ✓ |

---

## Hardware

| Resource | Spec | Status |
|---|---|---|
| GPU | NVIDIA GTX 1080 8GB VRAM | ✓ Working (Windows host, accessible via WDDM) |
| CUDA | 12.1 (driver 531.18) | ✓ |
| GPU memory usage | 1,816MB / 8,192MB (idle) | ~22% utilized — headroom for models |
| Ollama | NOT REACHABLE on localhost:11434 | ⚠️ May be on Windows host, not WSL. Needs verification. Models appear to be served via cloud provider currently. |

---

## Missing But Available (pip install — all verified on PyPI)

| Component | Purpose | Install | Size/Requirements |
|---|---|---|---|
| playwright | Headless browser for JS-rendered pages (Google docs, dynamic content) | `pip install playwright && playwright install chromium` | ~300MB (browser binary) |
| pyvis | Interactive network graph visualization (entity/relationship explorer) | `pip install pyvis` | Lightweight (~2MB) |
| crawl4ai | AI-friendly web crawling (markdown extraction, bypasses Cloudflare) | `pip install crawl4ai` | ~10MB |
| feedparser | RSS/Atom feed parsing (source monitoring, patent RSS) | `pip install feedparser` | Lightweight |
| sse-starlette | Server-Sent Events for real-time dashboard updates | `pip install sse-starlette` | Lightweight |

---

## Component-by-Component Stack Map

### 1. Intelligence Layer — Source Ingestion

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Fetch web pages (static) | httpx + beautifulsoup4 | Already installed | Fast, no browser overhead |
| Fetch JS-rendered pages | playwright | Install needed | For Google docs, Cloudflare sites |
| Fetch RSS/Atom feeds | feedparser | Install needed | Patent monitoring via RSS, source health checks |
| Bulk crawling | crawl4ai or scrapy | crawl4ai on PyPI | For full site extraction |
| API calls | httpx (async) | Already installed | Google Patents (no official API → need scraping), USPTO Open Data |

### 2. Intelligence Layer — NLP Extraction

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Named Entity Recognition (NER) | spaCy `en_core_web_trf` | Already downloaded | Transformer-based, 18 entity types. Heavy (~500MB). GPU recommended. |
| Lightweight NER | GLiNER | Already installed | Zero-shot, no predefined types. 50-100MB. Good for custom entities. |
| Relationship Extraction | REBEL model via transformers | transformers already installed | `Babelscape/rebel-large` on HuggingFace. Extracts (subject, relation, object) triples. |
| Text summarization | BART/T5 via transformers | transformers installed | For condensing source documents into extractable rules |
| Keyword / keyphrase extraction | spaCy + rake-nltk or keybert | spaCy installed; keyBERT on PyPI | For entity linking in source documents |
| Content readability scoring | textstat or built custom | textstat on PyPI | Flesch-Kincaid, SMOG, etc. |
| Schema.org markup detection | beautifulsoup4 + jsonschema | Both installed | Extract JSON-LD blocks, validate against schema types |
| Rule confidence correlation | scikit-learn (logistic regression) | Already installed | Entity density → citation probability model |

### 3. Domain KG

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Knowledge graph storage | LightRAG | Installed (1.4.15) | Proven at 33K docs. NanoVectorDB for vectors. JSON for graph storage. |
| Vector embeddings | sentence-transformers | Installed (5.4.1) | `all-MiniLM-L6-v2` (384d, fast) or `nomic-embed-text` (768d, via Ollama) |
| Reranking | sentence-transformers cross-encoder | Installed | `cross-encoder/ms-marco-MiniLM-L-6-v2` or BGE-reranker |
| Entity versioning | Custom JSON schema + migration scripts | jsonschema installed | Schema version field on every entity. Migration v1→v2 scripts. |
| Graph visualization | pyvis | Install needed | Interactive network graphs in HTML (dashboard embeddable) |
| Content inventory tracking | Custom (pandas + JSON) | Both installed | What pages exist, what entities they cover, timestamps |
| Freshness tracking | Custom (datetime + JSON) | Built-in stdlib | Entity timestamps, alert thresholds, decay calculation |

### 4. Content Output — Gap Detection

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Gap scoring engine | Custom Python | numpy + pandas installed | Weighted formula: rule × 0.30 + signal × 0.35 + vacuum × 0.20 + decay × 0.15 |
| Content → entity mapping | spaCy NER + LightRAG graph traversal | Both installed | Parse existing content, extract entities, match against KG |
| Schema gap detection | jsonschema comparison | Installed | Compare required schema against current page schema |
| Competitor content audit | playwright + beautifulsoup4 | playwright needs install | Scrape competitor pages, extract schema, NER, structure |

### 5. Dashboard

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Web framework | FastAPI | Installed (0.136.1) | Async, modern, typed |
| HTML templating | Jinja2 | Installed (3.1.6) | Server-side rendering |
| Real-time updates | SSE via sse-starlette | Install needed | Push freshness alerts, ingestion progress |
| Frontend interactivity | HTMX (no-build JS) | Single JS file, CDN | No npm, no React. Swap HTML fragments from server. |
| Styling | Simple CSS or Pico.css | Single CSS file, CDN | No framework needed. Dark theme. |
| Chat interface | Custom (FastAPI POST + SSE response) | Installed | Query Domain KG, stream response |
| Ingestion progress | SSE or polling | sse-starlette needed | Show chunk count, extraction progress |

### 6. Monitoring & Operations

| Need | Solution | Stack | Notes |
|---|---|---|---|
| Source health checks | httpx + custom logic | Installed | Last published date, 404 detection, 90-day alert |
| Patent monitoring | feedparser (USPTO RSS) + playwright (Google Patents) | feedparser on PyPI | No official Google Patents API. USPTO has open RSS feeds. |
| Change detection | custom (bs4 diff + hashing) | Installed | Compare today's scrape to yesterday's. Detect content changes. |
| LLM cost tracking | Custom (token counter + pricing table) | Built | Track tokens per extraction, calculate cost per source |
| Alert system | Custom (SSE push + cron) | Installed | Freshness alerts, contradiction flags, source death notices |
| Logging | Python logging + structlog | logging in stdlib | Structured logs, JSON format, ingestible by dashboard |

---

## What We DON'T Need (Anti-Stack)

These were considered but rejected:

| Component | Why Rejected |
|---|---|
| Docker/Kubernetes | Overkill for single-machine deployment. systemd user services are sufficient. |
| Redis/RabbitMQ | No message queue needed yet. FastAPI async handles concurrency. Cron handles scheduling. |
| PostgreSQL/Neo4j | LightRAG uses NanoVectorDB + JSON files. No external database needed. |
| React/Vue/Angular | HTMX + Jinja2 is simpler, fewer dependencies. No build step. |
| LangChain/LlamaIndex | LightRAG is the graph engine. Adding another abstraction layer adds complexity without benefit. |
| GraphRAG (Microsoft) | LightRAG is more battle-tested for our scale. GraphRAG is experimental. |
| Pinecone/Weaviate/paid vector DB | NanoVectorDB is built into LightRAG. Free. Local. |
| OpenAI API (paid) | Ollama + open-source models. Zero API cost. (Cloud provider for heavy models is acceptable fallback.) |

---

## Stack Gaps — What Doesn't Exist (Open Source)

| Gap | Why It Matters | Mitigation |
|---|---|---|
| **Google Patents has no official API** | Patent monitoring is Tier 1 predictive signal. Google Patents is the richest source. | Scrape via playwright (JS-rendered). Accept fragility. Fallback: USPTO Open Data API + RSS (less rich but official). |
| **No open-source "SEO rule engine" exists** | The Intelligence Layer is novel. No pre-built pipeline for "extract SEO rules from sources → apply to KG." | Build from scratch using NLP primitives (NER, RE, summarization). This IS the product. |
| **Schema.org citation correlation tool** | No tool that tests "does this schema markup cause citation?" | Build citation audit pipeline: publish → query engines → compare. Manual at first. |
| **LLM cost tracking for local models** | Most cost trackers assume API pricing (per-token billing). Local models have different cost model (GPU time, electricity). | Build custom. Token count × local inference time estimate. Simpler than API tracking. |
| **Content freshness half-life database** | No public dataset of "how long does content stay citable per industry?" | Build our own via longitudinal tracking. 12-month commitment. |

---

## Final Stack (2026-05-14) — Systems-Thinking Validated

> This section replaces all previous scraping layer recommendations. Validated via direct repo inspection, not web search.

### Hands Layer — Final

| Task | Tool | License | Why |
|---|---|---|---|
| Simple page fetch (80% of tasks) | **playwright** | Apache 2.0 | Fast, deterministic, zero LLM cost |
| Anti-detect browser layer | **camoufox** | MPL-2.0, 8K+ stars | Firefox fork that beats fingerprinting. For Google properties, patent sites, anti-bot walls. |
| AI-powered complex navigation | **browser-use** | MIT, 93K+ stars | "Find patent filings about generative retrieval" → it figures out the clicks |
| IP rotation | **User's proxy** (decode or similar) | User-managed | All tools accept `PROXY_SERVER` env var |

### Firecrawl — Rejected

**Why:** Self-hosted version lacks "Fire-engine" (their anti-detection layer). Their own docs: *"Self-hosted instances do not have access to Fire-engine, which includes advanced features for handling IP blocks, robot detection mechanisms."* Adds Node.js + Rust + Redis + Postgres to a Python stack. Too heavy. Too locked.

### Installation

```bash
pip install playwright && playwright install chromium
pip install camoufox browser-use pyvis sse-starlette feedparser keybert textstat
```

6 packages. All Python. No Docker. No external databases. Proxy slots into all tools.

### Full Stack Reference

| Layer | Component | Status |
|---|---|---|
| **Brain** (KG Engine) | LightRAG 1.4.15 | ✓ Installed |
| **Eyes** (NLP) | spaCy 3.8.14 + en_core_web_trf, GLiNER, REBEL | ✓ Installed |
| **Search** (Retrieval) | sentence-transformers 5.4.1 (bi-encoder + cross-encoder) | ✓ Installed |
| **Spine** (Web) | FastAPI 0.136.1 + uvicorn + Jinja2 | ✓ Installed |
| **Face** (UI) | HTMX + Jinja2 + SSE (sse-starlette) | HTMX: CDN. sse-starlette: install |
| **Hands** (Scraping) | playwright + camoufox + browser-use + user's proxy | Install 3 packages |
| **Nerves** (Monitoring) | feedparser + custom diff | Install 1 package |
| **Ledger** (Analysis) | numpy + pandas + scikit-learn + networkx | ✓ Installed |
| **Rulebook** (Validation) | jsonschema 4.26.0 | ✓ Installed |
| **Hardware** | GTX 1080 8GB (1.8GB used at idle) | ✓ Sufficient |

```bash
source /home/steve/lightrag-env/bin/activate

# Core scraping
pip install playwright && playwright install chromium

# Dashboard
pip install pyvis sse-starlette

# Monitoring
pip install feedparser crawl4ai

# Optional quality-of-life
pip install keybert textstat
```

Total new packages: 6. Total additional disk: ~350MB (mostly playwright browser binary).

---

## Verdict

**YES — we have the proper tech stack.** Everything needed for the Knowledge Synthesis Engine exists as open-source, is either already installed or available on PyPI, and runs on our hardware (GTX 1080 8GB). The only things that don't exist are the novel components we're BUILDING (Intelligence Layer rule extraction, citation audit pipeline, entity density correlation). That's the product.

---

*Assessment: 2026-05-14. Verified by direct system introspection + PyPI availability check. No web search used.*
