# Natural Language Inference (NLI) Paths — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Map the entailment relationships of every core statement Quan's content makes. Search engines use Natural Language Inference to determine what a document *implies* beyond what it explicitly states. If your content states Fact A but fails to cover what Fact A *entails*, the Knowledge-Based Trust (KBT) score is capped — the engine infers you don't actually understand the domain.

---

## Core Principle

A search engine doesn't just index what you said. It runs NLI against every declarative sentence:

> **Premise (your text):** "Quan negotiates builder incentives worth $5,000–$15,000."
> **Hypothesis (engine tests):** "This agent understands contractual contingencies."
> **Judgment:** Entailment? Contradiction? Neutral?

If the site never mentions contingencies, the entailment fails. NLI produces **Contradiction** or **Neutral** instead of **Entailment**. KBT drops. Ranking drops.

---

## Entailment Architecture

For every declarative statement Quan makes, there is a **required entailment set** — the concepts the engine expects to find elsewhere on the domain. Missing entailments create an **Entailment Gap**. Gaps accumulate across pages until the domain's aggregate NLI score degrades.

### Tier 1 Entailments (Mandatory — Missing = KBT Cap)

These are the "if you claim X, you MUST cover Y" relationships. Failure to cover any Tier 1 entailment signals to the engine that the domain does not actually possess the claimed expertise.

| Statement (Premise) | Entailed Concepts (Must Exist Somewhere on Domain) | Entailment Type |
|---|---|---|
| "We negotiate builder incentives" | Contractual contingencies, option period strategy, earnest money release, builder contract review, upgrade allowance structures, closing cost credits | Strict Entailment |
| "We help first-time buyers" | Down payment assistance programs, FHA loan requirements, pre-approval process, closing cost breakdown, home inspection guide, homestead exemption | Strict Entailment |
| "Texas property taxes explained" | MUD/PID tax structures, homestead exemption cap, protest/appraisal process, county-by-county rate comparison, effective tax rate vs nominal rate | Strict Entailment |
| "Katy neighborhood expertise" | School zoning boundaries, MUD district mapping, flood zone classifications, HOA fee structures, new construction vs resale inventory, commute corridor data | Strict Entailment |
| "Out-of-state relocation specialist" | Cost of living comparison methodology, Texas vs origin state tax differential, timeline planning (30-60-90 day), temporary housing options, neighborhood matching process | Strict Entailment |
| "REAL BROKERAGE affiliated" | What REAL BROKERAGE means for buyers, brokerage vs agent distinction, fiduciary duty explanation, TREC consumer protection notice, commission structure transparency | Strict Entailment |

### Tier 2 Entailments (Strong — Missing = Authority Signal Weakens)

These are expected by the engine but with lower severity. Missing them doesn't cap KBT but significantly reduces the domain's authority signal relative to competitors who cover them.

| Statement (Premise) | Entailed Concepts (Expected) | Entailment Type |
|---|---|---|
| "FHA vs Conventional comparison" | PMI vs MIP distinction, rate differentials, property standard requirements, refinance pathways, down payment gift rules | Strong Entailment |
| "Texas down payment assistance" | TDHCA program tiers, income limit brackets, recapture tax implications, lender approval list, program stacking rules | Strong Entailment |
| "New construction communities" | Builder reputation profiles, build timeline expectations, design center process, structural warranty coverage, pre-drywall inspection rights | Strong Entailment |
| "Katy ISD school guide" | School rating methodology explanation, transfer policy, magnet programs, feeder pattern maps, property tax correlation with school ratings | Strong Entailment |
| "Commute guide" | Peak vs off-peak differentials, toll road cost calculations, park & ride options, METRO connectivity, work-from-home trend impact on commute tolerance | Strong Entailment |

### Tier 3 Entailments (Contextual — Competitive Differentiator)

These are not strictly required but create a "completeness signal." Domains that cover Tier 3 entailments signal deeper expertise than competitors.

