---
name: query-expansion
description: Add HyDE-style multi-angle query expansion to LightRAG/Nexus retrieval pipelines, with per-notebook toggling for when it helps vs hurts.
category: integrations
---

# Query Expansion for LightRAG Retrieval

## When to use this skill
- Adding query expansion (HyDE-style multi-angle retrieval) to a LightRAG-based server
- The existing pipeline does single-angle search and answers feel thin
- You want richer context from the knowledge graph

## Core pattern

Before searching LightRAG, the LLM generates 3 alternative rewrites of the user's question. Then search from 4 angles (original + 3 rewrites). Deduplicate and merge results before generating the final answer.

## Implementation (Nexus server pattern)

### 1. Add expansion method to NotebookRuntime

```python
async def _expand_query(self, query: str) -> list[str]:
    """Generate 3 varied rewrites of the query using the LLM for multi-angle retrieval."""
    import json
    loop = asyncio.get_event_loop()
    prompt = f"""Rewrite the following question into 3 different, more detailed variations.
Search queries should cover different angles/interpretations. Output ONLY a JSON array of strings, no explanation.

Original: "{query}"

Output format: ["variation 1", "variation 2", "variation 3"]"""
    try:
        data = await loop.run_in_executor(None, self._ollama_sync, "/v1/chat/completions", {
            "model": self.config.llm_model,
            "temperature": 0.2,
            "max_tokens": 120,
            "messages": [
                {"role": "system", "content": "You are a query expansion engine. Output ONLY a JSON array."},
                {"role": "user", "content": prompt},
            ],
        }, 60)
        raw = data["choices"][0]["message"]["content"].strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        variations = json.loads(raw)
        if isinstance(variations, list) and len(variations) >= 1:
            return variations[:3]
    except Exception:
        pass
    return []  # graceful fallback
```

### 2. Modify retrieve() to loop over all queries

```python
async def retrieve(self, query: str, mode: str | None = None) -> dict:
    # Gate: skip expansion if config says no
    if self.config.use_query_expansion:
        expansions = await self._expand_query(query)
    else:
        expansions = []
    
    all_queries = [query] + expansions
    seen_sources = set()
    all_context_parts = []
    all_citations = []
    
    for q in all_queries:
        data_result = await self.rag.aquery_data(q, ...)
        # Deduplicate by source URL AND content similarity (first 60 chars)
        ...
    
    return {"context_text": merged, "citations": all_citations, ...}
```

### 3. Add toggle to NotebookConfig

```python
@dataclass
class NotebookConfig:
    ...
    use_query_expansion: bool = True  # True by default
```

### 4. Disable for notebooks where it hurts

## Critical lesson: When expansion HELPS vs HURTS

| Scenario | Expansion? | Why |
|---|---|---|
| Large KG (100+ entities, 20+ pages) | ✅ ON | 4x citation boost (20 vs ~5). Worth the extra LLM call. |
| Small KG (<10 chunks, <30 entities) | ❌ OFF | No new angles to discover. Adds latency with zero benefit. |
| Slow LLM (>30s per call) | ❌ OFF | Expansion + LightRAG's internal keyword extraction = 3-4 stacked LLM calls = 60-90s of waiting. |
| Fast LLM (<15s per call) | ✅ ON | The 1 extra call is barely noticeable. |

**Rule of thumb**: If the KG has fewer entities than your top_k_retrieve, skip expansion. Search already covers everything.

## Pattern: Dual-model (fast expander + quality reasoner)

The biggest win: use a **separate, faster model** for query expansion while keeping a **higher-quality model** for the final answer. This avoids the trap where expansion slows everything down.

```python
@dataclass
class NotebookConfig:
    ...
    use_query_expansion: bool = True
    expansion_llm_model: str = ""  # empty = use llm_model for both
```

In `_expand_query()`, use the expansion model:
```python
"model": self.config.expansion_llm_model or self.config.llm_model,
```

