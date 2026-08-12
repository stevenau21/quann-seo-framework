# EAV Triples Expansion Blueprint — Quann.Homes

**Date:** 2026-05-04
**Status:** Preparation — identifies all triples that need values
**Blocks on:** Market data collection, Quan interview, web entity audit

---

## Why This Matters

Every entity in the topical map needs a full set of triples. Without them, content briefs have gaps, pages are thin, and Google can't confidently connect the dots. This blueprint lists every triple we NEED so we know exactly what to collect.

---

## Entity-Attribute Matrix (Universal Categories)

Applying the methodology's 14 universal attribute categories to each entity class:

| # | Category | What it Produces |
|---|---|---|
| 1 | Definition/What | "X is..." declarative sentences |
| 2 | Types/Variations | Subcategories, options |
| 3 | Steps/Process | How-to, timelines |
| 4 | Benefits | Why it matters |
| 5 | Costs/Pricing | Numbers, ranges |
| 6 | Requirements | Qualifications, prerequisites |
| 7 | Comparisons/vs | Decision frameworks |
| 8 | FAQs | Direct question-answer pairs |
| 9 | Tools/Checklists | Downloadable assets |
| 10 | Statistics/Data | Hard numbers with sources |
| 11 | Timeline/Duration | How long things take |
| 12 | Mistakes to Avoid | Common pitfalls |
| 13 | Best Practices | Expert recommendations |
| 14 | Local Specifics | Texas/Katy-specific context |

---

## Triples Inventory

### Entity Class 1: Quan Nguyen (Primary Business Entity)

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| Q1 | Years of Experience | ? | Quan | ❌ Missing |
| Q2 | Languages Spoken | ? | Quan | ❌ Missing |
| Q3 | Certifications | ? (ABR, CRS, GRI?) | Quan | ❌ Missing |
| Q4 | Professional Associations | ? (NAR, TAR, HAR?) | Quan | ❌ Missing |
| Q5 | Awards/Recognition | ? | Quan | ❌ Missing |
| Q6 | Career Transactions Closed | ? | Quan | ❌ Missing |
| Q7 | Team Size | ? | Quan | ❌ Missing |
| Q8 | Specialties (ranked) | 1. First-time buyers, 2. Out-of-state, 3. ... | Quan | ❌ Missing |

### Entity Class 2: Katy, TX Market

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| K1 | Median Home Price | $? (2026) | HAR.com / Redfin | ❌ Needs proxy |
| K2 | Price Per Square Foot | $? | Redfin | ❌ Needs proxy |
| K3 | Days on Market (Average) | ? days | HAR.com | ❌ Needs proxy |
| K4 | Month's Supply / Inventory | ? months | HAR.com | ❌ Needs proxy |
| K5 | YoY Price Change (%) | ?% | Redfin / FRED | ❌ Needs proxy |
| K6 | Active Listings Count | ? | HAR.com | ❌ Needs proxy |
| K7 | Median Home Size (sqft) | ? sqft | HAR.com | ❌ Needs proxy |
| K8 | Average Property Tax Rate | ?% | Texas Comptroller | ❌ Needs proxy |
| K9 | Population | ? | US Census | ❌ Needs proxy |
| K10 | Best School Districts | Katy ISD (A-rated), ? | TEA ratings | ❌ Needs proxy |
| K11 | Major Employers | ? | Chamber of Commerce | ❌ Needs proxy |
| K12 | Commute to Downtown Houston | ? minutes | Google Maps data | ❌ Needs proxy |
| K13 | New Construction Median Price | $? | HAR.com / Builders | ❌ Needs proxy |
| K14 | Luxury Segment Median Price ($1M+) | $? | HAR.com | ❌ Needs proxy |

