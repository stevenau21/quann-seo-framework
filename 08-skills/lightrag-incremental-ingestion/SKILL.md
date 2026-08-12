---
name: lightrag-incremental-ingestion
description: LightRAG ainsert() is naturally incremental — never wipe the workspace between ingests unless you want a full rebuild. Documents already indexed are skipped via MD5 dedup in doc_status.
category: integrations
---

# LightRAG Incremental Ingestion Best Practices

## Core Finding

LightRAG's `ainsert()` is **incrementally safe by design**. Adding new documents does NOT destroy, dilute, or recompute existing data. The method:

1. Computes MD5 hash of each document content
2. Checks `doc_status` (via `kv_store_doc_status.json`) for each hash
3. **Skips** any document that already exists — zero recomputation
4. Only NEW documents get chunked, embedded, and entity-extracted

Source: `lightrag.py` around line 1449-1506 in the `ainsert` method.

## Anti-Pattern: Workspace Nuking

**In code:**
```python
# ❌ DESTRUCTIVE — forces full rebuild every time
shutil.rmtree(WORKSPACE)
os.makedirs(WORKSPACE, exist_ok=True)
raft = LightRAG(working_dir=WORKSPACE, ...)
await raft.ainsert(documents)
```

This pattern appeared in `quann-chat/index_quann.py` and `seo-methodology/index_seo.py`. Adding ONE new document triggers a full rebuild of ALL documents.

**At the cron level (even worse):**
```bash
# ❌ Weekly cron builds fresh index from subset of URLs → atomically swaps
python3 index.py --workspace workspace_new  # fresh, from 17 hand-picked URLs
mv workspace workspace_old                  # daily cron's 100+ incremental pages → orphaned
mv workspace_new workspace                  # only the 17 pages survive
systemctl restart lightrag-service          # serves from new, incomplete workspace
```

This destroyed the seo-methodology graph every Sunday for weeks — daily cron rebuilt it incrementally Mon-Sat, then Sunday's atomic swap replaced it with a fraction of the content. **Removed both weekly cron jobs (`seo-methodology-weekly-scrape`, `quann-chat-weekly-scrape`).** Each graph now has exactly ONE incremental daily cron and ONE `incremental_ingest.py` script. No more fighting cron jobs.

## Correct Pattern

```python
# ✅ INCREMENTAL — only new documents get processed
raft = LightRAG(working_dir=WORKSPACE, ...)
await raft.ainsert(documents)  # skips existing, processes new
```

## Revising Existing Documents

**Naive re-insertion pollutes the index.** Doc IDs are MD5 hashes of content — change one character and you get a completely different ID. If you just call `ainsert()` with revised content, the old version's chunks and entities remain forever as stale data. Shared entities get duplicated with conflicting descriptions.

**Correct revision workflow: surgical delete + insert:**

```python
# ✅ Surgical revision — cleans old, inserts new
await raft.adelete_by_doc_id(old_doc_id)
await raft.ainsert(revised_document)
```

**What `adelete_by_doc_id()` actually does** (traced from lightrag.py lines 3327-3735):

| Category | Action |
|---|---|
| Chunks exclusive to this doc | Fully deleted from `text_chunks` |
| Entities exclusive to this doc | Fully deleted from graph + `entity_chunks` |
| Entities shared with other docs | **Rebuilt** — description regenerated from remaining chunks only (line 3657) |
| Relationships (same logic) | Exclusive → deleted; shared → rebuilt from remaining sources (line 3732) |
| Other documents | **Completely untouched** — zero recomputation |
| LLM extraction cache | Cleaned up if `delete_llm_cache=True` |

Source proof from `adelete_by_doc_id()`:
```python
# lines 3640-3658
remaining_sources = subtract_source_ids(existing_sources, chunk_ids)
if not remaining_sources:
    entities_to_delete.add(node_label)           # exclusive → delete
elif remaining_sources != existing_sources:
    entities_to_rebuild[node_label] = remaining_sources  # shared → rebuild
else:
    logger.info(f"Untouch entity: {node_label}")  # unaffected
```

**Why MD5 hashing matters for revisions:**
```python
# compute_mdhash_id(content, prefix="doc-")
# "Katiana transcript v1" → doc-abc123
# "Katiana transcript v2" → doc-xyz789  ← completely different, treated as new
```

**Build a revision script pattern:**
```python
# revise_document.py
import sys, json
from lightrag import LightRAG

filename = sys.argv[1]
raft = LightRAG(working_dir=WORKSPACE, ...)

# Find old doc_id by file_path in doc_status
with open(f"{WORKSPACE}/kv_store_doc_status.json") as f:
    docs = json.load(f)
for doc_id, info in docs.items():
    if isinstance(info, dict) and info.get("file_path") == filename:
        result = await raft.adelete_by_doc_id(doc_id)
        print(f"Deleted: {result.status}")

# Insert revised version
with open(filename) as f:
    await raft.ainsert(f.read())
```

## When to Wipe

