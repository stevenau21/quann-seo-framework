# Entity Disambiguation Plan — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Proactively prevent Entity Collision — ensuring Google distinguishes Quan Nguyen (Texas Real Estate Agent, License #0774451, REAL BROKERAGE) from any other "Quan Nguyen" or similarly named entity in search.

---

## Core Principle

When multiple entities share the same or similar names, Google's Knowledge Graph suffers from **Entity Collision** — it can't tell which entity is which. The result: no Knowledge Panel, confused ranking signals, and lost entity authority. The solution is **Entity Resolution** — proactively telling Google "this Quan is THAT Quan" via disambiguation signals.

---

## Step 1: Identify Potential Collision Risks

### Name Variants to Check (via Google + KG API)

| Query to Test | Risk Level | Why |
|---|---|---|
| "Quan Nguyen" (bare name) | High | Common Vietnamese name. Likely multiple professionals. |
| "Quan Nguyen real estate" | Medium | Other Quan Nguyens may be agents in other states. |
| "Quan Nguyen Texas real estate" | Low | Narrows to Texas. Still check for duplicate agents. |
| "Quan Nguyen REAL BROKERAGE" | Lowest | Brokerage name anchors the entity uniquely. |
| "The Quantum Team" | Medium | May be used by other teams or businesses. |
| "Quann Homes" | Low | Branded domain. Unique, but verify. |

### Knowledge Graph API Check

Run for each variant:
```
GET https://kgsearch.googleapis.com/v1/entities:search?query=Quan+Nguyen+real+estate&key=[API_KEY]
```

**Expected outcome:** No existing KG entity for "Quan Nguyen" as a Texas real estate agent. If one exists for a different Quan Nguyen (e.g., a software engineer in California), we have a collision to resolve.

---

## Step 2: Create Disambiguating Attributes

### Unique Identifier Triples

These are the "fingerprints" that make THIS Quan Nguyen uniquely identifiable:

| Triple | Value |
|---|---|
| Quan Nguyen → hasOccupation → Real Estate Agent |
| Quan Nguyen → hasLicense → Texas #0774451 |
| Quan Nguyen → worksFor → REAL BROKERAGE |
| Quan Nguyen → brandName → The Quantum Team |
| Quan Nguyen → officialWebsite → https://quann.homes |
| Quan Nguyen → serviceArea → Katy, Houston, Austin, Dallas, Rio Grande Valley |
| Quan Nguyen → telephone → (832) 400-3152 |
| Quan Nguyen → email → quan@thequantumteam.net |

Every external profile must surface at least 3 of these triples. Consistency = disambiguation.

---

## Step 3: External Profile Anchoring (sameAs Network)

### Priority Profiles for sameAs Schema

| Platform | Action | Disambiguation Signal |
|---|---|---|
| **TREC License Lookup** | Verify license #0774451 is active. Link to public license page. | Highest authority — government source. |
| **Google Business Profile** | Create/claim with exact name: "Quan Nguyen — The Quantum Team at REAL BROKERAGE" | Maps + KG anchor. |
| **LinkedIn** | Profile must list: occupation=Real Estate Agent, company=REAL BROKERAGE, link to quann.homes | Professional identity anchor. |
| **HAR.com** | Agent profile (requires HAR membership). License # must match. | Industry database. |
| **Zillow** | Agent profile. Bio must include license # + brokerage. | Consumer-facing anchor. |
| **Realtor.com** | Agent profile. Same NAP consistency. | Consumer-facing anchor. |
| **Wikidata** | Create entity item with all unique identifiers. | Knowledge Graph source. |

### Schema Markup (Homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "@id": "https://quann.homes/#agent",
  "name": "Quan Nguyen",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "Texas Real Estate License",
    "value": "0774451"
  },
  "worksFor": {
    "@type": "RealEstateAgent",
    "name": "REAL BROKERAGE"
  },
  "brand": {
    "@type": "Brand",
    "name": "The Quantum Team"
  },
  "sameAs": [
    "https://www.trec.texas.gov/...",
    "https://www.linkedin.com/in/quan-nguyen-realestate",
    "https://www.har.com/...",
    "https://www.zillow.com/profile/...",
    "https://www.realtor.com/realestateagents/...",
    "https://www.wikidata.org/wiki/Q..."
  ],
  "url": "https://quann.homes",
  "telephone": "(832) 400-3152",
  "email": "quan@thequantumteam.net"
}
```

The `@id` field is critical — it establishes a canonical URI for the entity. Every Article schema on the site references this `@id` in its `author` field.

---

## Step 4: On-Site Disambiguation Signals

### Entity Home Page (About)

Must explicitly state:
> "Quan Nguyen is a licensed Texas real estate agent (License #0774451) with REAL BROKERAGE, operating as The Quantum Team."

This sentence contains four disambiguating attributes in one declarative statement:
1. Texas (jurisdiction)
2. License # (unique identifier)
3. REAL BROKERAGE (employer entity)
4. The Quantum Team (brand entity)

### Footer (Every Page)

```
Quan Nguyen | Texas License #0774451
The Quantum Team at REAL BROKERAGE
quann.homes | (832) 400-3152
```

Three identifiers on every page. Impossible to confuse with another "Quan Nguyen."

---

## Step 5: Ongoing Monitoring

| Check | Frequency | Tool |
|---|---|---|
| KG API query for "Quan Nguyen" — does our entity appear? | Monthly | Google KG Search API |
| SERP check: does "Quan Nguyen REALTOR" show a Knowledge Panel? | Monthly | Manual search |
| Collision check: any new "Quan Nguyen" entities in real estate? | Quarterly | KG API |
| sameAs profile consistency — all 7 platforms still link to quann.homes? | Quarterly | Manual verification |

---

## Risk Assessment

| Scenario | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Another Quan Nguyen is also a Texas agent | Low-Medium | High — direct collision | License # + brokerage in all profiles |
| "The Quantum Team" used by another business | Low | Medium — brand confusion | Always pair with "REAL BROKERAGE" |
| KG creates duplicate entities for same person | Medium | High — split authority | sameAs network + @id in all schema |
| No KG entity created after 3 months | Medium | High — invisible to KG | Wikidata creation + GBP verification |
