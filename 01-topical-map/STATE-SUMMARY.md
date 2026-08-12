# Quann.Homes — SEO Architecture State Summary

**Date:** 2026-05-05
**Status:** Architecture Validated — Ready for EAV triple scoping, then content drafting.

---

## Architecture Chain (10-Layer Methodology)

```
Source Context (gate) → Topical Borders (scope) → Topical Map (centroids)
→ Content Brief Template (9-field) → NLI Entailment Paths (cross-page)
→ Algorithmic Authorship Rulebook (how to write) → Predicate-Intent + SRL
→ Distributional Semantics (n-grams) → Contextual Bridges (linking)
→ Information Gap (unique facts) → Proactive Entitization (entity creation)
→ Momentum & Shock Publishing (batch sequence)
```

Every arrow is documented in our files. No dependency on external tools.

---

## Central Entity vs Source Context

| Concept | Value |
|---|---|
| **Central Entity** | Texas Residential Property (the broad domain Quan operates in) |
| **Source Context** | Strategic Acquisition / bridging buyer knowledge gaps (how Quan makes money) |

Two different things. Central Entity defines the Outdoor Section (statewide authority). Source Context defines the Core Section (monetization). Both established at launch via Batch 1.

---

## Batch 1 — Final Scope (6 Pages, Simultaneous Shock Drop)

### Core Section (Monetization)

| # | Page | IR Zone | Centroid Status | Architecture |
|---|---|---|---|---|
| 1 | About Quan Nguyen | `/about/` | ENTITY_ANCHOR | Hard EAV first → narrative second |
| 2 | FTHB Process Hub | `/guides/` | PRIMARY_CENTROID | ~1,200 words, links to satellites |
| 3 | Katy Neighborhood Hub | `/areas/` | PRIMARY_CENTROID | Comparison hub, HTML tables |

### Outdoor Section (Statewide Authority)

| # | Page | IR Zone | Purpose |
|---|---|---|---|
| 4 | Texas Property Tax Structure | `/guides/` | Statewide: Harris, Fort Bend, Travis, Dallas, Hidalgo counties |
| 5 | Texas Flood Zones & Insurance | `/guides/` | Coastal, inland, floodplain classifications |
| 6 | Texas Residential Market Fundamentals | `/guides/` | Regional trends, growth corridors |

---

## Key Architectural Decisions

### Page Architecture
- **Hubs, not monoliths:** FTHB/Katy pages are hub pages linking to satellites — not monolithic 3,000-word guides
- **Macro Context (Top):** H1 + first paragraph = "the one thing" the page teaches
- **Micro Context (Bottom):** Supplementary content with contextual bridges to adjacent topics
- **Contextual Bridges:** Anchor text matches target H1 exactly. Never generic ("click here")

### Writing Rules
- **Strategic Leverage Frame:** Stats as buyer outcomes (savings, speed, leverage), NOT agent vanity (volume, transaction count)
- **About Page Order:** Hard EAV assertions first (license, certifications, affiliations), strategic narrative second. Engine must ground the entity before attributing authority
- **Modality Matching:** "Should I...?" headings use modal; next sentence grounds in declarative fact. All other content: modality banned
- **SRL Enforcement:** Buyer is always Agent of verbs — never passive Object. "The buyer leverages concessions" not "Concessions are negotiated"
- **Declaration First, Condition Second:** State the fact, then attach conditions
- **Entity-specific predicates:** Valid verb sets per entity type (home prices = rise/fall/average, closing costs = include/exclude/average)

### Depth & Format
- **Centroid depth ratio:** 4-5x more detailed than satellites
- **Centroid format requirement:** Minimum 3 formats (table + list + prose)
- **Satellite format:** Single format acceptable
- **Measurement units:** Centroids min 3 ($, %, time/distance). Satellites min 1
- **Unique Information Gain:** Min 3 facts per page not in top 3 SERP results

### Cross-Page Enforcement
- **NLI Entailments:** 72 cross-page Tier 1 requirements across 12 spokes
- **Centroid Damage Rule:** Gap on PRIMARY_CENTROID cascades to all satellites in that cluster
- **Pre-publish NLI Gate:** Every page's declarative claims verified against entailment matrix before publishing
- **Redundancy Filter:** "Delete page → does world lose information?" Yes → publish. No → rewrite

### Publishing
- **Simultaneous drop:** 6 pages together triggers Broad Index Refresh
- **48-hour window:** Tolerated for staggered deployment (centroids first, outdoor nodes second)
- **Crawl quota tactics:** Sitemap resubmission, GSC manual index requests, social signals
- **No orphan pages:** Every page reachable within 2 clicks from nav

---

## Batch Sequence (Full Plan)

| Batch | When | Pages | Cumulative |
|---|---|---|---|
| **Batch 1** | Day 1 | 6 (About + 2 Centroids + 3 Outdoor) | 6 |
| **Batch 2** | Day 2-3 | 4 (Out-of-State, Builder Incentives, DPA, FHA/Conventional) | 10 |
| **Batch 3** | Day 4-5 | 5 (Closing Costs, Pre-Approval, Schools, Commute, New Construction) | 15 |

**Total: 15 pages.** 12 Core + 3 Outdoor anchors. Remaining Outdoor nodes (~3) in later batches.

---

## What's Changed (From Original Plan)

| Original Plan | Revised | Reason |
|---|---|---|
| 3-page Batch 1 | 6-page Batch 1 | Outdoor Section required for entity authority at launch |
| Katy-only Outdoor | Texas-statewide Outdoor | Quan's Central Entity is Texas, not just Katy |
| 3,000-word monolith pages | Hub-and-spoke (~1,200 hubs) | Monoliths create Contextual Noise; hubs+satellites cheaper for extraction |
| Agent vanity stats | Strategic leverage frame | Source Context demands buyer-outcome framing |
| Sequential publishing | Simultaneous shock drop | Triggers Broad Index Refresh and crawl quota increase |

---

## Outstanding Dependencies

| Dependency | Status |
|---|---|
| Framer access | ❌ Not obtained |
| Knowledge Graph API key | ❌ Not obtained |
| Public market data (9 points) | ❌ Not collected (needed for EAV scoping) |
| External profiles (GBP, Zillow, HAR) | ❌ Not audited |
| Competitor analysis | ❌ Not done |
| HAR market report from Quan | ❌ Not obtained |

---

## Files Updated (2026-05-05, final revisions)

| File | What Changed |
|---|---|
| `00-roadmap.md` | Batch 1 scope (6 pages), status, architecture decisions |
| `MASTER-GAP-LIST.md` | Tiered priority refactored for 3-batch sequence |
| `06-topical-map/topical-map.md` | Added Pillar 4 (Outdoor Section — Statewide Authority) |
| `09-research/momentum-shock-publishing.md` | Batch 1 expanded to 6 pages with Outdoor nodes |
| `09-research/seo-agent-brief-validation.md` | New — SEO agent feedback preserved |
| `STATE-SUMMARY.md` | New — this file, comprehensive architecture reference |

---

## Next Action

**EAV Triple Scoping** — Identify Root, Rare, and Unique attributes for all 6 Batch 1 pages before drafting any content. Then write Batch 1 pages following the 9-field content brief template and 10-layer methodology.