Only wipe the workspace when:
- Switching embedding models (old vectors won't match)
- **Switching LLM/chunking models** — entity extraction format differs between models; old entities from e.g. Gemma4 have different coverage and naming conventions than Pro's output. Mixing them produces an inconsistent graph.
- Changing chunking strategy (old chunks would be stale)
- Corrupted index needs full rebuild
- You've already deleted `doc_status` entries manually (they must stay in sync)

**Model switch wipe procedure:**
```bash
sudo systemctl stop lightrag-koray-lectures
rm -rf /home/steve/lightrag-apps/koray-lectures/workspace/*
# Verify .env has new model AND mandatory Ollama overrides
grep -E 'LLM_MODEL|OLLAMA_LLM|MAX_GRAPH' /tmp/lightrag-ui-envs/koray-lectures/.env
sudo systemctl start lightrag-koray-lectures
# Confirm health endpoint shows new model
curl -s http://localhost:8014/health | python3 -c "import sys,json; print(json.load(sys.stdin)['configuration']['llm_model'])"
```

**MANDATORY: Test ONE document before batch ingestion.** The Ollama caps (128 output tokens, 32K context) are LightRAG defaults that silently destroy every extraction. Setting them in `.env` is not enough — you MUST verify they're actually in effect. Insert a single 500-1000 char test document and wait for processing to complete before firing the full batch. User correction (2026-05-26): *"makes sure that the 1 million context is on the pro and make sure that it processes everything and do note skip anything"* — context caps must be verified, not assumed.

```python
# Test pattern — insert one doc, wait for processing, check success
import requests, time

resp = requests.post("http://localhost:8014/documents/text", json={
    "text": "Short test paragraph about the framework...",
    "file_path": "test_caps_verify.txt"
}, timeout=60)
track_id = resp.json()["track_id"]

# Trigger scan and poll until done
requests.post("http://localhost:8014/documents/scan", timeout=30)
for i in range(30):
    time.sleep(10)
    s = requests.get("http://localhost:8014/documents/status_counts", timeout=10)
    counts = s.json()["status_counts"]
    if counts["pending"] == 0 and counts["processing"] == 0:
        assert counts["failed"] == 0, f"Test doc failed — caps NOT working! Fix .env before batch."
        print(f"✓ Caps verified — test doc processed in {i*10}s")
        break
```

**Failure pattern:** Test doc sits in `processing` forever or returns `failed`. This means the 128-token or 32K-context cap is still in effect (service didn't pick up `.env` changes, or env vars weren't set correctly). Fix: check `systemctl cat` for `Environment=` lines that might override settings; ensure the service was fully restarted (not just reloaded).

**CRITICAL — LightRAG Ollama default caps:** LightRAG has hidden defaults in `lightrag/llm/binding_options.py` that silently destroy extraction quality. `OLLAMA_LLM_NUM_PREDICT=128` and `OLLAMA_LLM_NUM_CTX=32768` are applied to EVERY extraction call unless overridden in `.env`. Always set these before starting any LightRAG instance:
```bash
OLLAMA_LLM_NUM_CTX=1048576
OLLAMA_LLM_NUM_PREDICT=8192
OLLAMA_LLM_TEMPERATURE=0.0
MAX_GRAPH_NODES=5000
```
Discover all available env var names with: `python -m lightrag.llm.binding_options`

## Batch Size Tuning for Slow Models

**Batch size must match model speed.** The batch ingest script sends N documents, then waits for all N to finish before sending the next batch. If the scan timeout is too short, chunks in the batch silently fail.

| Model | Per-chunk time | Recommended batch size | Recommended scan timeout |
|-------|---------------|----------------------|------------------------|
| Gemma4 31B | ~12s | 8 | 1200s (20 min) |
| Pro | ~88s | 2 | 3600s (1 hour) |
| Flash | ~143s | 2 | 3600s (1 hour) |

**Failure pattern:** Large batch + fast scan timeout = documents appear "inserted" (200 OK) but `wait_for_processing()` times out before the queue finishes. These show as `pending` or `failed` in status_counts. Fix: reduce batch size and increase `SCAN_TIMEOUT`.

## Source Proof

From `lightrag.py` `ainsert()`:

```python
# Step 3. Filter out already processed documents
all_new_doc_ids = set(new_docs.keys())
unique_new_doc_ids = await self.doc_status.filter_keys(all_new_doc_ids)
ignored_ids = list(all_new_doc_ids - unique_new_doc_ids)
# → Documents with existing IDs are skipped entirely
```

## Recovery from Destructive Scripts

If a script already has `rmtree()` and you need to add files incrementally:
1. Remove the `shutil.rmtree()` lines
2. Remove any `os.makedirs()` that recreates the directory
3. Just call `ainsert()` — LightRAG handles the rest

If the workspace was already wiped, the rebuild must complete. For future runs, the corrected script will be incremental.

## Entity Extraction Quality: Gleaning Trade-Off

**`entity_extract_max_gleaning` controls how many refinement passes LightRAG makes over extracted entities.** Each pass re-reads chunks after discovering entities from other chunks, merging descriptions across sources. Without it, multi-chunk entities get raw concatenation with `<SEP>` delimiters.

**The trade-off: quality vs. throughput.**

| Gleaning | Effect | When to use |
|---|---|---|
| 0 | Fastest. Entities described from single-chunk view only. May have `<SEP>` concatenation in multi-chunk entities. | Text-dense conceptual docs (lecture transcripts, SEO theory), tight deadlines, fast models where speed matters |
| 1 | One refinement pass. Merges descriptions from discovered sources. | Default for most use cases |
| 2 | Two refinement passes. Richest entity descriptions, best cross-chunk merging. | Short documents, high-value knowledge bases, when descriptions must be presentation-quality |

**GLEANING=0 IS PROVEN SUFFICIENT for lecture-style content.** The working 8012 instance (seo-methodology, 394 Koray docs) runs with `MAX_GLEANING=0` via systemd override — entity descriptions are coherent and usable, not raw `<SEP>` concatenation. LightRAG versions after ~1.4.x handle single-chunk extraction better than earlier versions.

**Earlier evidence (client-knowledge, 2026-05-13):** Gleaning=0 on older LightRAG produced `<SEP>` concatenation for multi-document entities (HOA dues example). This was a different document type (customer transcripts with overlapping entities across many files) and likely an older LightRAG version. The rule is softer than previously stated — test your document type before assuming gleaning=2 is mandatory.

**When gleaning=2 is worth the 2x time cost:**
- Many short documents sharing the same entities (customer transcripts, meeting notes)
- Entity descriptions will be shown to end users (chatbot responses)
- Throughput is not a bottleneck (fast model, small corpus)

**When gleaning=0 is fine:**
- Long, self-contained documents (lecture transcripts, articles)
- Entity descriptions are for internal retrieval only
- Batch ingestion speed matters (88 lectures × ~20 chunks)

**Fix for any new notebook (start with gleaning=2, reduce if needed):**
```python
rag = LightRAG(
    working_dir=WORKSPACE,
    ...
    addon_params={
        "entity_extract_max_gleaning": 2,
        "entity_types": ["organization", "person", "geo", "event", "category"],
        "language": "English",
    },
)
```
**For systemd-managed instances, override in .env:**
```bash
MAX_GLEANING=2  # or 0 for speed
```

## Cleaning Up Stale `dup-*` Records

**Problem:** After a killed/restarted ingestion run, `kv_store_doc_status.json` contains `dup-MD5HASH` entries marked FAILED alongside the real `tx-NNNN` entries. They share the same file_paths but have zero chunks — pure tracking artifacts that inflate the doc count (e.g., showing 36 when it's really 18).

**Fix when `adelete_by_doc_id()` is inconvenient (venv dependencies):**
```python
import json
WORKSPACE = '/path/to/workspace'
with open(f'{WORKSPACE}/kv_store_doc_status.json') as f:
    doc_status = json.load(f)
# Remove all dup-* entries
for k in [k for k in doc_status if k.startswith('dup-')]:
    del doc_status[k]
with open(f'{WORKSPACE}/kv_store_doc_status.json', 'w') as f:
    json.dump(doc_status, f, indent=2)
```

This is safe because `dup-*` entries have no corresponding chunks or vectors — they were never successfully ingested. Restart the service after to pick up the clean count.

## Pitfalls

- If you `rm -rf` the workspace but NOT the `kv_store_doc_status.json`, `ainsert()` will skip everything because doc_status still shows them as processed. The vectors and graphs are GONE but status says they exist — this causes a corrupted state.
- If you manually delete `doc_status` entries without clearing the workspace, you'll get duplicate entities and chunks.
- Always keep workspace and doc_status in sync. Either wipe both or wipe neither.
- **nomic-embed-text-v2-moe has a 512-token context limit.** Do NOT use `max_token_size=8192` (the LightRAG default). If you do, every embedding call fails with "input length exceeds the context length." Set `max_token_size=512` and use `chunk_token_size=256` to stay safely within the limit. The v1.5 model supports 8192.
- **18 DUPLICATE FAILED records in doc_status after a killed run is expected.** When you kill and restart, LightRAG's `ainsert()` re-computes MD5 hashes and marks every existing doc as [DUPLICATE] FAILED. These are harmless tracking artifacts — the real processed/pending/failed counts reflect actual state. Ignore the duplicate noise and focus on the non-DUPLICATE entries.
- Cloud-proxied models (e.g., `gemma4:31b-cloud` via DeepSeek proxy) have their own timeout policies. A 360s worker timeout is usually the proxy, not the model — the same chunk would process in 30s locally. With LLM cache building up, re-runs on failures are fast since cached extractions are reused.
- **Every new notebook MUST explicitly set gleaning and entity_types.** Forgetting this produces entities with raw `<SEP>` concatenation and `entity_type: ?` — the index looks populated but the descriptions are unusable garbage. The template at `/home/steve/lightrag-apps/notebooks/TEMPLATE.yaml` bakes these in as required fields.
