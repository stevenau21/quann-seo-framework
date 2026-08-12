# Query Network Classification — Data-Artifact Node Specification

> **Source:** Koray Lecture 1, lines 15-33
> **Status:** MISSING from dependency DAG (2026-05-26)
> **Type:** Translation layer between abstract framework sequence and concrete client execution

## The Problem

The `dependency_dag.py` 3-Vector Engine models 12 framework→framework edges. Topological sort produces the correct framework execution order. But the engine has zero data-artifact nodes — intermediate data products that frameworks produce and consume.

The specific gap: Koray requires Query Network Classification between Entity-Semantic Bridge (Phase 4) and Topical Authority Assembly (Phase 6). Without it, the topical map starts at the service level and the URL hierarchy has no broad-layer borders.

## What Koray Prescribes

> "Find the most popular entity type in the query networks. Classify by local proximity — continents → countries → cities. Then dive into lexical relations (visa, climate). The closest relevant country comes from user behaviour, not encyclopedic similarity."

This means: before building ANY topical map, the pipeline must determine what dimension the map descends by.

## The Missing DAG Node

```
Entity-Semantic Bridge (Phase 4)
        ↓ produces
  Domain Knowledge Graph
        ↓ produces
  Query Network Classification  ← NOT MODELED
        ↓ consumed by
  Topical Authority Assembly (Phase 6)
```

Without this node, topological sort is correct for framework ordering but blind to the data flow.

## Classification Algorithm

1. **Extract entity type frequency distribution** from Domain KG
2. **Identify dominant entity type:** geographic (city/state/zip) | product-category | service-category | persona | temporal | industry-vertical
3. **Group by proximity** based on dominant type:
   - **Geographic:** continent → country → state → county → city → neighborhood → service
   - **Product taxonomy:** category → subcategory → brand → SKU → attribute
   - **SaaS:** industry → vertical → use-case → feature
   - **Local service:** metro area → city → neighborhood → service type
4. **Build broad-layer map borders** — these form the top levels of the URL hierarchy
5. **Then narrow** to service attributes, entities, spokes

## Why This Is Dependency Resolution

This is NOT a missing phase. It's a missing dependency edge. The engine already does framework ordering — it just needs to model the intermediate data artifacts too.

The user identified this correctly: "it's dependency resolution." The fix is structural — extend `dependency_dag.py` to include data-artifact nodes (Query Network Classification, Contextual Vectors, Information Tree, URL Structure Derivation) alongside framework nodes. Topological sort will then naturally enforce the broad→narrow descent without any special-case gate logic.

## Examples

| Client | Dominant Entity Type | Broad→Narrow Descent |
|---|---|---|
| Buyer's agent, Katy TX | Geographic | Texas → Houston Metro → Katy → Neighborhoods → Buyer Services |
| Dentist, Phoenix AZ | Geographic | Arizona → Maricopa County → Phoenix → Scottsdale → Dental Services |
| SaaS project management | Industry-vertical | Enterprise → Mid-Market → SMB → Feature Categories |
| E-commerce sneakers | Product category | Athletic → Running → Trail → Brand → Model |

## Implementation

The fix goes into `dependency_dag.py`:
- Add `DATA_NODES` dict alongside `FOUNDATIONAL_LAYER`
- Add edges: Entity-Semantic Bridge → Query Network Classification → Topical Authority
- Extend phase chunking to include data-artifact phases
- Output includes `data_artifacts` array in `phase-dependencies.json`
