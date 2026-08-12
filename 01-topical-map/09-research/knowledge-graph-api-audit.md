# Knowledge Graph API Audit — EAV Verification & Contextual Bridges

**Date:** 2026-05-05
**Purpose:** Verify Quan's EAV triples against Google's current "perception of reality" for the core topics. Build contextual bridges where Google's understanding differs from Quan's specialized perspective.

---

## Core Principle

Google's Knowledge Graph stores facts as **Entity-Attribute-Value (EAV) triples.** These triples represent Google's "current perception of reality" for a niche. If Google associates "Texas home buying" with "acreage" and "privacy" but Quan's content focuses on "builder incentives" and "MUD/PID structures," Quan's pages will appear semantically misaligned — and rank poorly.

The solution: identify the gap, then build contextual bridges that move the algorithm from its current understanding to Quan's specialized perspective.

---

## Audit Method

### Step 1: Identify Core Entities

For Quan's niche, the core entities are:

| Entity | KG MID (to verify) |
|---|---|
| Texas real estate | `/m/0...` |
| Home buying | `/m/0...` |
| First-time home buyer | `/m/0...` |
| Katy, Texas | `/m/01_v9q` |
| Houston | `/m/03g5z` |
| Real estate agent | `/m/0dtdf` |
| Property tax | `/m/05z8x` |
| Mortgage loan | `/m/0275q6` |
| FHA insured loan | `/m/02q7d5` |
| Closing costs | `/m/0...` |

### Step 2: Query Knowledge Graph API

For each entity, query:
```
GET https://kgsearch.googleapis.com/v1/entities:search?query=[entity]&key=[API_KEY]
```

Extract:
- `@type` — entity type
- `detailedDescription.articleBody` — Google's textual description
- `description` — short description
- Explicit attributes returned
- `resultScore` — confidence

### Step 3: Extract Current Triples

For each entity, parse:
- **Explicit attributes** (from API response)
- **Implied attributes** (from `detailedDescription` text — what does Google emphasize?)
- **Associated entities** (from `@type` and `hasPart`/`subclassOf` relationships)

---

## Expected Findings (Pre-Audit Hypothesis)

Based on known KG structure for real estate entities:

### Current KG Perception of "Texas Real Estate"

| Likely Attribute | Likely Value |
|---|---|
| `subclassOf` | `Real estate in the United States` |
| `location` | `Texas` |
| `hasPart` | `Houston real estate`, `Austin real estate`, `Dallas real estate` |
| Emphasized attributes | Acreage, privacy, land, ranches, oil/mineral rights |
| **Missing** | Builder incentives, MUD/PID structure, FTHB programs, new construction dynamics |

### Current KG Perception of "Home Buying"

| Likely Attribute | Likely Value |
|---|---|
| `subclassOf` | `Purchasing` |
| `hasPart` | `Mortgage`, `Down payment`, `Closing` |
| Emphasized attributes | Financing, inspection, appraisal |
| **Missing** | Builder incentive capture, "get paid to buy," agent negotiation tactics |

---

## Contextual Bridge Strategy

### Bridge 1: Generic "Home Buying" → "Texas Home Buying"

**Gap:** KG treats "home buying" as a generic concept. Quan specializes in Texas-specific dynamics.

**Bridge content:**
- Opening paragraph of every page explicitly connects the generic concept to the Texas context:
  > "Home buying follows the same fundamental process nationwide — but Texas introduces specific dynamics: homestead exemptions, MUD/PID tax structures, and builder-dominated new construction markets."

### Bridge 2: "Property Tax" → "MUD/PID Tax Structures"

**Gap:** KG associates "Texas property tax" with high rates but not with the MUD/PID mechanism.

**Bridge content:**
- Dedicated definitions in every area guide:
  > "Texas property taxes are higher than the national average — but the MUD (Municipal Utility District) and PID (Public Improvement District) structures explain why. A MUD tax funds the water, sewer, and drainage infrastructure that made your new community possible."

### Bridge 3: "New Construction" → "Builder Incentives"

**Gap:** KG treats "new construction" as a product type. Quan treats it as a negotiation opportunity.

**Bridge content:**
- Reframe in every new-construction page:
  > "New construction isn't just about choosing floor plans — it's about capturing builder incentives. Most buyers don't know that builders routinely offer closing cost credits, rate buy-downs, and upgrade allowances worth $5,000-$15,000."

### Bridge 4: "Home Buying" → "Get Paid to Buy"

**Gap:** KG doesn't recognize "getting paid to buy" as a valid concept.

**Bridge content:**
- Case study format bridges the gap:
  > "Getting paid to buy means stacking builder incentives, lender credits, and closing cost roll-ins so that your out-of-pocket cost at closing is reduced — sometimes to zero. Here's how it worked for a recent Katy buyer..."

---

## Attribute Verification Matrix

| Core Entity | KG Has This? | Quan Has This? | Bridge Needed? |
|---|---|---|---|
| Texas home buying → high property tax | ✅ Yes | ✅ Yes | No |
| Texas home buying → MUD/PID | ❌ No | ✅ Yes | ✅ Bridge 2 |
| New construction → product types | ✅ Yes | ✅ Yes | No |
| New construction → builder incentives as negotiation | ❌ No | ✅ Yes | ✅ Bridge 3 |
| Home buying → down payment assistance | ✅ Yes (generic) | ✅ Yes (Texas DPA) | Minor bridge |
| Home buying → "get paid to buy" | ❌ No | ✅ Yes (core differentiator) | ✅ Bridge 4 |
| First-time buyer → process steps | ✅ Yes | ✅ Yes | No |

---

## Action Plan

| Step | Action | Timeline |
|---|---|---|
| 1 | Obtain Google Knowledge Graph API key | Before content writing |
| 2 | Run API audit for all 10 core entities | 1 hour |
| 3 | Compare extracted triples vs Quan's EAV triples | 30 min |
| 4 | Identify mismatches — where KG emphasis differs from Quan's focus | 30 min |
| 5 | Build contextual bridges for every mismatch | Integrated into content briefs |
| 6 | After page publish: re-run API audit (4 weeks later) to see if KG perception shifted | 4 weeks post-launch |

---

## Expected Outcome

After contextual bridges are published and indexed:
- Google's KG API begins returning MUD/PID as an attribute of "Texas property tax"
- "Builder incentives" becomes associated with "Texas new construction"
- "Get paid to buy" emerges as a recognized entity (or at minimum, a strongly associated phrase with quann.homes)
- quann.homes begins appearing as a `sameAs` or `mentions` link in entity associations
