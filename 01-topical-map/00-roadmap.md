# SEO-quann.homes — Master Roadmap

**Status:** Phase 2 Initialization  
**Last Updated:** 2026-05-24  
**Architecture:** 38 files, 11 precision layers  
**Goal:** Build a semantic DAG of content pillars with intent-locked predicates, centroid depth ratios, and ontological entity anchoring — then feed the output into Phase 3's Content Brief Generator.

## Architecture

```
SEO-quann.homes/
├── 00-roadmap.md                                  # ← this file
├── MASTER-GAP-LIST.md                             # Combined gap list + project state
├── QUAN-CALL-AGENDA.md                            # 6-block interview agenda
├── 01-source-context/source-context.md            # Layer 1: Brand identity × business model
├── 02-central-entity/central-entity.md            # Layer 2: Quan Nguyen entity profile
├── 03-web-entity/
│   ├── web-entity.md                              # Layer 3: External profile audit
│   └── entity-disambiguation-plan.md              # Layer 8: sameAs, collision prevention
├── 04-eav-triples/eav-triples.md                  # Layer 4: Entity-Attribute-Value extraction
├── 05-query-templates/query-templates.md          # Layer 5: 8 query patterns
├── 06-topical-map/
│   ├── topical-map.md                             # Layer 6: Pillars, centroids, spokes
│   ├── topical-borders.md                         # Semantic boundary definitions
│   ├── information-gap.md                         # Zero-volume nodes
│   └── contextual-bridges.md                      # Cross-cluster links
├── 07-content-briefs/
│   ├── content-briefs.md                          # 9-field brief template
│   ├── lexical-richness.md                        # Knowledge Domain Terms
│   └── cost-of-retrieval.md                       # Page Character Analysis
├── 08-backlink-strategy/backlink-strategy.md      # Contextual relevance > DA
└── 09-research/
    ├── algorithmic-authorship-rulebook.md          # Phase 3.5 Layer 1: 6+2 rules
    ├── distributional-semantics.md                 # Phase 3.5 Layer 2: n-gram clusters
    ├── serp-feature-mapping.md                     # Phase 3.5 Layer 3: per-spoke SERP
    ├── proactive-entitization-strategy.md          # Phase 3.5 Layer 4: Wikidata, GBP
    ├── momentum-shock-publishing.md                # Phase 3.5 Layer 5: 12 pages/5 days
    ├── knowledge-graph-api-audit.md                # Phase 3.5 Layer 6: KG API verification
    ├── predicate-intent-mapping.md                 # Phase 3.6 Layer 7: verb→intent
    ├── truth-range-consensus-mapping.md            # Groundedness Protocol
    ├── knowledge-domain-terms-expert.md
    ├── functional-intent-discovery.md
    ├── semantic-distance-border-definition.md
    ├── historical-identity-resurrection.md
    ├── cost-of-retrieval-per-spoke.md
    ├── data-collection-setup.md
    ├── competitor-analysis-framework.md
    ├── web-entity-audit-framework.md
    ├── eav-triples-expansion-blueprint.md
    ├── existing-content-gap-analysis.md
    ├── methodology-phase2-reference.md
    └── consensus-baseline.md
```

## Central Entity Anchor Values

- **Quan Nguyen**, License #0774451, REAL BROKERAGE, "The Quantum Team"
- Service areas: Katy, Houston, Austin, Dallas, Rio Grande Valley
- Phone: (832) 400-3152, Email: quan@thequantumteam.net
- Domain: quann.homes (first archived April 2025 — clean slate)

## Data Sources

| Source | Contents | Status |
|---|---|---|
| Domain KG | 381 entities, 289 with graph relations, 24 docs | ✅ Live |
| Kernel v2.1 | 23 rules, 53 contaminations, 46 bridge failures | ✅ Live |
| Source Context | Approved brand identity | ✅ In skill |
| RuleBridge | 15 deterministic + 116 directive checks | ✅ Live |
| seo-topical-map skill | Complete methodology, 11 layers | ✅ Reference |
| SEO RAG (port 8001) | holisticseo.digital (empty workspace) | ⚠️ Use skill |
| Quann Chat RAG (port 8001) | quann.homes content | ⚠️ Use KG directly |

## Build Order (Strict)

1. **Foundation (Layers 1-3):** Source Context → Central Entity → Web Entity
2. **Alignment Audit:** Separate confirmed from mentioned
3. **Semantic Extraction (Layers 4-5):** EAV Triples → Query Templates
4. **Topological Structure (Layer 6):** Topical Map → Borders → Gaps → Bridges
5. **Connective Tissue (Layers 3.5):** 6 precision layers
6. **Neurological Precision (Layers 3.6):** 5 algorithmic rigor layers
7. **Execution:** Wire into Phase 3 Content Brief Generator

## Key Constraints

- **Never speculate:** Build only from confirmed content + approved Source Context
- **GROUND, DON'T GUESS:** Services mentioned in KG with zero pages = gray zone
- **Truth ranges mandatory:** Hard numeric bounds with sources (Texas prop tax ~1.80%, FHA 3.5%)
- **No per-page LLM calls:** Deterministic where possible, directive injection capped at 8
- **Centroid-first:** Every gap detection anchored to page centroid via graph traversal
