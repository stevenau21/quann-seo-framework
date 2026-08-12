# Quan SEO Framework

A complete semantic SEO system built on **Koray Tuğberk GÜBÜR's** topical authority methodology, implemented for **Quan Nguyen** (License #0774451, REAL BROKERAGE) and the **quann.homes** real estate domain.

## What This Repo Contains

This repository is the full SEO infrastructure — from source research to knowledge graphs to content generation pipelines. It is NOT a lightweight tutorial; it is the actual production system running on Quan's server.

---

## Architecture Overview

```
01-topical-map/          → Master SEO roadmap (11-layer architecture, 38 files)
02-knowledge-graphs/     → LightRAG workspaces (Koray's site, lectures, quann.homes)
03-extraction-pipeline/  → 5-phase framework extraction from Koray's 395-URL corpus
04-knowledge-synthesis/  → Rule inventory, gap reports, entity audits, content briefs
05-content-briefs/       → (merged into 04-knowledge-synthesis/briefs/)
06-nexus-server/         → FastAPI server powering LightRAG query UI + sitemap ingestion
07-seo-rag-server/       → Standalone RAG chatbot server (FastAPI + Ollama)
08-skills/               → Hermes Agent skills (reusable SEO workflows)
09-research/             → Raw research data (holisticseo.digital chunked corpus)
10-roadmap/              → SEO methodology reference materials
```

---

## 1. Topical Map (`01-topical-map/`)

The master SEO roadmap for quann.homes — an 11-layer, 38-file architecture covering:
- Entity definitions (person, broker, service areas, neighborhoods)
- Topical clusters (buying, selling, neighborhoods, lifestyle, legal)
- Internal linking strategy
- Content silo structure
- Source attribution and uniqueness criteria

**Status:** Phase 2 (as of May 2026)

---

## 2. Knowledge Graphs (`02-knowledge-graphs/`)

Three LightRAG knowledge graphs built from different source corpora:

