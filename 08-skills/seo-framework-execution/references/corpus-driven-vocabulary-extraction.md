# Autonomous Seed Query Generation — Methodology & Code

**Part of:** seo-framework-execution skill (formerly its own skill; absorbed 2026-06-01)
**Status:** Proven methodology — validated on quann.homes real estate, portable to any industry  
**Date:** 2026-05-28 (moved 2026-06-01)

---

## Problem Statement

The Phase 1 vocabulary extraction pipeline requires 5-10 seed queries to feed into the SERP scraper. If we hand-write these queries (e.g., "Katy TX home buyer guide"), the framework is locked to one industry. A Chicago dental clinic would require rewriting all queries.

**Solution:** The Domain Knowledge Graph already contains everything the engine needs to generate seed queries. The `get_anchor_entities()` function extracts high-signal entities, and an LLM combiner pairs them with intent modifiers to produce queries. No human input needed.

---

## Full Methodology

### Step 1: Load the Domain KG

Combine three data sources:
- **EAV triples** (`04-eav-triples/eav-triples.md`) — entity-attribute-value relationships
- **Central entity** (`02-central-entity/central-entity.md`) — canonical entity definition
- **JSON-LD schemas** (`phase2-schemas.json`) — structured data with `knowsAbout` arrays

### Step 2: Structural Extraction

**CRITICAL:** Use structural/regex parsing, not manual blacklists.

Parse markdown tables with structural awareness:
- Skip header rows (`|---|---|` dividers)
- Discard columns whose values match structural patterns: table column headers (`Entity`, `Attribute`, `Value`, `Schema`, `Type`, `Notes`), schema-internal types (`RealEstateAgent`, `ProfilePage`, `Person`)
- Extract entity-attribute-value triples from remaining rows

This filter is domain-agnostic. It works identically for real estate, dentistry, or any vertical because it filters on document structure, not domain vocabulary.

### Step 3: Score Entities

For each unique entity, compute:
```
salience = frequency × (1.0 + unique_attributes × 0.3) × (1.0 + connections × 0.2)
```
Where frequency = count of appearances, attributes = distinct attribute names, connections = entities sharing attributes or values.

### Step 4: Deconflict by Type

Classify top 10-15 entities by type (brand, location, service, product) to avoid generating redundant queries. Pick the top entity from each type to ensure diverse coverage.

### Step 5: Generate Compound Queries

Combine anchors with intent modifiers using an LLM call:
```
For top 5 deconflicted entities × 4 intent modifiers (guide, cost of, comparison, how to):
  Generate: "{intent} {entity}" queries
  
Then generate 2-3 compound queries:
  "{service} in {location}" or "{product} guide {location}"
```

### Step 6: Expert Review

Present 10-12 generated queries to the domain expert. They confirm, reject, or modify before scraping.

---

## Code: generate_seed_queries.py

See `scripts/generate_seed_queries.py` for the reference implementation. Copy to new project root and run:
```
python3 generate_seed_queries.py /path/to/eav-triples.md /path/to/central-entity.md /path/to/phase2-schemas.json
```

Outputs `phase1-auto-seeds.json` with 12 seed queries.

---

## Validation Criteria

A successful seed generation:
- [ ] Produces 5-12 queries
- [ ] Mixes single-entity and compound queries
- [ ] Covers brand, location, service, and product entity types
- [ ] Contains zero structural artifacts (no "Schema", no "Entity", no numbered rows)
- [ ] Would produce different queries for a different industry — no hardcoded terms
- [ ] Queries are specific enough to return topically relevant SERPs

---

## Why This Matters

This is the architectural difference between a one-off SEO script and a scalable SaaS platform. The seed generator removes the last human dependency from the pipeline. Plug in any Domain KG, and the framework self-configures without code changes.
