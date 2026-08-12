---
name: lightrag-model-selection
description: How to pick and validate an LLM for LightRAG entity extraction — what works, what fails silently, and how to benchmark.
---

# LightRAG Model Selection for Entity Extraction

LightRAG's `ainsert()` sends every chunk through the LLM for entity/relationship extraction.
This is **the bottleneck** in indexing — picking the wrong model makes it 23× faster but produces zero usable output.

## QUALITY-FIRST METHODOLOGY (MANDATORY)

**Rule:** Never dismiss a slower model because of speed. Accuracy, relation richness, type precision, and graph completeness are what matter for LightRAG retrieval quality. Speed is ONLY a tiebreaker when accuracy is equal.

**Critical pitfalls from real sessions:**
- Dismissing `deepseek-v4-pro:cloud` as "dead for chunking" because initial runs at `num_predict=4096` produced truncated output. At `num_predict=8192` it completed all 3 chunks cleanly.
- Running partial tests (1 chunk) and jumping to conclusions. User correction: *"No you need to run it and they all need to produce results wait for it to finish."*
- Showing only 2 models in comparison after claiming you'd show all 3. User correction: *"where is flash why didn't you show results for all three again"* — present ALL candidates in every comparison.

**Procedure:** Run ALL candidate models through ALL samples to COMPLETION before drawing any conclusions. Never report "eliminated" based on partial data. Never drop a model from comparison mid-report.

## The Key Finding

**Smaller models (< ~12B parameters) fail silently.** They generate text that looks plausible but
don't follow LightRAG's structured extraction format. Result: no `vdb_entities.json`, no chunks,
no errors — just a fast, empty index.

**Tested (2026-05-27, sandbox benchmark — 3 models × 3 chunks, LightRAG extraction prompt, EVERY model completed EVERY chunk at correct token caps):**

| Model | Avg time | Entities avg | Relations avg | Token cap | Completed | Notes |
|-------|---------|-------------|--------------|-----------|-----------|-------|
| `gemma4:31b-cloud` | ~12s | 15 | 12 | N/A (efficient) | 3/3 ✓ | Clean output, zero hallucinations. Weakest type accuracy. Misses domain concepts (Source Context, Entity Type, Semantic Content Network). No bidirectional relations. |
| `deepseek-v4-flash:cloud` | ~143s | 17 | 13 | **16384** | 3/3 ✓ | Needs `num_predict: 16384` (4096 truncates to zero relations). Low noise. Better types than Gemma4. Still misses bidirectional relations. 12× slower than Gemma4 for marginal quality gain. |
| `deepseek-v4-pro:cloud` | ~88s | **20** | **20** | **8192** | 3/3 ✓ | **Richest graph — 40% more relations than Gemma4.** Required `num_predict: 8192`. Best type accuracy. Bidirectional edges. Only model capturing Source Context, Entity Type, Semantic Content Network. 7× slower than Gemma4 but permanent quality gain. |

**Decision framework:**

| Choose | When |
|--------|------|
| Gemma4 31B | Speed-critical, embedding-dominant retrieval, already proven on infra |
| Pro | **Knowledge graph retrieval (default)** — richest graph, bidirectional edges, best types. Worth the 7× time for permanent quality gain. |
| Flash | Not recommended — 12× slower than Gemma4 for only marginal type improvement |

**Key finding (2026-05-27):** `deepseek-v4-pro:cloud` IS viable and is the best model for chunking — it produces the richest entity graphs with bidirectional relations. Earlier failures were due to TWO issues: (1) `num_predict: 4096` was too low (needs 8192), (2) **LightRAG's Ollama defaults silently cap every extraction**: `OLLAMA_LLM_NUM_PREDICT=128` (not even enough for one entity) and `OLLAMA_LLM_NUM_CTX=32768` (3% of Pro's 1M window). These env vars MUST be set in LightRAG's `.env` file.

## CRITICAL: LightRAG Ollama Default Caps

LightRAG has hidden Ollama defaults in `lightrag/llm/binding_options.py` that will silently destroy extraction quality across ALL models:

| Env var | LightRAG default | What it does | Fix |
|---------|-----------------|--------------|-----|
| `OLLAMA_LLM_NUM_PREDICT` | **128** | Caps output tokens per extraction call | `8192` |
| `OLLAMA_LLM_NUM_CTX` | **32768** | Caps input context window | `1048576` |
| `OLLAMA_LLM_TEMPERATURE` | 1.0 | Non-deterministic extractions | `0.0` |
| `MAX_GRAPH_NODES` | 1000 | Caps total graph size | `5000` |

**These apply to EVERY LightRAG instance using Ollama** — not just Pro. The 128-token output cap means models can't even output one complete entity before being truncated. The 32K context cap wastes 97% of large models' windows.

