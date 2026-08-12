# Functional Intent Discovery — Quann.Homes

**Date:** 2026-05-05
**Status:** Pre-execution baseline — defines what the site must DO, not just what it says
**Methodology:** A web entity is defined by its functions. Lacking engagement components leads search engines to classify a site as a "mere blog" rather than a professional service provider, lowering ranking priority.

---

## Current State

quann.homes has:
- ✅ Chatbot widget (RAG-powered — likely the strongest functional component)
- ✅ Contact forms (/contact-us, /contact-us-2)
- ❌ No calculators
- ❌ No search tools
- ❌ No estimators
- ❌ No interactive maps
- ❌ No comparison tools

**Assessment:** The site is classified as informational/promotional, not as a service tool. It's missing the functional density that top-tier real estate authorities (Zillow, Redfin, Realtor.com) provide.

---

## Functions Top-Tier Authorities Provide

### Zillow / Redfin / Realtor.com (Full suite)

| Function | What It Does | Intent Served |
|---|---|---|
| Home search + map | Browse listings on a map with filters | "Find homes for sale" |
| Mortgage calculator | Calculate monthly payment from price, rate, term | "How much will this cost?" |
| Affordability calculator | "How much home can I afford based on income/debt?" | "Can I afford to buy?" |
| Rent vs buy calculator | Compare long-term cost of renting vs buying | "Should I rent or buy?" |
| Home value estimator | Automated property valuation | "What's my home worth?" |
| Agent finder | Match with local agents | "Find an agent" |
| Saved searches / alerts | Email notifications for new listings | "Stay updated" |

### Top Local Agent Sites (Selective)

Most top Katy agents provide 1-3 of these — usually a home search (IDX integration) and sometimes a home valuation tool. Almost none provide the full suite.

---

## Functional Gap for Quann.Homes

### Gap Analysis

| Function | Zillow/Redfin | Top Competitors | quann.homes | Priority |
|---|---|---|---|---|
| Home search / map | ✅ | ✅ (IDX) | ❌ | 🟡 Medium — Quan is buyer-first, so search is natural. But IDX integration is heavy. |
| Mortgage calculator | ✅ | ⚠️ (1-2 have it) | ❌ | 🔴 Critical — directly supports "bridge the knowledge gap" mission |
| Affordability calculator | ✅ | ❌ (rare) | ❌ | 🟡 Medium — high value, low competition |
| Rent vs buy | ✅ | ❌ (rare) | ❌ | 🟡 Medium — differentiation opportunity |
| Home valuation | ✅ | ✅ (many have) | ❌ | 🟢 Low — Quan is buyer-first, not seller-first |
| Saved searches | ✅ | ❌ (rare) | ❌ | 🟢 Low — operational complexity |
| Chatbot (knowledge) | ❌ | ❌ (rare) | ✅ | Already exists — competitive differentiator |

### Priority Builds

#### 1. Mortgage Calculator (Embed — Not Custom Build)

**Why:** Every buyer needs this. Quan's Source Context says "bridge the knowledge gap" — a calculator bridges the gap between "I like this house" and "can I afford it?"

**Build approach:** Embed a white-label widget (no custom dev):
- MortgageCalculator.org embed (free, no branding)
- Bankrate embed (trusted domain, adds credibility)
- Zillow mortgage calculator embed (familiar to users)

**Where it lives:** On every property-related spoke page AND as a standalone tool page at /mortgage-calculator — which also serves as a pillar page that ranks for "Texas mortgage calculator."

#### 2. Affordability Calculator (Differentiator)

**Why:** Almost no local agent has this. Zillow/Redfin dominate the SERP for "how much home can I afford" — but they don't include Texas-specific factors (property tax impact, MUD taxes, homestead exemption effect on payment).

**Quan's angle:** A Texas-specific affordability calculator that factors in:
- County property tax rate
- MUD/PID assessments (checkbox for "new construction in Katy")
- Homestead exemption impact (before/after toggle)
- Builder incentive impact on cash-to-close

**Where it lives:** Standalone page `/how-much-home-can-i-afford` — the page itself is the informational resource; the calculator is the engagement component that proves functional completeness.

#### 3. Contextual Bridges With Functional Intent

Per methodology: a page that both explains a concept AND provides a tool to act on it has higher functional density.

| Spoke Page | Function to Embed |
|---|---|
| FTHB programs page | Eligibility checker (simple: "select your scenario → see which programs might apply") |
| Out-of-state buyer guide | Cost of living comparison table (interactive: "enter your current city → see Texas equivalent") |
| Katy neighborhood guide | Interactive map with school zones, commute heatmap, flood zone overlay |
| Closing costs page | Closing cost estimator (simple calculator) |
| Property tax guide | Tax impact calculator (before/after homestead, before/after MUD) |

---

## What Lacking Functions Costs

Per methodology, search engines evaluate:

1. **Engagement signals** — users who bounce from a page that lacks a calculator may click through to a page that has one
2. **Entity completeness** — a RealEstateAgent entity that provides no tools is algorithmically "thin"
3. **Classification** — without functional components, the site may be classified as informational/blog content rather than a professional service business
4. **SERP feature exclusion** — Google won't surface a site in "Mortgage Calculator" direct answer boxes without a calculator on the page

---

## Implementation Strategy

### Phase 1 (Immediate — before any pages written)
- Embed mortgage calculator widget on site
- Create `/mortgage-calculator` page

### Phase 2 (After first 6 spoke pages)
- Build Texas-specific affordability calculator page
- Add calculator embeds to FTHB and out-of-state pages

### Phase 3 (After area guides)
- Build interactive neighborhood tools (maps, comparisons)
- Add closing cost estimator

---

## Functional Density Score

Rate the site on functional completeness:

| Score | Meaning |
|---|---|
| 1 | Static informational pages only |
| 2 | Forms + chatbot (where quann.homes is NOW) |
| 3 | 1-2 embedded tools (where we target Phase 1) |
| 4 | Multiple tools with Texas-specific customization (Phase 2) |
| 5 | Full suite: tools + maps + calculators + chatbot (Phase 3) |

**Target:** Score 4 within 3 months of content launch.