### koray-gubur (220MB, 394 documents)
- **Source:** 395 URLs scraped from `holisticseo.digital` (Koray's site)
- **Purpose:** The primary SEO methodology knowledge base
- **Graph:** `graph_chunk_entity_relation.graphml` (9.8MB, 394 entities, 394 relations)
- **Scripts:** `batch_ingest_koray.py` (sitemap → chunk → LightRAG ainsert)
- **Config:** `config.json` (DeepSeek for extraction, Ollama for embedding)

### koray-lectures (37MB, 89 documents)
- **Source:** Koray's YouTube lecture transcripts
- **Purpose:** Supplemental methodology content not on the blog
- **Graph:** 85 entities, 79 relations

### quann-chat (8.1MB, 24 documents)
- **Source:** quann.homes pages (about, contact, blog, legal)
- **Purpose:** Quan's own content knowledge base for RAG-powered chat
- **Key scripts:**
  - `incremental_ingest.py` — Incremental ingestion (never wipe-and-reload)
  - `rule_bridge.py` — Bifurcated RuleBridge (deterministic checks + LLM directive injections)
  - `rule_extractor.py` — Extract SEO rules from Koray's knowledge graph
  - `entity_audit_engine.py` — Audit entities for template contamination
  - `content_brief_generator.py` — Generate content briefs scored against Koray's rules
  - `crash_recovery.py` — Auto-recover orphaned LightRAG processes

---

## 3. Extraction Pipeline (`03-extraction-pipeline/koray-gubur/`)

A 5-phase enterprise-grade pipeline that extracts structured SEO frameworks from Koray's 395-URL corpus:

| Phase | Script | Output | Description |
|-------|--------|--------|-------------|
| 1 | `phase1_clean.py` | `phase1_clean_graph.json` | Clean and normalize the LightRAG graph |
| 2 | `phase2_communities.py` | `phase2_communities.json` | Community detection (Louvain/Leiden) |
| 3 | `phase3_extract.py` | `phase3_extractions_v4_deepseek.json` | Deep extraction (DeepSeek-v4) — frameworks, mental models, strategies |
| 4 | `phase4_remediation.py` | `phase4_flashcards.json` | Flashcard generation + remediation |
| 5 | `phase5_graph.py` | `phase5_dependency_graph.json` + `.mermaid` + `.html` | Dependency graph visualization |

### Extracted Frameworks (12 total):
- Signal hierarchy
- Agent Rank Patent
- Negative space analysis
- Source attribution
- Topical authority
- Semantic SEO
- Entity-first indexing
- Content uniqueness
- Information gain
- And more...

### Mental Models (6):
- Search engine as student
- Topical map as curriculum
- Source as teacher
- Entity as concept
- Query as question
- Content as answer

---

## 4. Knowledge Synthesis (`04-knowledge-synthesis/`)

The bridge between Koray's methodology and Quan's content:

### Key Files
- **`kernel.py`** — Core synthesis engine
- **`gap_report.json`** — Rule compliance audit (82/204 checks = 40.2%, severity CRITICAL)
  - 81 total gaps (33 high, 48 medium)
  - 53 template contamination entities
- **`entity_audit_report.json`** — Entity audit of quann-chat graph
- **`entity_audit_client_report.md`** — Human-readable audit report
- **`rules_inventory.json`** — Complete inventory of Koray's SEO rules
- **`koray_sitemap_urls.txt`** — 395 source URLs from holisticseo.digital

### Content Briefs (`briefs/`)
14 content briefs generated May 24, 2026, each scored against Koray's SEO rules:
- Out-of-state buyer guide
- First-time home buyer guide
- Steps for buying your first home
- About me page
- Home tours
- Blog template
- Privacy policy, Terms of service, Cookie policy, Disclosure
- Texas Real Estate Commission Information About Brokerage Services

Each brief uses the **Bifurcated RuleBridge** pattern:
1. **Deterministic checks** — Hard-coded rules (word count, heading structure, entity coverage)
2. **LLM directive injections** — Soft rules scored by LLM against Koray's methodology

---

## 5. Nexus Server (`06-nexus-server/`)

A FastAPI server that powers LightRAG query UI and sitemap ingestion:
- **Port:** 9620 (local)
- **Public:** `rag.quann.homes` via Cloudflare Tunnel
- **Notebooks:** `quann-chat` (gemma4:31b-cloud), `seo-methodology` (deepseek-v4-pro:cloud)
- **Features:**
  - Multi-notebook LightRAG management
  - Sitemap ingestion (`ingest_sitemap.py`)
  - Pipeline recovery (`scripts/pipeline_recovery.py`)
  - Ollama forwarder for local model routing
  - Unified Web UI for graph exploration

### Deployment
```bash
cd 06-nexus-server
pip install -r requirements.txt
cp .env.example .env  # Fill in API keys
python nexus_server.py
```

---

## 6. SEO RAG Server (`07-seo-rag-server/`)

A standalone FastAPI RAG chatbot replacing Dify:
- Uses LightRAG for retrieval
- Serves quann.homes visitor questions
- Docker-ready (`Dockerfile` included)
- systemd service file (`seo-rag.service`)

---

## 7. Skills (`08-skills/`)

19 Hermes Agent skills encoding reusable SEO workflows:

| Skill | Purpose |
|-------|---------|
| `seo-framework-execution` | Execute the full SEO Topical Authority Framework |
| `seo-topical-map` | Build a complete semantic SEO topical map using dual LightRAG |
| `seo-entity-discovery` | Discover and audit external web profiles |
| `seo-market-data-collection` | Pull live market data for SEO content (real estate focus) |
| `knowledge-synthesis-architecture` | Multi-source intelligence synthesis architecture |
| `lecture-gap-auditor` | Cross-reference framework outputs against lecture content |
| `architect-extraction-pipeline` | Enterprise-grade 5-phase extraction pipeline |
| `knowledge-graph-gap-analysis` | Compare two LightRAG graphs for semantic gaps |
| `rulebridge-content-brief` | Bifurcated RuleBridge for content briefs |
| `seo-rag-server-skill` | Build/deploy the SEO RAG server |
| `lightrag-rag-apps` | Build self-contained LightRAG FastAPI apps |
| `lightrag-sitemap-ingestion` | Incremental sitemap → LightRAG ingestion |
| `lightrag-webui` | Launch LightRAG's built-in Web UI |
| `lightrag-model-selection` | Pick/validate LLMs for entity extraction |
| `lightrag-incremental-ingestion` | Never-wipe incremental ingestion pattern |
| `query-expansion` | HyDE-style multi-angle query expansion |
| `quannchat-ingestion-pipeline` | Quan's Instagram/website ingestion pipeline |
| `custom-rag-chatbot` | Build custom RAG chatbot (FastAPI + Ollama) |
| `deterministic-router-llm-templater` | Deterministic router + LLM templater pattern |

---

## 8. Research Data (`09-research/`)

- `holisticseo_chunks.jsonl` — 395 URLs from Koray's site, chunked and ready for ingestion
- `extract_chunks.py` — Chunk extraction script

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Source URLs (Koray's site) | 395 |
| LightRAG docs (koray-gubur) | 394 |
| LightRAG docs (koray-lectures) | 89 |
| LightRAG docs (quann-chat) | 24 |
| Dify knowledge base files | 3,944 |
| Extracted frameworks | 12 |
| Extracted mental models | 6 |
| Content briefs generated | 14 |
| Rule compliance | 40.2% (82/204) |
| Gap report severity | CRITICAL (81 gaps) |
| Template contamination entities | 53 |

---

## Technology Stack

- **LightRAG** — Knowledge graph construction and RAG retrieval
- **DeepSeek** — Deep extraction (phase 3) and seo-methodology notebook
- **Ollama (gemma4:31b)** — Local LLM for quann-chat notebook
- **nomic-embed-text-v2-moe** — Embedding model
- **FastAPI** — Nexus Server and SEO RAG Server
- **Cloudflare Tunnel** — Public access at `rag.quann.homes`
- **systemd** — Service management with auto-restart

---

## Methodology Credit

This framework implements the SEO methodology of **Koray Tuğberk GÜBÜR** (holisticseo.digital), including:
- Topical authority mapping
- Semantic SEO and entity-first indexing
- Source attribution and information gain
- Negative space analysis
- Signal hierarchy

---

## License

MIT

## Author

Quan Nguyen — REAL BROKERAGE, License #0774451
Domain: [quann.homes](https://quann.homes)
Service areas: Katy, Houston, Austin, Dallas, Rio Grande Valley (Texas)