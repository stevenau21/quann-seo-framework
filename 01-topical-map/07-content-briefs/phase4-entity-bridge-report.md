# Phase 4 Deliverable: Entity-Semantic Bridge
> **Koray Frameworks:** Semantic SEO (11 rules) + Entity-Based SEO (19 rules)  
> **Allocation:** 93% ENGINE — 7% HUMAN (review only)  
> **Layer:** 3 — bridges Phase 2 (KG) → Phase 6 (Topical Authority)  
> **Status:** Complete — awaiting Review Gate  

---

## What the Engine Executed

### 1. Entity Relationship Graph

Built a 37-node semantic network from all EAV triples. Entities connect through shared attributes and co-occurrence values.

| Stat | Value |
|---|---|
| Total entities mapped | 37 |
| Semantic edges (entity-to-entity connections) | 94 |
| Avg attributes per entity | 2.1 |
| Isolated entities (no connections) | 14 (section headers — see artifacts below) |

### 2. Entity Salience Ranking

Quan Nguyen dominates the graph with 1,250.8 salience — 78× more than the next entity. This confirms the entity-centricity of the domain: **everything connects through Quan.**

| Entity | Salience | Edges | Attributes |
|---|---|---|---|
| Quan Nguyen | 1,250.8 | 5 | 36 |
| Katy, TX | 16.0 | 5 | 2 |
| Buyer Representation | 13.4 | 2 | 2 |
| Investment Consulting | 4.5 | 2 | 2 |
| Houston, TX | 1.8 | 0 | 1 |

### 3. Contextual Bridge Map

Six bridges span the entity map. These are the semantic connections Google uses to understand **why** Quan Nguyen relates to Katy:

- **Quan ↔ Katy:** Katy area, Cinco Ranch, 77494, master-planned community, Katy ISD
- **Quan ↔ Houston Relocation:** out of state buyer, corporate relocation, Energy Corridor, transferee  
- **Katy ↔ Houston:** Energy Corridor, Katy Freeway (I-10), metro area, Fort Bend County
- **First-Time Buyer ↔ TSAHC:** down payment assistance, Home Sweet Texas Loan, 620+ credit score
- **New Construction ↔ Katy:** Cinco Ranch, builder incentive, master-planned, quick move-in
- **Property Tax ↔ Katy:** MUD, PID, homestead exemption, MUD tax rate

### 4. Information Gap Analysis

Schema.org expects 15 critical attributes for a RealEstateAgent. The EAV triples have attribute names that don't map 1:1 to schema.org JSON-LD keys — this is a normalization gap, not a data gap. The data exists (license number, website URL, etc.) but the EAV uses human-readable attribute names ("TREC License" instead of "hasCredential").

**Engine will resolve this silently in Phase 5 — no human action required.**

### 5. Entity Disambiguation Matrix

| Status | Count | Profiles |
|---|---|---|
| Verified sameAs | 3 | Quann.homes, Instagram, primary LinkedIn |
| Contaminated (needs fix) | 2 | HAR.com (Forever Realty), Realty.com (Forever Realty) |
| Duplicate (needs closure) | 2 | LinkedIn (Elevatus), LinkedIn (Truss) |
| Missing (needs creation) | 4 | Zillow, Realtor.com, Wikidata, Crunchbase |

---

## Engine Artifacts (Transparent Flag)

Two known structural artifacts in the output — same class as Phase 1's table-header contamination:

**Artifact A: Section headers classified as entities.** "Business Entity," "Service Entities," "Location Entities" appear as isolated nodes with zero edges. These are section dividers in the EAV markdown file, not business entities. They account for 3 of the 14 isolated nodes.

**Artifact B: Row indices in salience ranking.** "1," "2," "8" appear with scores of 2.9-3.1 because the spoke ranking table uses numbered rows. The structural parser correctly filtered column headers but didn't catch bare-number cells in the first column.

**Both are Phase 2 Entity Recognition layer issues — non-blocking for this phase.**

---

## Human Review Checklist

Only 4 actions require a human. Everything else was handled by the engine.

| # | Action | Platform | Time |
|---|---|---|---|
| 1 | Update brokerage on HAR.com: Forever Realty → Walzel Properties | HAR.com | 10 min |
| 2 | Update brokerage on Realty.com: Forever Realty → Walzel Properties | Realty.com | 10 min |
| 3 | Close duplicate LinkedIn profiles (Elevatus, Truss) — consolidate to primary | LinkedIn | 15 min |
| 4 | Review contextual bridge map above — does any connection feel wrong or missing? | Chat review | 5 min |

**Total human time: ~40 minutes.** Everything else was engine work.

---

## What Feeds Into Phase 5

Phase 5 (Technical & International SEO — 30 grounded rules) will use:
1. The 6 contextual bridges to structure internal linking and canonical URLs
2. The disambiguation matrix to populate `sameAs[]` once profiles are fixed
3. The attribution normalization gap to produce exact schema.org mappings
4. The salience ranking to prioritize which entities get dedicated pages vs. inline mentions

---

## Files Produced

| File | Purpose |
|---|---|
| `06-topical-map/phase4-entity-bridge.json` | Machine-readable entity graph, salience scores, bridges, gaps |
