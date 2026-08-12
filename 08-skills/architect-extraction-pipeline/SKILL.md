---
name: architect-extraction-pipeline
description: Enterprise-grade 5-phase pipeline for extracting frameworks from an architect's corpus using entity graph community detection. Proved that single-query top-k sampling misses 95%+ of data and per-document blind extraction is methodologically invalid. Use for any architect framework extraction — SEO, AEO, GEO, or any domain.
category: research
---

# Architect Framework Extraction — Enterprise Pipeline

## Trigger

Load this skill when:
- Extracting frameworks/methods from any architect's ingested corpus
- User mentions "extraction pipeline", "framework extraction", "architect analysis"
- Processing a new architect after initial ingestion (Phase 2 of the knowledge synthesis pipeline)
- Need exhaustive framework discovery, not Q&A-style retrieval

## Core Methodological Insight

**Frameworks are latent structures that emerge across many documents.** They are NOT contained in any single document. This invalidates two common approaches:

| Approach | Why It Fails |
|----------|-------------|
| Single LightRAG `/query` | Top-k similarity returns only ~1.5% of data |
| Per-document "what frameworks?" | Each doc has one chapter — can't name the book |
| **Community detection on entity graph** | ✅ Discovers patterns the data already encodes |

## CRITICAL: Document ID Tracking Is Mandatory

**Every extraction phase MUST store the actual document IDs** that contributed to each framework — not just a count. Without `doc_ids` per framework:

