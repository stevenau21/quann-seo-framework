# Revised Quan Call Agenda — Entity Classification & EAV Values

**Date:** 2026-05-05
**Duration:** 15 minutes
**Purpose:** Confirm the real-world attributes that turn quann.homes from a set of pages ("strings") into a recognized Web Entity ("thing") in Google's Knowledge Graph. This is NOT about "what content to write" — it's about the Entity-Attribute-Value triples that populate a Knowledge Panel.

---

## Block 1: Entity Classification (2 min)

### Question: Organization or Person?

Google needs to know whether "Quan Nguyen" is a **Person** entity or if "The Quantum Team" is an **Organization** entity. This determines the schema type and Knowledge Panel format.

```
A. Is your primary identity "Quan Nguyen, individual agent" (Person entity)?
B. Or is it "The Quantum Team at REAL BROKERAGE" (Organization entity)?
C. Both — Quan IS the team, but you present as an individual agent?

→ This determines whether homepage schema is:
   {"@type": "RealEstateAgent"}  (for Person)
   {"@type": "RealEstateAgent", "worksFor": {"@type": "RealEstateAgent", "name": "REAL BROKERAGE"}}
   vs.
   {"@type": "LocalBusiness"} for "The Quantum Team"
```

---

## Block 2: Official Attributes (5 min)

These are the EAV values that populate structured data and Knowledge Panels.

### Agent Credentials

| Attribute | Question |
|---|---|
| **Years of experience** | "How many years have you been a licensed agent? Include any prior brokerage." |
| **License status** | "Confirm: Texas license #0774451, active? Any disciplinary history?" |
| **Certifications** | "Do you hold ABR (Accredited Buyer's Representative)? CRS? GRI? CIPS? Any designations?" |
| **Languages** | "Do you speak Vietnamese? Any other languages?" |
| **Education** | "College degree? Any real estate-specific education beyond licensing?" |

### Professional Affiliations

| Attribute | Question |
|---|---|
| **NAR membership** | "Are you a member of the National Association of Realtors?" |
| **TAR membership** | "Texas Association of Realtors?" |
| **HAR membership** | "Houston Association of Realtors? (required if you practice in Houston)" |
| **Other** | "Katy Chamber of Commerce? Asian Real Estate Association? Any other?" |

### Service Geography

| Attribute | Question |
|---|---|
| **Primary office location** | "What physical address is on your license? (This becomes your NAP anchor.)" |
| **Service area precision** | "You serve Houston/Austin/Dallas/RGV — are these entire metros or specific neighborhoods within them? Which are primary vs occasional?" |
| **Zip codes** | "Which Katy/Houston ZIP codes do you serve most? 77494? 77450? 77449?" |

### Track Record

| Attribute | Question |
|---|---|
| **Transaction volume** | "Approximately how many transactions have you closed in your career? In the last 12 months?" |
| **Volume by type** | "What % buyers vs sellers vs investors?" |
| **Awards** | "Any awards? REAL BROKERAGE top producer? HAR awards? Local recognition?" |
| **Average client outcome** | "What's a typical outcome for your buyers? (e.g., 'average $5K in builder incentives negotiated')" |

---

## Block 3: Service Confirmation (3 min)

### Buyer Services (Core — Build These)

| Question | Why |
|---|---|
| "Which buyer types generate most of your business? Rank: first-time / out-of-state / move-up / new construction / luxury?" | Determines pillar priority order |
| "What's your buyer process? 4-5 key steps you walk every client through?" | Populates process pages |
| "What's the #1 thing clients say they didn't know before working with you?" | Information gap nodes |

### Seller Services (Gray Zone — Confirm or Cut)

| Question | Why |
|---|---|
| "Do you actively pursue seller listings? Or is it mostly buyer referrals?" | If no → cut seller pillar entirely |
| "If yes, what % of your business is sellers? What's your listing process?" | If yes → build 2-3 seller spokes |

### Investment Services (Gray Zone — Confirm or Cut)

| Question | Why |
|---|---|
| "Do you work with investors as a distinct client type? Or is it occasional?" | If occasional → cut investment pillar |
| "If yes, what kind of investors? First-time, portfolio growth, fix/flip?" | Determines which investment spokes |

---

## Block 4: Differentiators & Tools (3 min)

### Quan's Unique Approach

