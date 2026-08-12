# Master Gap List — Quann.Homes (Final, Grounded)

**Date:** 2026-05-05 (Final revision after alignment audit)
**Last Updated:** 2026-05-24 (Session 3 — Category C entity discovery complete, 8 new issues + 3 new patterns)
**Status:** Prerequisites progressing. ✅ Category A (SEO interview), ✅ Category B (market data, 10/10 HIGH confidence), ✅ Category C (entity discovery, 11 profiles across 7 platforms). Remaining: D (Framer access), E (KG API key), F (tech SEO prep), G (competitor analysis)

---

## What Quan Covers (Confirmed)

| Area | Evidence |
|---|---|
| First-time home buyer education | 2 blog posts exist |
| Out-of-state relocation | 1 massive 11-part guide exists |
| Builder incentives / getting the best deal | Homepage differentiator |
| Buyer representation | Core focus per approved Source Context |

---

## What Quan Has Signaled He Wants (Via Source Context)

| Area | Signal |
|---|---|
| Area guides for Katy/Houston | "Through accessible area guides" |
| Trust/credibility content | Testimonials on homepage, footer entity data |

---

## Gap Categories

### Category A: Quan Interview (15 min — no tools needed) ✅ COMPLETE (2026-05-24)

| # | Question | Answer |
|---|---|---|
| 1 | Years of experience? | 5 years |
| 2 | Languages spoken? | English + Vietnamese |
| 3 | Certifications? | ABR, GRI, C2EX, MRP, PSA |
| 4 | Professional associations? | NAR, TAR, HAR, Katy Chamber, AREAA |
| 5 | Awards or recognition? | None. Frame real achievements instead (years licensed, certs earned, families served) — no fabrication. |
| 6 | FTHB spoke priorities? | ALL matter. No pruning. All FTHB spokes are tier 1. |
| 7 | Seller/investor content? | Deferred, not deleted. Eventually yes, not now. |

### Category B: Public Market Data (30 min — no proxies)

| # | Data Point | Source |
|---|---|---|
| 1 | Katy median home price | Redfin Data Center (public) |
| 2 | Katy price/sqft | Redfin (public) |
| 3 | Houston metro median price | Redfin (public) |
| 4 | Texas avg closing costs % | Bankrate (public article) |
| 5 | Harris/Fort Bend county property tax rates | Texas Comptroller (public PDFs) |
| 6 | FHA loan limits — Texas | HUD website (public) |
| 7 | Average Texas mortgage rate | Freddie Mac PMMS (public) |
| 8 | Katy ISD / surrounding school ratings | TEA website (public) |
| 9 | Katy commute times (to downtown, Energy Corridor) | Google Maps (manual lookup) |

### Category C: Quan-Specific Data (5 min — ask Quan) ❌ SKIPPED

| # | Request | Result |
|---|---|---|
| 1 | HAR market report export (MLS data: DOM, inventory, sold count, active listings) | Skipped — Quan cannot provide. Use public data only. |

---

## What We Don't Know (And Shouldn't Guess)

### External Profiles
- Google Business Profile: unknown if exists
- Zillow agent profile: unknown
- Realtor.com: unknown
- HAR.com agent profile: unknown
- LinkedIn: unknown
- Katy Chamber membership: unknown

**Approach:** Manual one-time search. Don't build automated audit flows. Don't assume they exist.

### Competitors
- Who are Quan's actual competitors? Not searched.
- What content do they cover? Not reviewed.

**Approach:** 2-hour manual Google session. Visit top sites. Note what they cover. Not an automated crawl.

---

## Build Priority (What to Do First)

### Tier 1 — Batch 1 (6 pages, simultaneous shock drop)

**Core Section (Monetization):**
| # | Page | IR Zone | Centroid Status |
|---|---|---|---|
| 1 | About Quan Nguyen | `/about/` | ENTITY_ANCHOR |
| 2 | First-Time Home Buyer Process (Hub) | `/guides/` | PRIMARY_CENTROID |
| 3 | Katy Neighborhood Guide (Comparison Hub) | `/areas/` | PRIMARY_CENTROID |