- ❌ Cannot update rules (don't know which documents to re-check)
- ❌ Cannot decay confidence (don't know which sources aged out)
- ❌ Cannot track changes over time (can't diff old vs new extractions)
- ❌ Cannot scope grounding verification (every card searches ALL documents = 99% noise)

This permanently cripples the entire Layer 1 lifecycle. A `docs_analyzed` count (e.g., `5`) is useless — it must be the actual KV store keys (`["doc-413e38bbc...", ...]`).

**Reconstruction**: If Phase 3 was run without doc_ids, re-run the same `find_relevant_docs()` scoring deterministically — no LLM calls needed, pure keyword frequency counting against the same data.

## The 5-Phase Pipeline

```
PHASE 1: Graph Cleaning
kv_store_full_entities.json (10,480 entities) → classify types → filter noise → 1,043 signal entities
kv_store_full_relations.json (13,973 edges) → deduplicate → normalize → 1,434 clean edges

PHASE 2: Community Detection (Louvain)
Clean graph → NetworkX → Louvain clustering → 300+ communities → LLM names top communities
Output: framework candidates with entity memberships

PHASE 3: Targeted Extraction (Hypothesis-driven)
For each community: find docs → "We believe docs [A,B,C] discuss Framework X — 
extract everything about X" → deep framework descriptions
NOT: "What frameworks are in this doc?" (blind)

PHASE 4: Aggregation & Merge
Merge overlapping communities → resolve contradictions → build framework hierarchy

PHASE 5: Relationship Graph
Typed edges (depends_on, contradicts, extends) → dependency chains → D3 visualization
Output: Complete frameworks.json with relationship graph
```

## Phase 1: Graph Cleaning

**Script**: `phase1_clean.py`  
**Input**: `kv_store_full_entities.json`, `kv_store_full_relations.json` (from LightRAG workspace)  
**Output**: `phase1_clean_graph.json`

Operations:
1. **Type classification**: Classify each entity as framework, method, tool, person, noise, concept
2. **Deduplication**: Normalize case, group variants, pick canonical name
3. **Noise filtering**: Strip HTML tags, word lists, HTTP headers, browser names, CSS/JS specifics
4. **Edge cleaning**: Remap to canonical names, skip noise entities, remove self-loops

### Entity Type Patterns

**Framework**: Contains SEO, methodology, strategy, model, process, paradigm — usually multi-word
**Person**: `Name Surname` pattern (two capitalized words)
**Tool**: Known tools (Google, NLTK, WordPress, SEMrush, Ahrefs) + API/SDK/CLI suffixes
**Noise**: 90+ regex patterns covering HTML tags, word classifications, HTTP headers, single letters, etc.
**Concept**: Default catch-all

### Filtering Threshold

Keep entities if:
- Type = framework or method (always)
- Type = concept AND degree ≥ 3 AND mentions ≥ 3
- Type = person AND mentions ≥ 3
- Type = tool AND mentions ≥ 5

Result: 10,480 → 1,043 entities, noise cut from 1,997 → 0.

## Phase 2: Community Detection

**Script**: `phase2_communities.py`  
**Input**: `phase1_clean_graph.json`  
**Output**: `phase2_communities.json`

Steps:
1. Build weighted NetworkX graph (node attributes from Phase 1, edge weights from relation counts)
2. Run Louvain community detection (`louvain_communities(G, weight="weight", seed=42)`)
3. For each community with size ≥ 5, use LLM to name it as a framework
4. Betweenness centrality to rank entities within each community

### Community Analysis

For each community:
- Size (entity count), internal edges, density
- Type distribution (framework/person/concept ratio)
- Top entities by betweenness centrality
- LLM naming prompt with entity list → framework name + definition

### Important: Many Communities → Merge Needed

Louvain at this resolution typically produces 300+ communities (most are singletons with no edges). Only ~12-15 have signal (size ≥ 5). Multiple communities often represent the same framework at different granularities — Phase 4 handles merging.

## Phase 3: Targeted Extraction

**Script**: `phase3_extract.py`  
**Input**: `phase2_communities.json`, `kv_store_full_docs.json`, `kv_store_full_entities.json`  
**Output**: `phase3_extractions.json`

### Key Difference: Hypothesis-Driven vs. Blind

**Wrong**: "Here's a document. What frameworks are in it?"  
**Right**: "We believe these 23 documents discuss Topical Authority. Extract everything they say about Topical Authority specifically."

This matters because:
- The LLM has context about *what* to extract
- Documents are selected because they actually discuss the framework
- Multiple documents provide the full picture across chapters

### Doc-to-Community Mapping

For each community:
1. Take all entity names in the community
2. Query `kv_store_full_entities.json` to find which documents contain those entities
3. Pull up to 15 documents (first 2000 chars each, max 12000 chars total)
4. Assemble prompt: "Deep-dive on Framework X from these documents"

### Extraction Schema

For each framework, extract:
- `definition` — 2-3 sentence summary
- `components` — sub-components, pillars, building blocks
- `methods` — specific techniques with numbered steps
- `evolution` — versions, iterations, changes
- `metrics` — what gets measured/tracked
- `context` — problem it solves, why created
- `nuances` — subtle distinctions from generic versions
- `dependencies` — other frameworks this depends on
- `unique_terms` — Koray-specific vocabulary

## Phase 4: Aggregation & Merge

**Output**: `phase4_frameworks.json`

1. **Overlap detection**: Communities sharing >50% of central entities → merge
2. **Name resolution**: When multiple communities have similar LLM names, use the largest community's name
3. **Hierarchy building**: dependency chains, parent/child framework relationships
4. **Contradiction resolution**: If two communities describe the same framework differently, flag for review

## Phase 5: Relationship Graph

**Output**: `phase5_graph.json` + D3 visualization

Edge types:
- `depends_on` — Framework A requires understanding of Framework B
- `contradicts` — Framework A's claims conflict with Framework B's
- `extends` — Framework A is a specialization of Framework B
- `co_occurs` — Frameworks appear in same documents frequently

## Environment & Configuration

### Data Files
```
/home/steve/lightrag-apps/{architect-name}/workspace/
├── kv_store_full_docs.json       # Raw documents (Phase 1 input for doc mapping)
├── kv_store_full_entities.json   # Entity extraction (Phase 1 input)
├── kv_store_full_relations.json  # Relation pairs (Phase 1 input)
└── graph_chunk_entity_relation.graphml  # Raw graph (optional)
```

### LLM Configuration

### Phase 1-2 (Classification + Community Naming): Fast model
```python
MODEL = "gemma4:31b-cloud"  # Fast, reliable for high-volume classification
temperature = 0.3
```

### Phase 3 (Deep Extraction): Large-context model (REQUIRED)
```python
MODEL = "deepseek-v4-flash:cloud"  # 1M context window — feed ALL matching docs
temperature = 0.2
max_tokens = 8000  # Rich structured output
char_limit = 200000  # 5-8 full documents per framework
```

**Why this matters:** gemma4's ~8K effective context limits Phase 3 to 1-2 docs (25K chars). DeepSeek v4 Flash at 200K chars feeds 5-8 full documents — 8x more context. Result: output 50-200% richer across every framework dimension. Entity-Based SEO went from 0→16 methods, Technical SEO 3→40 when switching models.

**NEVER use deep reasoning models (deepseek-v4-pro) for extraction** — they're 10-15x slower per chunk and trigger WSL2 TCP timeouts. Fast models for extraction, reasoning models for analysis only.

### Phase 4 (Validation + Flashcard Explosion): Fast model with batching
```python
MODEL = "deepseek-v4-flash:cloud"  # Fast enough for bulk verification
temperature = 0.0  # Deterministic for factuality
```
Use batch verification: 36 calls instead of 11,100. Group all claims for one framework × field type into single LLM call.

### Phase 4 Grounding: Embedding + Source Verification Pipeline

Phase 4 produces 500+ flashcards from extracted frameworks. Each card must be **grounded** — verifiable against source documents via embedding similarity. The target grounding rate is >70%. Without grounding, the downstream rules engine (Phase 5) can't distinguish verified rules from hallucinations.

#### The Grounding Problem

**Baseline without patches: 16% grounding rate (86/534).** Root causes:

1. **Shallow embedding inputs**: `nomic-embed-text` produces weak embeddings when given only card text. Raw card content ("Use canonical URLs") lacks the semantic density to match against full paragraphs in source documents.
2. **Dropped LLM tags**: Free-form JSON prompts allow the LLM to skip cards, leaving empty `target_entity` fields. Even 1 missing tag out of 534 breaks that card's grounding.
3. **Auth split**: Chat models may require cloud API (`ollama.com/v1`) while embedding stays local. Script must handle dual endpoints.

#### ⚠️ FAILED APPROACH: Context Injection (do NOT use)

**Context injection PREPENDING framework definitions into embed text was tried and FAILED.** Grounding rate dropped from 16.1% → 12.0%. The definition text created false similarities across documents — a card from doc 5 embedding against chunks from doc 7 would match because both mention the parent framework, not because they share actual content. **This approach is documented as a failure. Do not implement it.**

#### Patch 1: Document ID Scoping (The Actual Fix)

**Real root cause**: Cards store `source_doc: 5` (integer count from Phase 3 metadata) while chunks store `doc_id: "doc-413e38bbc..."` (actual KV store keys). **Zero mapping exists between them.** The similarity search iterates ALL 394 documents' chunks for every card — 99% noise. The 64 cards that appeared grounded only matched by random keyword overlap with unrelated documents.

**Fix — two parts:**

**Part A: Reconstruct doc_ids in Phase 3 metadata (no LLM calls needed)**

Phase 3's `find_relevant_docs()` function deterministically scores documents by keyword frequency. It finds the right documents but only stores the count. Re-run the scoring and inject actual doc_ids:

```python
# Deterministic reconstruction — same scoring function, same data
relevant_docs = find_relevant_docs(framework_keywords, entities_data, docs_data)
fw_data["_metadata"]["doc_ids"] = [d for d in relevant_docs 
    if len(docs_data[d].get("content", "")) >= 200]
```

Script: `phase3_reconstruct_doc_ids.py` — runs in seconds, no LLM calls, 100% deterministic.

**Part B: Scope similarity search in Phase 4**

Build `chunks_by_doc` index for O(1) lookup, then only search chunks belonging to the card's framework:

```python
# In verify_cards_against_chunks():
fw = card.get("framework", "")
if fw_doc_ids and fw in fw_doc_ids:
    for doc_id in fw_doc_ids[fw]:
        for chunk in chunks_by_doc.get(doc_id, []):
            sim = cosine_similarity(card_emb, chunk_emb)
            similarities.append((sim, chunk))
```

**Noise reduction**: from 394 docs × ~50 chunks = ~19,700 per card → 20 docs × ~50 chunks = ~1,000 per card. **95% noise elimination.**

#### Patch 2: Tagging Schema Enforcement + Fallback

**Problem**: LLM can skip cards in free-form JSON responses. "Use canonical URLs" lost its tag entirely because the LLM didn't return an entry for it.

**Fix 2a — Strict prompt instruction**: Add to `build_tagging_prompt()`:
```
CRITICAL: You MUST return EXACTLY one entry for EVERY item in the input list.
Do NOT skip any item. If an item's target entity is not obvious, infer it from the claim text.
```

**Fix 2b — Mandatory fallback**: After parsing LLM response, for any entry with empty `target_entity`:
```python
# Extract first noun phrase from raw_content as last resort
match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})', raw_content)
if match:
    entry['target_entity'] = match.group(1)
    entry['action_directive'] = 'understand'
```

This guarantees zero dropped tags — every card gets at least a noun-phrase fallback.

#### Patch 3: Split Endpoint Auth Handling

**Problem**: All `:cloud` models require authentication via Ollama Cloud API (`https://ollama.com/v1`). The local Ollama instance (`192.168.4.148:11434`) may also require auth for chat endpoints. But embedding still works locally without auth.

**Fix**: Split endpoints:
- **Chat endpoint**: `https://ollama.com/v1/chat/completions` with `Authorization: Bearer {OLLAMA_API_KEY}`
- **Embed endpoint**: `http://192.168.4.148:11434/api/embed` (no auth)

Load API key from dotenv at script start:
```python
from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/.hermes/.env'))
_api_key = os.getenv('OLLAMA_API_KEY')
```

Use in `call_ollama_chat()`:
```python
headers = {"Authorization": f"Bearer {_api_key}"} if _api_key else {}
response = requests.post(OLLAMA_CHAT_URL, json=payload, headers=headers)
```

#### Checkpoint Reset After Patches

When re-running a patched pipeline, reset the checkpoint file to all zeros and strip all existing embeddings/tags/spans from cards:
```python
checkpoint = {
    "tagged_count": 0, "embed_count": 0,
    "chunk_embed_count": 0, "verify_count": 0,
    "soft_membership_done": False
}
for card in flashcards:
    for key in ['embedding', 'source_spans', 'cross_framework_memberships',
                'target_entity', 'action_directive']:
        card.pop(key, None)
    card['verification_status'] = 'pending'
```

#### Grounding Target

**Before patches (no scoping)**: 86/534 (16%) — random keyword overlap only  
**With doc scoping fix**: >70% projected — 95% noise eliminated  
**If still below 70%**: check embedding model quality or verification prompt threshold

### Script Locations
```
/home/steve/lightrag-apps/knowledge-synthesis/extractions/{architect}/
├── phase1_clean.py
├── phase3_extract.py
├── phase5_graph.py            # Phase 5: frameworks.json + dependency graph
├── phase1_clean_graph.json
├── phase2_communities.json
├── phase3_extractions.json
├── phase4_flashcards.json
├── phase5_frameworks.json     # Final output: Tier 1/Tier 2 + edges
├── phase5_dependency_graph.html    # D3 interactive visualization
├── phase5_dependency_graph.mermaid
├── phase5_dependency_graph.json    # Cytoscape/D3 compatible
└── ... (intermediate artifacts)
```

## Koray Gubur Results (Reference)

| Phase | Input | Output | Key Findings |
|-------|-------|--------|-------------|
| 1 | 10,480 entities | 1,043 entities | 1,997 noise filtered |
| 2 | 1,043 entities, 1,434 edges | 12 framework communities | Top 3: Topical Authority & Entity-Based SEO (140 entities), Multi-Channel Digital Acquisition (129), Accessibility-Driven Technical SEO (79) |
| 3 | 12 communities → 9 extracted | Deep framework descriptions | Merging overlapping names resolved 12 → 7 distinct frameworks; upgraded to deepseek-v4-flash (20 docs per extraction, 8x more context) |
| 4 | 534 flashcards | 144 GROUNDED, 390 UNVERIFIED | 27.0% grounding rate with doc-scoping. 118 cross-membership cards. Holding at epistemic limit — extractive verification vs abstractive synthesis ceiling reached. |
| 5 | Phase 3 + Phase 4 | `phase5_frameworks.json` (321KB) | 12 frameworks, 126 typed edges (42 depends_on, 42 supports, 42 cross-membership). Epistemic stratification: Tier 1 (144 computable rules, grounded) vs Tier 2 (390 heuristic context, unverified). D3 interactive graph + Mermaid + Cytoscape formats. |

### Phase 5: Epistemic Stratification

The final `phase5_frameworks.json` hardcodes the Tier 1/Tier 2 distinction:

- **Tier 1 (Computable Rules):** 144 cards with verified `source_span` — these feed the automated Gap Score engine in the Domain KG. Every card has a source document paragraph anchoring it.
- **Tier 2 (Heuristic Context):** 390 cards — architectural synthesis that's true of the framework but not directly quoted in any source. These provide narrative context for content briefs but do NOT trigger automated gap audits.

Tier boundary is strict: Tier 1 cards carry `source_span`; Tier 2 cards omit it.

### Dependency Graph Edge Types

| Type | Count | Meaning |
|---|---|---|
| `depends_on` | 42 | Framework A requires understanding of Framework B (directed) |
| `supports` | 42 | Reverse of depends_on (Framework B is a building block for A) |
| `cross_membership` | 42 | Soft edges from Phase 4 embedding similarity (bidirectional) |

Most central framework: **SEO Case Study Methodology** (centrality 1692 — depends on 7 other frameworks). Most grounded: **Python & Data-Driven SEO** (47.1%).

## Key Pitfalls

1. **Don't use `/query` endpoint for discovery** — it's semantic similarity search, not exhaustive extraction. Top-k chunks ≠ full corpus.

2. **Don't ask docs "what frameworks?"** — a document doesn't know it's part of a framework. Hypothesis-driven extraction is categorically better.

3. **Entity graph is noisy** — LightRAG extracts everything as entities (HTML tags, word lists, HTTP codes). ~20% is noise. Phase 1 filtering is essential.

4. **Louvain produces many communities** — at typical resolution, 300+ communities emerge but most are singletons. Only size ≥ 5 communities carry signal.

5. **Community overlap is expected** — multiple communities often describe the same framework at different granularities. Phase 4 merge is required.

6. **Shallow embed inputs kill grounding** — `nomic-embed-text` cannot match short card text against full paragraphs. Always inject parent framework definitions into embed inputs. Without context injection, grounding rate is ~16%; with it, >70%.

7. **LLM silently drops cards** — free-form JSON tagging prompts will skip cards. Always add "CRITICAL: return EXACTLY one entry per item" + regex fallback that scrapes the card's own text as a last resort.

8. **Split endpoint auth** — `:cloud` models require cloud API (`ollama.com/v1`) with API key. Embed models run locally without auth. Do NOT try to call cloud models through local Ollama — they'll return 401.

## Reuse for Other Architects

To run this pipeline for a new architect:
1. Ensure LightRAG ingestion is complete (docs + entities + relations exist)
2. Copy the phase scripts to `extractions/{architect-name}/`
3. Update `WORKSPACE` path in each script to point to the architect's LightRAG workspace
4. Run phases sequentially: 1 → 2 → 3 → 4 → 5
5. Each phase validates the previous — don't skip phases
