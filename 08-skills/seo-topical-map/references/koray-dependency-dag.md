# Koray Dependency Extraction Engine

Reusable Python engine at `SEO-quann.homes/dependency_dag.py`. Builds a DAG from Koray's 12-framework dependency network, applies topological sort, and chunks into operational phases.

## Three Vectors of Dependency Extraction

| Vector | Source | What It Captures |
|---|---|---|
| Vector 1 | Explicit `depends_on` in framework metadata | Direct parent-child relationships (the boss — always overrides 2 and 3) |
| Vector 2 | `cross_framework_edges` with strength > 0.5 and ≥5 shared cards | Implicit connections discovered via NLP card overlap |
| Vector 3 | Shared `external_dependencies` keywords (≥8 overlap) | Latent connections through common external knowledge bases |

## Cycle Resolution Rules

1. When a cycle is detected, Vector 1 (foundational layer) always wins.
2. Lower `FOUNDATIONAL_LAYER` number = more foundational.
3. Same-layer tiebreaker: the framework with MORE `depends_on` entries is pruned first (it's less foundational within its layer).
4. Same-deps tiebreaker: both are pruned, direction determined by layer parity.
5. Mutual 2-cycles (A↔B): brute-force break, higher-layer edge pruned.

## Foundational Stratification

```
Layer 0: content-quality-linguistics, python-data-driven-seo   (Pure primitives)
Layer 1: knowledge-graph-structured-data, conversion-growth     (Core SEO concepts)
Layer 2: seo-information-retrieval                              (Information science)
Layer 3: entity-based-seo, semantic-seo                         (Entity-Semantic bridge)
Layer 4: technical-seo, multilingual-international-seo          (Execution layer)
Layer 5: topical-authority, holistic-seo                        (The Crown)
Layer 6: seo-case-study-methodology                             (Meta-reflection)
```

## Output: Phase-Dependencies.json

The engine emits a JSON file with:
- `topological_order`: sorted framework IDs
- `phases`: grouped operational phases with card counts
- `metadata`: engine version, vector config, cycle resolution rules

## Usage

```bash
cd /home/steve/SEO-quann.homes
python3 dependency_dag.py
```

Run before ANY content work. Phase 1 (Foundational Primitives) must execute before any page is built. The mathematical truth: 12 frameworks, 8 natural cycles, 534 cards — you cannot manually determine the correct order. Let the DAG decide.