Example config — gemma rewrites the query, deepseek-v4-pro writes the answer:
```python
NotebookConfig(
    name="seo-methodology",
    llm_model="deepseek-v4-pro:cloud",       # reasoning
    expansion_llm_model="gemma4:31b-cloud",   # expansion
    use_query_expansion=True,
)
```

**When to use dual-model**: Any time the reasoning model is slower than ~20s per call. The expansion model just needs to rephrase — no deep thinking required. Gemma4 is near-perfect for this role (~10-15s per call).

## Model choice matters for speed

**Measured timings on Ollama Cloud (WSL2 → host.docker.internal):**

| Model | Per-call latency | Best for |
|---|---|---|
| `gemma4:31b-cloud` | ~10-15s | **Keyword extraction** + **Query expansion** |
| `deepseek-v4-flash:cloud` | ~20-30s | Borderline for expansion; OK for reasoning on small KGs |
| `deepseek-v4-pro:cloud` | ~40-50s | **Reasoning only** — too slow for expansion but highest quality |

Use the cheapest/fastest model for expansion AND keyword extraction, and your best model for reasoning. `gemma4` does both expansion and keywords for ~25s total, then `deepseek-v4-pro` handles the final answer. Total: ~40-45s with high quality vs ~75s if everything ran on pro.

**Real test results** (query: "how does Quan help first-time buyers in Katy Texas", quann-chat notebook with 169 entities):
- Pure LightRAG with noop LLM: 0 citations, 0 results
- Pure LightRAG with real keywords: 0 citations (hybrid mode mismatch, but context returned)
- Nexus + real keywords + expansion: **70 citations**, ~73s (gemma4 for both)
- SEO (dual-model): gemma expand (~15s) + deepseek-pro reason (~25s) = ~39s total

## ⚠️ Critical prerequisite: Real keyword extraction

Query expansion multiplies your search angles — but if LightRAG can't extract keywords, **every angle returns nothing**. The most common failure mode: a noop/passthrough LLM function that returns `"high_level_keywords":[]`. With no keywords, LightRAG's `kg_query` can't find entities, can't find chunks — the entire retrieval pipeline produces zero results.

### Fix: Give LightRAG a real LLM for keyword extraction

```python
# BEFORE (broken — 0 citations every time):
async def _noop_llm(self, prompt, ...):
    return '{"high_level_keywords": [], "low_level_keywords": []}'

# AFTER (working — 70 citations on the same query):
async def _kw_llm(self, prompt, system_prompt=None, **kwargs):
    """Real LLM just for extract_keywords_only — low temp, short tokens."""
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, self._ollama_sync, "/v1/chat/completions", {
            "model": "gemma4:31b-cloud",      # fast model — doesn't need reasoning quality
            "temperature": 0.1,
            "max_tokens": 100,
            "messages": [
                {"role": "system", "content": system_prompt or "Extract keywords as JSON."},
                {"role": "user", "content": prompt},
            ],
        }, 30)
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return '{"high_level_keywords":[],"low_level_keywords":[]}'
```

Then pass it to LightRAG:
```python
rag = LightRAG(
    working_dir=str(ws),
    llm_model_func=self._kw_llm,   # ← real LLM, not noop
    ...
)
```

**Impact**: Same query, same KG, same expansion — citations went from 0 to 70. Keyword extraction is the foundation. Query expansion multiplies what's already there.

## Verification

After deploying, test with:
```bash
# With expansion (should get 15-20+ citations)
curl -s -X POST http://localhost:8001/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"how does Quan help first-time buyers","session_id":"test1"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('citations:', len(d['citations']))"

# Without expansion (should complete in reasonable time)
curl -s -X POST http://localhost:8001/seo \
  -H 'Content-Type: application/json' \
  -d '{"message":"what is entity-based SEO","session_id":"test2"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('reply preview:', d['reply'][:200])"
```

## Files touched in our Nexus setup
- `/home/steve/lightrag-apps/nexus_server.py` — expansion method + gated retrieve()
- `/home/steve/lightrag-apps/nexus_shared.py` — `use_query_expansion` field on NotebookConfig
