# Proactive Entitization Strategy — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Turn the website string "quann.homes" into a recognized Knowledge Graph entity — a "thing" Google understands as "a Texas buyer-specialist agent operating under Walzel Properties."

---

## Core Principle

A website is a "string." A Knowledge Graph entity is a "thing." Turning the former into the latter requires deliberate information point creation, entity reconciliation across trusted knowledge bases, and seed entity association on third-party platforms. This cannot happen organically — it must be engineered.

---

## Phase 1: Entity Reconciliation — Create the KG Node

### Step 1: Check if an entity already exists

Use the [Google Knowledge Graph Search API](https://developers.google.com/knowledge-graph) to query:
- `Quan Nguyen real estate`
- `The Quantum Team Walzel Properties`
- `quann.homes`

**Expected outcome:** No entity exists yet. This is a new entity to create.

### Step 2: Create on Wikidata

Create a Wikidata item for "Quan Nguyen" (the person, not the domain):

| Property | Value |
|---|---|
| `instance of (P31)` | `human (Q5)` |
| `occupation (P106)` | `real estate agent (Q1860857)` |
| `employer (P108)` | `REAL BROKERAGE` (create if needed) |
| `official website (P856)` | `https://quann.homes` |
| `work location (P937)` | `Katy, Texas`, `Houston`, `Austin`, `Dallas` |
| `identifier (P... )` | `Texas license #0774451` |

### Step 3: Create on Crunchbase / OpenCorporates

If "The Quantum Team" is a registered business entity:
- Create Crunchbase organization profile
- Add website, description, industry = "Real Estate"
- Link back to quann.homes

### Step 4: Google Business Profile

If one exists: claim and fix NAP (Name, Address, Phone).
If not: create one with:
- Business name: Quan Nguyen — The Quantum Team at REAL BROKERAGE
- Category: "Real Estate Agent"
- Service areas: Katy, Houston, Austin, Dallas, Rio Grande Valley
- No physical storefront (service-area business)

---

## Phase 2: Information Point Creation

### The Entity Home Page

`quann.homes/about` must serve as the definitive "information point" — the source of truth about the entity.

**Required content blocks:**
1. Name + license + brokerage (the triple anchor)
2. Entity type declaration: "Quan Nguyen is a licensed Texas real estate agent..."
3. Service areas with specificity (cities, not "all of Texas")
4. Certifications + associations + awards (after Quan call)
5. Transaction count / years of experience
6. Differentiator: "get paid to buy" with concrete examples
7. Languages spoken
8. Testimonial excerpts

### JSON-LD Structured Data (Homepage + Every Page)

```json
{
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "name": "Quan Nguyen",
  "identifier": {
    "@type": "PropertyValue",
    "propertyID": "TX License",
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
  "url": "https://quann.homes",
  "sameAs": [
    "https://www.wikidata.org/wiki/Q...",
    "https://www.zillow.com/profile/...",
    "https://www.har.com/...",
    "https://www.linkedin.com/in/..."
  ],
  "areaServed": [
    {"@type": "City", "name": "Katy"},
    {"@type": "City", "name": "Houston"},
    {"@type": "City", "name": "Austin"},
    {"@type": "City", "name": "Dallas"},
    {"@type": "City", "name": "Rio Grande Valley"}
  ],
  "knowsAbout": [
    {"@type": "Thing", "name": "First-time home buying in Texas"},
    {"@type": "Thing", "name": "Builder incentives and new construction"},
    {"@type": "Thing", "name": "Texas property taxes and MUD/PID"}
  ],
  "telephone": "(832) 400-3152",
  "email": "quan@thequantumteam.net"
}
```

### Article Schema (Every Blog Post)

```json
{
  "@type": "Article",
  "headline": "...",
  "author": {
    "@type": "RealEstateAgent",
    "name": "Quan Nguyen",
    "sameAs": "https://quann.homes/#agent"
  },
  "about": {"@type": "Thing", "name": "..."},
  "datePublished": "...",
  "dateModified": "..."
}
```

---

## Phase 3: Seed Entity Association

### Platform Checklist

| Platform | Action | Priority |
|---|---|---|
| Google Business Profile | Claim/Create + verify | HIGH |
| Zillow | Claim agent profile, add website + bio | HIGH |
| Realtor.com | Claim agent profile | HIGH |
| HAR.com | Verify profile exists (requires HAR membership) | HIGH |
| LinkedIn | Create/optimize profile, link to site | MEDIUM |
| Nextdoor | Claim agent profile (if neighborhood presence) | MEDIUM |
| Facebook | Create business page if not existing | MEDIUM |
| Instagram | @quann.nguyen — ensure bio links to quann.homes | MEDIUM |
| YouTube | If Quan does video, create channel linked to site | LOW |

### Content-Driven Entity Association

For each blog post published:
- Include `author` and `about` schema linking to the Quan Nguyen entity
- Cross-reference established entities (TREC, HAR, REAL BROKERAGE, relevant Texas cities) in body text
- Where possible, link OUT to authoritative knowledge bases (Wikipedia, Wikidata) for key concepts

---

## Phase 4: Entity Reconciliation Triggers

**Goal:** Google's Knowledge Graph API starts returning quann.homes as a recognized entity.

**Timeline expectations:**
- Wikidata creation → 2-4 weeks for Google ingestion
- Google Business Profile → immediate for Maps, 2-4 weeks for KG
- Structured data on site → indexed at next crawl
- Third-party profile consistency → cumulative signal over 4-8 weeks

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| Wait for Google to discover Quan | Create the entity proactively on Wikidata |
| Use different names on different platforms | Exact same name, phone, website everywhere |
| No sameAs in schema | Populate sameAs with every verified profile URL |
| Generic about page | Entity home page with every attribute populated |