**Outdoor Section (Statewide Authority):**
| # | Page | IR Zone | Purpose |
|---|---|---|---|
| 4 | Texas Property Tax Structure | `/guides/` | Statewide authority anchor — Harris, Fort Bend, Travis, Dallas, Hidalgo counties |
| 5 | Texas Flood Zones & Insurance | `/guides/` | Statewide authority anchor — coastal, inland, floodplain classifications |
| 6 | Texas Residential Market Fundamentals | `/guides/` | Statewide authority anchor — regional trends, growth corridors |

**Architecture decisions applied:**
- Outdoor Section is statewide (not Katy-only) — Quan's Central Entity is Texas Residential Property
- FTHB/Katy pages are hub pages (~1,200 words) linking to satellites, not monoliths
- Strategic leverage frame: stats as buyer outcomes, not agent vanity
- About page: hard EAV assertions first, strategic narrative second
- Centroids: 4-5x satellite depth, 3+ formats, 3+ measurement units ($, %, time)
- SRL: Buyer always Agent, never passive Object
- Publishing: simultaneous drop ideal, 48-hour window tolerated

### Tier 2 — Batch 2 (Day 2-3)

4. **Out-of-State Relocation Hub** — Break out from existing 11-part guide.
5. **Builder Incentives / Get Paid to Buy** — Quan's core differentiator.
6. **Down Payment Assistance Programs** — TDHCA, stacking rules, recapture tax.
7. **FHA vs Conventional Loans** — Texas-specific comparison.

### Tier 3 — Batch 3 (Day 4-5)

8. **Closing Costs — Texas Breakdown** — Line-by-line estimator.
9. **Pre-Approval Process** — Texas lender requirements, doc checklist.
10. **Katy ISD School Guide** — Ratings, feeder patterns, zoning trends.
11. **Commute Guide (Katy → Houston)** — Peak/off-peak, toll costs, METRO.
12. **New Construction Communities** — Builder profiles, timeline, design center.

### Tier 4 — After Profile Discovery

13. **Claim/fix GBP** — If it exists.
14. **sameAs URLs** — Add confirmed profile URLs to schema.
15. **Review generation strategy** — One platform at a time.

---

## What We Removed (Not Grounded in Quan's Content)

| Removed | Reason |
|---|---|
| All 6 seller spokes | Quan mentions it but has built nothing for sellers |
| All 5 investment spokes | Same — mentioned, not built |
| Competitor automated crawl framework | Overkill. Manual review is sufficient. |
| 13-platform automated audit | Profiles likely don't exist. Manual search first. |
| Proxy setup requirement | 90% of data is public or from Quan directly |
| 50+ spoke page plan | Reduced to ~12 grounded spokes |

---

## State of the Project

```
Phase 1 (Foundation):          ✅ Complete — 8 docs, all grounded
Phase 2 (Blueprint):                ✅ Complete — 6 methodology layers
Phase 3 (Prep/Audit):               ✅ Complete — frameworks revised to match reality
Phase 3.5 (Connective Tissue):      ✅ Complete — 6 architectural layers
Phase 3.6 (Neurological Precision): ✅ Complete — 5 precision layers:
                                       🔤 Predicate & Intent Mapping (verbs per intent)
                                       🔗 Entity Disambiguation Plan (collision prevention)
                                       🧵 Discourse Integration + Modality Matching
                                       🎨 Page Character Analysis (per-spoke visual semantics)
                                       ⚖️ Groundedness Validation Protocol (hard truth ranges)
Phase 3.7 (Algorithmic Reflexes):     ✅ Complete — 5 algorithmic reflex layers:
                                       🏷️ SRL SOP (Role Labeling added to Predicate Mapping)
                                       🎯 Centroid Selection (added to Topical Map)
                                       🔮 NLI Entailment Paths (new file)
                                       📁 Role-Based URL Taxonomy (added to Roadmap)
                                       📊 Information Gain Auditing (Fact-per-Token, added to Content Briefs)
Phase 4 (Execution):                ⏳ Ready — blocks on: Quan interview (15 min)

Ready to build NOW:            /about, JSON-LD, navigation fixes
Ready after Quan call:         FTHB spokes (3-5 pages), market data integration
Ready after discovery:         Profile fixes, backlink groundwork

Publishing plan:               12 pages across 5 days (3-batch shock drop)
```
