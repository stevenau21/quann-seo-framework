# Architect Extraction Pipeline — Plan

**Date:** 2026-05-22 01:30 AM
**Goal:** Extract frameworks, mental models, methods, and signal hierarchies from Koray Gubur's 395 ingested docs → structured `frameworks.json`

## Current State

| What | Status |
|---|---|
| Koray Gubur LightRAG | 🟢 Running on port 8012 |
| Docs ingested | 394 (holisticseo.digital articles) |
| Entities extracted | 394 (by LightRAG auto-extraction) |
| Relations extracted | 394 |
| Full docs stored | 394 (6.7MB JSON) |
| Extraction code | ❌ Nothing built yet |
| frameworks.json | ❌ Doesn't exist |

## Architecture Context

The extraction schema is defined in `knowledge-synthesis-architecture/SKILL.md` under "Phase 2: Individual Extraction." The output is `frameworks.json` per architect with this structure:

```json
{
  "architect": { name, paradigm, domains, extraction_date, total_docs_analyzed },
  "frameworks": [{ id, name, type, confidence, definition, source_docs, evolution, depends_on, contradicts, raw_sources_cited, unique_position, negative_space }],
  "mental_models": [...],
  "methods": [...],
  "signal_hierarchy": { ranked: [...] },
  "breadcrumbs": { patents, papers, api_docs, official_docs },
  "negative_space": { topics_avoided, questions_never_answered, contradictions_unresolved, blind_spots }
}
```

## Approach

This is an **LLM-powered extraction** — we query the LightRAG graph for documents, feed chunks to gemma4:31b-cloud with a structured prompt, and aggregate the results into `frameworks.json`.

### Why not use LightRAG's built-in query?

LightRAG query returns chat-style responses, not structured data. We need the extraction to produce machine-readable JSON. The approach:
1. Pull raw documents from `kv_store_full_docs.json` or query via LightRAG API
2. Chunk documents into LLM-friendly segments (~8K chars each)
3. Send each chunk to gemma4 with a structured extraction prompt
4. Merge overlapping extractions, deduplicate, and produce final `frameworks.json`

### Two-pass strategy

**Pass 1 — Entity/Concept Discovery:** Query LightRAG for all entities. Feed entity list to LLM to identify which are frameworks, which are mental models, which are methods.

**Pass 2 — Deep Extraction:** For each identified framework/model/method, pull the relevant source docs and extract full details (definition, evolution, dependencies, contradictions, breadcrumbs).

### Model choice

gemma4:31b-cloud on Ollama Cloud. Fast enough for batch extraction (~5-8s per chunk). Deep reasoning NOT needed for extraction — we learned this from the ingestion failure catalog.

## Step-by-Step Plan

### Step 1: Query LightRAG for entity landscape
- GET `/documents` → list all 394 docs with titles
- GET `/graph/entity/list` → all entities with descriptions
- Save entity list to `koray_entities.json`

### Step 2: LLM classification pass
- Feed entity list to gemma4 → classify each as: framework, mental_model, method, concept, tool, example, or noise
- Identify the top 10-15 framework entities (Koray's core operating system)

### Step 3: Framework deep-dive
- For each identified framework, pull related docs from LightRAG
- Feed doc chunks to gemma4 with structured prompt:
  ```
  Extract from Koray Gubur's content:
  - Framework name + definition
  - What problem it solves
  - How it evolved over time
  - What it depends on
  - What it contradicts
  - Raw sources cited (patents, papers, docs)
  - What's unique about his position
  - What he doesn't address (negative space)
  ```

### Step 4: Mental models & methods extraction
- Same deep-dive for mental models and methods
- Extract signal hierarchy (what Koray says matters most → least)

### Step 5: Breadcrumb tracing
- Scan all docs for citations: patents (USPTO numbers), papers (arXiv, academic), API docs, official sources
- Build the breadcrumbs map

### Step 6: Negative space analysis
- What topics does Koray avoid?
- What questions does he never answer?
- What contradictions exist in his own work?
- What blind spots does he have?

### Step 7: Assemble frameworks.json
- Merge all extractions
- Deduplicate overlapping frameworks
- Add metadata (extraction_date, paradigm=seo, total_docs_analyzed=394)
- Save to `/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur/frameworks.json`

## Files to Create/Modify

| File | Purpose |
|---|---|
| `koray-gubur/extract_frameworks.py` | Main extraction pipeline |
| `koray-gubur/extraction_prompts.py` | Structured prompts for gemma4 |
| `knowledge-synthesis/extractions/koray-gubur/frameworks.json` | Output |
| `knowledge-synthesis/extractions/koray-gubur/entities.json` | Entity classification |
| `knowledge-synthesis/extractions/koray-gubur/extraction_log.jsonl` | Per-chunk extraction log |

## Validation

- [ ] frameworks.json has at least 5 frameworks extracted
- [ ] Each framework has: id, name, definition, source_docs (at least 2), evolution
- [ ] Signal hierarchy is ranked (not just a list)
- [ ] Breadcrumbs include at least 3 patents or papers
- [ ] Negative space is non-empty (legitimate blind spots identified)
- [ ] Total extraction covers at least 50 unique source docs

## Risks

1. **LLM hallucination** — gemma4 may invent frameworks that don't exist in the source. Mitigation: every framework must cite specific source_docs (doc IDs that exist in the workspace).
2. **Token budget** — 394 docs × 8K chars = 3.2M chars. Can't process all at once. Will batch with `max_tokens` limits.
3. **Overlap/duplication** — Koray revisits the same frameworks across multiple articles. Need dedup by concept, not just by keyword.
4. **Deep reasoning temptation** — gemma4 is fast but less thorough than deepseek-v4-pro. Resist switching models mid-extraction. Speed > perfection for Phase 2.

## Timeline Estimate

- Step 1-2: ~5 min (entity listing + LLM classification)
- Step 3-4: ~20-30 min (batch extraction of 10-15 frameworks × 3-5 chunks each)
- Step 5-6: ~5 min (breadcrumb scan + negative space)
- Step 7: ~5 min (assembly)

Total: ~45 minutes for first architect extraction.
