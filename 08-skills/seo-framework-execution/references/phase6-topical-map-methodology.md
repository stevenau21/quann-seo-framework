# Phase 6 — Topical Map Synthesis Methodology

## When This Applies
Phase 6 (Topical Authority Assembly) synthesizes three inputs into a single topical map deliverable:

1. **Phase 1 — Vocabulary Bank** (domain-specific terms from SERP corpus)
2. **Phase 4 — Entity-Semantic Bridges** (contextual connections between entities)
3. **Koray Methodology** (Quarice Framework from transcript KG, port 8014)

## The Synthesis Pipeline

### Step 1: Gather Inputs
- `06-topical-map/phase1-vocabulary-bank.json` — 94 terms across 7 buckets (government programs, tax districts, relocation, etc.)
- `06-topical-map/contextual-bridges.md` — 6 bridges (Quan↔Katy, FTHB↔TSAHC, etc.)
- Koray transcripts KG (port 8014) — Quarice Framework, 9-step topical map process, content brief template, root/seed/node architecture
- `phase4_flashcards.json` — 534 cards for rule citation

### Step 2: Run the Data Pipeline Auditor (MANDATORY)
```bash
python3 /tmp/data_pipeline_auditor.py \
  --target http://localhost:8014 \
  --baseline /home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur/phase4_flashcards.json \
  --out-dir /home/steve/SEO-quann.homes/07-content-briefs/
```
This produces `phase1-5-lecture-patches.md` and `transcript-raw-data.json`. The raw data captures the full KG state even when structural extraction has false negatives.

### Step 3: Define Source Context + Central Entity
From `master-operating-blueprint.json`:
- Agent, brokerage, vertical, geography, monetization
- Central entity (the person/business the site IS about)
- Central Search Intent (what search query does the homepage answer?)

### Step 4: Build Raw Topical Map
Cross-reference vocabulary buckets with bridge connections to produce Entity–Attribute pairs. Every attribute gets assigned:
- SERP-validated vocabulary terms (from Phase 1)
- Bridge connection (from Phase 4)
- These become attribute-level rows in the raw map table

### Step 5: Partition Core vs. Outer
Per Koray methodology:
- **Core Section** = directly tied to source context and monetization (the pages that convert)
- **Outer Section** = attributes that prove broader relevance and build historical data

### Step 6: Process into URL Structure
- 3-layer hierarchy: Root → Seeds → Nodes
- No word repetition across URLs
- Logical crawl paths
- Quality Note on root page (linked from every page footer)

### Step 7: Generate Contextual Vectors Per Page
For EACH node, produce:
- **Macro Context** — H1 + title tag (appears in search results)
- **Predicate Family** — from Phase 1 approved 8 families (FIND, LEARN, COMPARE, PROTECT, SAVE, BUILD, MOVE, INVEST)
- **Context Terms** — assigned vocabulary from Phase 1 buckets
- **Ordered H2/H3 headings** — the contextual vector (question format, logical flow)
- **Bridge** — cross-page anchor text connection

### Step 8: Build Bridges Table
Source page → Anchor Text → Target Page → Purpose
Every bridge uses anchor text matching the target page's H1, placed at least once BEFORE the actual link.

### Step 9: Publishing Order
Per Koray batch methodology:
- Batch 1: Core service pages (highest conversion)
- Batch 2: Location authority
- Batch 3: Financial context
- Batch 4: Market depth
- Batch 5: Trust layer (about/contact, last)

### Step 10: Copywriter Reference Card
Produce:
- Vocabulary-by-page-intent table (which terms go on which page type)
- Predicate families table (8 approved verb sets)
- Banned words table (modality, empty adjectives, fluff, passive starts)
- Pre-write checklist (9 questions)

## Output Structure

The deliverable (`phase6-topical-map.md`) contains these sections:
1. Source Context & Central Entity
2. Raw Topical Map (all entity–attribute pairs with vocab + bridges)
3. Core vs. Outer Partition
4. Processed Topical Map (macro context + vector + bridge per page)
5. URL Structure (root → seed → node, 3 layers)
6. Content Brief Template (9 components per page)
7. Contextual Bridges (cross-page connections table)
8. Publishing Order & Momentum (5 batches, ~8 weeks)
9. Copywriter Reference Card (vocab, predicates, banned words, checklist)
10. Page Count & Workload Summary

## Pitfalls

- **Structural regex false negatives on narrative prose.** The `data_pipeline_auditor.py` uses keyword/regex extraction that fails on Koray's narrative teaching style. Only ~30% of queries return structured output. The raw KG responses ARE rich — do NOT discard them. The `transcript-raw-data.json` captures everything. When extraction undercounts, read the raw data directly.
- **Phase 5 scope creep.** Technical SEO is deferred maintenance. When business priority is content production, bypass Phase 5 for Phase 6. The correct sequence is 0→1→2→3→4→6→5→7.
- **One bridge per page.** Do not scatter CTA bridges throughout content. One bridge at the END of the page, after value is delivered.