| Statement (Premise) | Entailed Concepts (Competitive Edge) | Entailment Type |
|---|---|---|
| "Texas housing market expertise" | Sub-market volatility data, seasonal inventory patterns, builder incentive cycle timing (quarter-end), iBuyer impact analysis, institutional investor activity in target zip codes | Contextual |
| "First-time buyer guidance" | Rent vs buy break-even calculation, opportunity cost of waiting, future value projection methodology, homeownership hidden costs catalog | Contextual |
| "Katy community knowledge" | Master-planned community development pipeline (3-5 year), commercial development correlation with home values, demographic shift analysis, infrastructure bond election impacts | Contextual |

---

## Entailment Verification Matrix

Before publishing any page, verify that ALL Tier 1 entailments for every claim on that page exist somewhere on the domain. Use this matrix as a pre-publish gate.

### Per-Spoke Entailment Checklist

| Spoke | Primary Claim | Entailment Count (T1) | Current Coverage | Gap |
|---|---|---|---|---|
| Builder Incentives | "Negotiate builder incentives" | 6 | 0 | ALL MISSING |
| First-Time Buyer Process | "Help first-time buyers" | 7 | Blog covers basic process only | 5 missing |
| Out-of-State Relocation | "Relocation specialist" | 5 | 11-part guide exists, unknown which entailments covered | Verify |
| Katy Neighborhoods | "Katy expertise" | 6 | 0 | ALL MISSING |
| Katy ISD Schools | "School knowledge" | 5 | 0 | ALL MISSING |
| New Construction | "New construction communities" | 5 | 0 | ALL MISSING |
| Commute Guide | "Commute expertise" | 5 | 0 | ALL MISSING |
| Down Payment Assistance | "Texas DPA" | 5 | 0 | ALL MISSING |
| FHA vs Conventional | "Loan comparison" | 5 | 0 | ALL MISSING |
| Closing Costs | "Closing cost knowledge" | 4 | 0 | ALL MISSING |
| Pre-Approval | "Pre-approval guidance" | 4 | 0 | ALL MISSING |
| About Quan | "REAL BROKERAGE" | 7 | Footer only | 6 missing |

---

## NLI Integration Into Publishing Workflow

### Pre-Publish NLI Gate

Before any page goes live, run through this checklist:

1. **Extract all declarative claims** from the page content
2. **For each claim, identify Tier 1 entailments** from the mapping above
3. **Verify each entailment exists** on the domain (same page or linked page)
4. **Tag missing entailments** in the editorial calendar as required follow-up pages
5. **Do not publish if any Tier 1 entailment gap remains unaddressed** — either add the entailment content to the current page or commit to publishing the entailment page within the same shock drop batch

### Batch-Level NLI Audit

After each shock drop batch, run a cross-batch entailment check: does Batch 1's content satisfy the entailments Batch 2's pages will create? The goal is **zero Tier 1 entailment gaps at any point in the publishing sequence**.

---

## Entailment Gap Consequences

| Gap Type | Algorithmic Consequence |
|---|---|
| Single Tier 1 gap on one page | Local KBT score reduction for that page cluster |
| Multiple Tier 1 gaps across multiple pages | Site-wide KBT degradation — engine infers domain does not possess claimed expertise |
| Tier 1 gap persisted for >30 days | KBT cap becomes semi-permanent — harder to recover than initial ranking |
| Tier 1 gap on Centroid page | All pages in that spoke cluster inherit the gap — centroid amplifies damage |

---

## Related Documents

- [Predicate & Intent Mapping](predicate-intent-mapping.md) — predicates drive the premises that create entailments
- [Algorithmic Authorship Rulebook](algorithmic-authorship-rulebook.md) — Rules 7-8 (Discourse Integration, Modality Matching) govern how entailments connect across sentences
- [Truth Range Consensus Mapping](truth-range-consensus-mapping.md) — factual claims in entailment context must match truth ranges
- [Topical Map](../06-topical-map/topical-map.md) — Centroid pages carry the heaviest entailment burden