| Question | Why |
|---|---|
| "What do you do differently from other agents that clients specifically mention?" | Populates Tier 4 Knowledge Domain Terms |
| "How exactly does 'get paid to buy' work? Walk me through a real example — which incentives did you stack, what was the total benefit?" | Creates a case-study declarative sentence bank |
| "What tools or resources do you use that most agents don't? Custom spreadsheets? Negotiation scripts? Builder relationship database?" | Functional intent discovery |

### Site Functions to Confirm

| Question | Why |
|---|---|
| "Would you want a mortgage calculator on your site? An affordability calculator?" | Functional intent approval |
| "Would you use an IDX home search, or do you prefer sending clients listings yourself?" | Determines if we build home search |
| "Do you want clients booking consultation calls directly on the site (Calendly/widget) or contacting you first?" | CTA format decision |

---

## Block 5: Content Boundaries (2 min)

| Question | Why |
|---|---|
| "Are there any topics you specifically do NOT want covered? (e.g., 'don't write about negotiating — I do that personally')" | Borders — things Quan keeps off-site |
| "What's a topic you know a lot about but haven't written about yet?" | Hidden expertise — may be next pillar |
| "Any competitors you specifically want to beat in search? Who do you see ranking for 'Katy buyer agent'?" | Competitor priority |
| "Is there a specific client story or transaction you're most proud of? Can I use it as a case study?" | Anchor testimonial for content |
| **NEW: "Our writing rules ban hedging language (could, might, should). Every page reads like a definitive answer, not an opinion. Are you comfortable with that expert tone?"** | Confirms algorithmic authorship commitment |
| **NEW: "Your site needs to feel like a Relational Database of expertise — tables, definitions, data — not like a typical agent marketing site. Is that the brand you want?"** | Confirms distributional semantics / knowledge site identity |

---

## Block 6: Publishing Strategy (NEW — 1 min)

| Question | Why |
|---|---|
| **"We'll publish 12 pages across 5 days in 3 batches — not one at a time. This 'shock' triggers faster indexing and re-ranking. Are you okay with an aggressive launch?"** | Confirms momentum/shock strategy |

---

## Call Output: What We Produce After

### Immediately After Call

1. **Update central-entity.md** with all new values
2. **Populate EAV triples** with confirmed data
3. **Finalize schema templates** (Person vs Organization, RealEstateAgent vs LocalBusiness)
4. **Lock the spoke list** — cut any pillars Quan rejected, prioritize what remains
5. **Assign first 3 pages to write** based on Quan's ranked priorities
6. **Finalize Algorithmic Authorship Rulebook** — confirm any Quan-specific style preferences
7. **Lock the Shock Drop schedule** — confirm 5-day, 3-batch timeline

### EAV Triples Updated

```
Quan Nguyen → entity type → [Person/Organization]
Quan Nguyen → years experience → [N]
Quan Nguyen → certifications → [list]
Quan Nguyen → languages → [list]
Quan Nguyen → transaction volume → [N]
Quan Nguyen → primary ZIP → [XXXXX]
Quan Nguyen → buyer% → [N%]
Quan Nguyen → differentiator → ["get paid to buy: builder incentive capture + lender pairing + closing cost roll-in"]
```

### Schema Decision

```json
// If Person entity:
{
  "@type": "RealEstateAgent",
  "name": "Quan Nguyen",
  "identifier": "0774451",
  "worksFor": {"@type": "RealEstateAgent", "name": "REAL BROKERAGE"},
  "areaServed": ["Katy", "Houston", "Austin", "Dallas", "Rio Grande Valley"],
  "knowsLanguage": ["English", "Vietnamese"],
  "hasCredential": [
    {"@type": "EducationalOccupationalCredential", "credentialCategory": "ABR"},
    {"@type": "EducationalOccupationalCredential", "credentialCategory": "GRI"}
  ],
  "sameAs": ["..."] // Populated after web entity audit
}

// If Organization entity:
{
  "@type": "RealEstateAgent",  // or LocalBusiness
  "name": "The Quantum Team",
  "founder": "Quan Nguyen",
  "areaServed": [...]
}
```

---

## What NOT to Ask in This Call

- ~~"What content do you want?"~~ → Not Quan's job to be an editor. We present a plan, he confirms or cuts.
- ~~"What keywords should we target?"~~ → That's our methodology's job, not his.
- ~~"What pages should we build?"~~ → We present the grounded spoke list. He approves/denies. We execute.
- ~~"When do you want this done?"~~ → We propose a timeline. He adjusts.

This call is about **facts** — the real-world attributes of a real business. Not opinions about content.