**To discover all env var names for a LightRAG version:**
```bash
python -m lightrag.llm.binding_options
```

**Fix: Add to `.env` before starting any LightRAG instance:**
```bash
OLLAMA_LLM_NUM_CTX=1048576
OLLAMA_LLM_NUM_PREDICT=8192
OLLAMA_LLM_TEMPERATURE=0.0
MAX_GRAPH_NODES=5000
```

This was the root cause of Pro's "silent failures" — the 128-token cap meant LightRAG's extraction prompt was being fed through a pinhole, not the full 1M window. All model comparisons are invalid if run without these overrides.

**Failed models:**
- `rnj-1:8b-cloud` — 0.6s/chunk but zero entities/chunks (2026-05-12)

## Model Sandbox Benchmarking (PREFERRED METHOD)

Before committing to a model for LightRAG ingestion, run a **controlled sandbox** against 3 representative chunks using LightRAG's actual extraction prompt — not a full `ainsert()` cycle. This is faster (3 API calls per model vs. full indexing) and lets you see EXACTLY what each model outputs.

**Why sandbox first:**
- `ainsert()` swallows failures — a model producing empty content just means missing `vdb_entities.json` with no clear error.
- Sandbox shows raw output, so you catch reasoning-model silent failures (DeepSeek Pro), format violations, and truncation immediately.
- 3 models × 3 chunks = ~60-90 seconds total, vs. minutes-to-hours for full insertion + inspection.

**Methodology:**
1. Pick 3 representative chunks from source material (~250 words each): one introductory, one mid-difficulty, one advanced
2. Use LightRAG's actual extraction prompt (grab from `lightrag/prompt.py`, copy `entity_extraction_system_prompt` and `entity_extraction_user_prompt` with correct delimiters)
3. Send identical prompt + chunk to each candidate model via `curl` or Python `requests` to `http://host.docker.internal:11434/api/chat`
4. Compare: entities count, relations count, elapsed time, output format compliance

**Benchmark script template:** See `references/chunking-sandbox-template.py`.

**Key validation checks:**
- Output MUST use `entity<|#|>name<|#|>type<|#|>desc` format (not prose)
- Output MUST end with `<|COMPLETE|>`
- Entity count should be non-zero (0 = silent failure, even if tokens burned)
- Time per chunk should be under 20s for batch ingestion feasibility
- **Check that `response["message"]["content"]` is non-empty** — reasoning models (DeepSeek Pro, R1 variants) output thinking into `reasoning_content` or internal fields, leaving `content` empty

**`num_predict` tuning:** LightRAG chunks need 2048-4096 output tokens to avoid truncation. If model stops before `<|COMPLETE|>`, bump `num_predict` to 4096.

## Full-Index Benchmark (For Final Validation Only)

Once sandbox identifies the winner, validate with a real LightRAG `ainsert()` on 3 test documents:

```python
# Minimal benchmark: index 3 chunks, time it, check output files
import asyncio, json, time, os, shutil
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc

# ... (set up embed func and llm func with candidate model)
await rag.ainsert(chunks, ids=ids, file_paths=fps)
elapsed = time.time() - start

# VALIDATION — these MUST exist after indexing:
assert os.path.exists(f"{WORKSPACE}/vdb_entities.json"), "Model failed entity extraction!"
assert os.path.exists(f"{WORKSPACE}/vdb_chunks.json"), "Model failed chunk storage!"
```

## What to Check After Benchmarking

1. **`vdb_entities.json` exists AND is > 1KB** — if missing or tiny, model can't handle extraction
2. **`vdb_chunks.json` exists** — if missing, model couldn't even store chunks
3. **`kv_store_full_docs.json`** — should exist regardless, confirms basic insertion worked

## Silent Failure Pattern

- Model returns text quickly (0.6s/chunk vs 14s/chunk)
- No errors thrown
- `kv_store_full_docs.json` created (raw text storage works)
- `vdb_entities.json` and `vdb_chunks.json` **missing** (extraction failed)
- The index is empty — queries return nothing

This happens because small models don't reliably follow the complex structured prompts
LightRAG uses for entity extraction. They produce conversational text instead of
properly formatted entity/relationship JSON.

## Files Affected When Changing the Model

All of these must be updated:
- `*/index_*.py` — standalone indexer scripts
- `seo_ingest.py` — incremental ingestion with model switching
- `nexus_server.py` — unified server with per-notebook configs + keyword extraction LLM
- `client-knowledge/ingest_transcripts.py` — transcript indexer

The **query/runtime LLM** (`seo-methodology/server.py` → `deepseek-v4-pro:cloud`) is separate
and should NOT be changed — it handles end-user queries, not entity extraction.
