# Phase 2 Deliverable: Knowledge Graph & Conversion Architecture
> **Koray Framework:** Knowledge Graph & Structured Data (14 grounded rules)  
> **Allocation:** 100% ENGINE — Zero copywriter tasks  
> **Artifacts:** schemas.json, sameAs manifest, entity descriptions, KG tracking config

---

## ENGINE OUTPUT (Already Complete — No Human Action)

### 1. JSON-LD Schemas Generated
Four schemas written to `/06-topical-map/phase2-schemas.json`:
- **Homepage schema:** RealEstateAgent with all 11 entity attributes, credentials, languages, service areas, sameAs anchors
- **About page schema:** ProfilePage linking to #agent entity
- **Article template:** Copy-paste for every blog post — headline, author, about, dates
- **LocalBusiness schema:** The Quantum Team at Walzel Properties

### 2. Entity Descriptions (KG Pattern)
Koray's KG rule: "Entity descriptions follow a strict pattern — definitive, answers 'what'/'who', includes related entities, no subjective opinions." Two descriptions produced:
- **Quan Nguyen:** Definitive 5-sentence entity description with 5 related entities
- **Walzel Properties:** Definitive 2-sentence description with 3 related entities

### 3. KG Panel Tracking Config
4 locations to monitor, 5 queries to track. Success = Knowledge Panel appears within 4-8 weeks of Wikidata + GBP creation.

### 4. sameAs Manifest
Complete mapping of every external profile — verified, needs verification, needs creation, contaminated.

---

## HUMAN ACTION CHECKLIST

**[Koray Rule: KG Concept #7 — Brand SERP]**  
*"The Brand SERP is Google's business card for your entity. Every incorrect entry is a ranking signal that fractures entity identity."*

### PRIORITY ORDER (Execute in sequence — each step builds on the previous)

| Step | Platform | Action | Time |
|---|---|---|---|
| **1** | LinkedIn | **Fix duplicates.** Close the Elevatus and Truss profiles. Keep ONE profile only, updated to Walzel Properties. | 15 min |
| **2** | Google Business Profile | **Create.** Name: "Quan Nguyen — The Quantum Team at Walzel Properties". Category: "Real Estate Agent". Service-area business (no storefront). Verify by postcard. | 30 min + wait |
| **3** | Zillow | **Create agent profile.** Add bio, photo, link to quann.homes. Ask 3 past clients for reviews. | 20 min |
| **4** | Wikidata | **Create item.** Type: human (Q5). Occupation: real estate agent (Q1860857). Employer: Walzel Properties. Add official website (quann.homes) and work locations. | 15 min |
| **5** | HAR.com | **Update brokerage.** Log into HAR member portal → update profile → set to Walzel Properties. | 10 min |
| **6** | Realty.com | **Claim and update.** Correct brokerage from Forever Realty to Walzel Properties. | 10 min |
| **7** | Realtor.com | **Create new profile.** Name: Quan Nguyen. Brokerage: Walzel Properties. Link to quann.homes. | 15 min |
| **8** | Crunchbase | **Create organization profile** for "The Quantum Team." Industry: Real Estate. Add website. | 10 min |
| **9** | Nextdoor + YouTube | **Claim/create.** Low priority — do after steps 1-7 are verified. | 20 min |

**Total time: ~2 hours** (plus Google postcard wait time)

---

### VERIFICATION CHECKLIST (After Steps 1-7 Complete)

- [ ] LinkedIn: One profile only, brokerage = Walzel Properties
- [ ] GBP: Created and verification postcard requested
- [ ] Zillow: Profile live with quann.homes link
- [ ] Wikidata: Item created with Q-ID (save the Q-ID)
- [ ] HAR.com + Realty.com: Brokerage corrected to Walzel Properties
- [ ] Realtor.com: Profile created
- [ ] All profiles show: **Quan Nguyen → Walzel Properties → quann.homes**

Once verified, the engine will populate the `sameAs[]` array in the JSON-LD schema with all confirmed URLs. This is the final signal that collapses Google's fragmented entity view into one Knowledge Graph node.

---

## CONVERSION ARCHITECTURE (Phase 2 Engine — Silent)

**[Koray Rule: Conversion & Growth — Flywheel Model, A/B Testing, User Retention]**

The engine has mapped the conversion flywheel for quann.homes. This is infrastructure only — no human action required. The copywriter will receive templates in Phase 4.

**Flywheel Mapping:**
- **SPEED:** AI Language Bridge (instant multilingual response) + The Quantum Team System (documented process)
- **FRICTION:** Contact form → direct booking (remove phone tag). Every page → CTA to consultation.
- **SIZE:** Post-transaction referral system. Every closed buyer = 1 review + 1 referral.

**A/B Testing Setup (Deferred):** After 6 pages published, engine will configure A/B tests for CTA placement and headline variants against conversion tracking.

---

*Engine: Phase 2 complete. 14 grounded KG rules executed. 4 schemas generated. 9-step human checklist produced. Conversion architecture mapped. Stand by for Phase 3.*