### Entity Class 3: Texas Home Buying Process

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| P1 | Average Closing Costs (% of price) | ?% | Bankrate / ClosingCorp | ❌ Needs proxy |
| P2 | Typical Earnest Money | ?% of price | TREC / local convention | ❌ Needs proxy |
| P3 | Typical Option Period Fee | $? | TREC | ❌ Needs proxy |
| P4 | Attorney State vs Title State? | Texas = title company state | TREC | ✅ Known |
| P5 | Average Time from Offer to Close | ? days | Local data | ❌ Needs proxy |
| P6 | Common Contingency Types | Financing, inspection, appraisal, sale of home | Standard | ✅ Known |
| P7 | Required Disclosures (Seller's Disclosure) | TREC Seller's Disclosure Notice | TREC | ✅ Known |
| P8 | Who Chooses Title Company? | Buyer typically | TREC | ✅ Known |

### Entity Class 4: Texas Property Taxes

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| T1 | Average Rate per County | Harris: ?%, Fort Bend: ?%, Waller: ?% | Texas Comptroller | ❌ Needs proxy |
| T2 | Homestead Exemption Amount | $100,000 school tax exemption | Texas Comptroller | ✅ Known |
| T3 | MUD Tax (Katy-specific) | What MUD taxes are, typical amount | Fort Bend MUD #? | ❌ Needs proxy |
| T4 | Tax Protest Process | Steps + typical savings | Local resources | ❌ Needs research |
| T5 | Over-65 / Disability Exemptions | Amount + eligibility | Texas Comptroller | ❌ Needs proxy |
| T6 | How Tax Assessed Value is Determined | County appraisal district process | Local CADs | ❌ Needs proxy |

### Entity Class 5: Mortgage / Financing (Texas-specific)

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| M1 | FHA Loan Limits — Texas | $? (2026) | HUD | ❌ Needs proxy |
| M2 | Conventional Loan Limits — Texas | $? | FHFA | ❌ Needs proxy |
| M3 | VA Loan (no down payment) | $0 down + funding fee structure | VA | ✅ Known |
| M4 | USDA Loan Eligible Areas (near Katy) | ZIPs / map | USDA | ❌ Needs proxy |
| M5 | TDHCA Down Payment Assistance Amount | Up to ?% | TDHCA | ❌ Needs proxy |
| M6 | Texas MCC Program (Mortgage Credit Certificate) | Tax credit up to $?/yr | TDHCA | ❌ Needs proxy |
| M7 | Average Interest Rate — Texas (2026) | ?% | Freddie Mac | ❌ Needs proxy |
| M8 | Minimum Credit Score — FHA | 580 | FHA | ✅ Known |
| M9 | Minimum Credit Score — Conventional | 620 | Fannie Mae | ✅ Known |
| M10 | Debt-to-Income (DTI) Limits | FHA: ?%, Conventional: ?% | HUD / Fannie Mae | ❌ Needs proxy |

### Entity Class 6: TREC / Legal

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| L1 | Option Period Length (standard) | 7-10 days | TREC | ✅ Known |
| L2 | Option Period Termination Form | TREC 38-4 | TREC forms library | ✅ Known |
| L3 | Buyer Rep Agreement Types | Exclusive vs non-exclusive | TREC | ✅ Known |
| L4 | Agency Disclosure Timing | First substantive contact | TREC | ✅ Known |
| L5 | TREC Consumer Protection Notice | Required link + explanation | TREC | ✅ Known |
| L6 | Information About Brokerage Services (IABS) | Required form | TREC | ✅ Known |

### Entity Class 7: Houston Metro (comparison)

| # | Attribute | Needed Value | Source | Status |
|---|---|---|---|---|
| H1 | Median Home Price | $? | HAR.com | ❌ Needs proxy |
| H2 | Average DOM | ? days | HAR.com | ❌ Needs proxy |
| H3 | Top Suburbs for Families | ? | Local rankings | ❌ Needs proxy |
| H4 | Commute Times per Corridor | Energy Corridor: ?min, Downtown: ?min | Google Maps | ❌ Needs proxy |
| H5 | Flood Zone Percentage (Katy) | ?% of homes in flood zones | FEMA | ❌ Needs proxy |

### Entity Class 8: Existing Content Audit (quann.homes)

These pages already exist — need to catalog what they cover vs what's missing:

| Page | Status | Missing Entities |
|---|---|---|
| / (Homepage) | ✅ Live | Needs JSON-LD (missing), needs clear central entity anchor |
| /blog/steps-for-buying-your-first-home | ✅ Live | Audit: does it cover FTHB programs, down payment, loans? |
| /blog/out-of-state-buyer-guide | ✅ Live (comprehensive outline, 11 parts) | Probably covers A LOT — audit for gaps |
| /blog/texas-first-time-home-buyer-guide5 | ✅ Live | Audit: overlap/differences with other FTHB post |
| /contact-us, /contact-us-2 | ✅ Live | Two contact pages? Merge/review |
| /disclosure | ✅ Live | TREC-required — good |
| /privacy-policy | ✅ Live | Required — good |
| /texas-real-estate-commission-information-about-brokerage-services | ✅ Live | IABS form — good |

---

## What to Do When Data Arrives

1. Fill ALL triples with real values from market data collection
2. Fill Quan-specific triples from interview
3. Regenerate query templates with real values (e.g., "median home price Katy TX $385,000" instead of "median home price Katy TX $?")
4. Validate: does every spoke topic have all needed triples?
5. Expand content briefs with real data points
6. Start writing pages

---

## Dependency Map

```
Quan Interview ──────┐
                      ├──→ Fill Central Entity ──→ Update JSON-LD
                      │
Market Data (proxy) ──┤
                      ├──→ Fill Location/Market Triples ──→ Content Briefs
                      │
Competitor Crawl ─────┤
                      ├──→ Gap Matrix ──→ Content Priorities
                      │
Web Entity Audit ─────┘
                      └──→ sameAs URLs ──→ Structured Data
```
