# Phase 1: Copywriter Operations Manual — quann.homes
> **Source:** Koray Gubur Framework — Phase 1 Foundational Primitives  
> **Engine:** 3-Vector Dependency Extraction Engine v1.0  
> **Cards Processed:** 23 grounded rules (16 Python + 7 Linguistics)  
> **Deliverable:** Vocabulary bank, predicate-verb pairs, sentence structure rules  
> **For:** Copywriter — copy, paste, and follow verbatim

---

## Section 1: Your Canonical Predicate-Verb Bank

Every sentence you write for quann.homes must use verbs from this bank. No exceptions. These are Koray's "Verbs of Life" — the predicates that teach Google's entity engine what Quan does.

### The 7 Canonical Predicates (with approved synonyms)

| Canonical Predicate | Intent Type | Approved Alternatives | ❌ Banned |
|---|---|---|---|
| **FIND** | Discovery / Navigation | discover, locate, identify, uncover, search, explore, seek, spot | "look for," "check out" |
| **LEARN** | Education / Informational | discover, determine, acquire, ascertain, guide, explain | "understand," "figure out" |
| **COMPARE** | Evaluation / Commercial | evaluate, contrast, weigh, examine, assess | "look at," "see how" |
| **QUALIFY** | Screening / Pre-Action | assess, determine eligibility, measure, verify, confirm | "check if," "see whether" |
| **SAVE** | Value / Outcome | preserve, retain, economize, accumulate, conserve | "get a deal," "cut costs" |
| **PROTECT** | Security / Insurance | safeguard, shield, secure, guard, defend, cover | "keep safe," "watch out for" |
| **BUILD** | Creation / Investment | construct, develop, establish, create, design, form | "put together," "make" |
| **INVEST** | Growth / Long-term | commit, fund, allocate, endow, empower | "put money into," "buy" |

**Rule:** Every page targets exactly ONE canonical predicate. A "Sell Your Home" page uses **EARN** (gain, secure, obtain). A "First-Time Buyer Guide" uses **LEARN** (discover, guide, explain). Never mix predicates on one page.

### Domain-Specific Predicate Mapping

| Page Intent | Canonical Predicate | Example Sentence |
|---|---|---|
| Houston relocation guide | **LEARN** → discover, guide | "Discover how Katy's MUD districts reduce your property tax burden compared to inner-loop Houston." |
| First-time buyer process | **QUALIFY** → assess, verify | "Assess your down payment options with Texas DPA programs that stack for zero out-of-pocket closing." |
| Builder incentives / new construction | **EARN** → gain, secure | "Gain builder incentives that offset closing costs — saving Houston buyers $8,000 on average." |
| Why Walzel Properties | **PROTECT** → safeguard, shield | "Walzel Properties safeguards your transaction with fiduciary representation at every negotiation point." |
| Katy neighborhood guide | **FIND** → discover, explore | "Find your ideal Katy community — from master-planned Cinco Ranch to gated enclaves near Katy Mills." |
| Investment / multi-family | **BUILD** → construct, develop | "Build your Houston investment portfolio with cash-flowing multi-family properties in emerging submarkets." |
| CMA / property valuation | **COMPARE** → evaluate, assess | "Evaluate your home's market position using active, pending, and sold comparables in real-time MLS data." |

---

## Section 2: Entity Vocabulary Bank

### Location Entities — Approved Terms

| Entity | Approved Synonyms | ❌ Avoid |
|---|---|---|
| Houston | Houston metro, Greater Houston, Houston area | "H-Town," "Space City" |
| Katy | Katy area, Katy ISD zone, Katy Texas | "Katy suburb" |
| Texas | Lone Star State (sparingly) | "Big state," "TX" in body text |
| suburb | suburban community, residential area, neighborhood | "bedroom community" |
| community | neighborhood, residential district, locality | "hood," "area" |

### Transaction Entities — Approved Terms

| Entity | Hypernyms (broader) | Hyponyms (narrower) |
|---|---|---|
| estate | real estate, real property, realty, immovable | countryseat, entail, life estate, feoff |
| home | abode, dwelling, domicile, habitation, residence | fixer-upper, cliff dwelling, condominium, fireside |
| house | building, accommodation, edifice, structure | adobe house, beach house, town house, duplex, semi-detached |
| construction | creating, building, fabrication, assembly | arcade, assembly, balcony, basement |
| buy | acquire, purchase, obtain | buy up, buy out, pay off, pick up |
| sell | exchange, cede, deliver | auction, auction off, deal, clear |
| relocate | move, displace | — |
| invest | enable, equip, outfit, install | buy into, fund, float |
| finance | business, economics, management, direction | banking, funding, flotation, backing |

### Actor Entities — Approved Terms

| Entity | Hypernyms | Hyponyms | ❌ Avoid |
|---|---|---|---|
| agent | causal agent, official, functionary, businessperson | estate agent, house agent, land agent, real estate agent | — |
| realtor | estate agent, house agent, land agent, real estate broker | — | — |
| broker | businessperson, merchant, negotiator | insurance broker, investment banker, general agent | — |
| buyer | client, customer | purchaser, vendee, home buyer | — |
| seller | merchandiser, merchant | vendor, dealer, marketer | — |
| family | association, lineage, household | conjugal family, extended family | "clan" |
| investor | capitalist | depositor, lender, bondholder, contrarian | "speculator" |
| developer | creator | — | "builder" (use context) |

### Financial Entities — Approved Terms

| Entity | Approved Synonyms | ❌ Avoid |
|---|---|---|
| mortgage | home loan, financing | "house loan" |
| payment | defrayal, disbursement, settlement | "pay-off" |
| credit | credit rating, credit history, deferred payment | "credit score" (colloquial) |
| closing | completion, settlement, conclusion | "closing deal" |
| insurance | indemnity, policy, coverage | "insurance thing" |
| tax | assessment, levy, taxation | "taxes" (use singular for entity) |

---

## Section 3: Sentence Structure Rules

### Rule 1: Entity-First Declarative Structure

**[Koray Card: content-quality-linguistics — Linguistic Correctness]**

Every sentence starts with the ENTITY (noun), followed by the PREDICATE (verb), followed by the RESOLUTION.

```
❌ WRONG: "If you want to buy a home in Katy, it's important to know about MUD taxes."
✅ RIGHT: "Katy homebuyers qualify for MUD-district tax advantages that reduce annual property costs."
```

```
❌ WRONG: "There are many great neighborhoods in Houston, and each one has its own character."
✅ RIGHT: "Houston neighborhoods divide into master-planned communities, historic districts, and emerging submarkets — each with distinct price ceilings."
```

**The entity is always first. Always. No "there are" intros, no "if you" conditionals, no fluff.**

### Rule 2: No Modality — Declarative Ground Truth Only

**[Koray Card: content-quality-linguistics — E-A-T (Expertise, Authoritativeness, Trustworthiness)]**

❌ BANNED: might, could, maybe, perhaps, possibly, generally, usually, often, typically, in most cases

```
❌: "Katy homeowners could save money by refinancing when rates drop."
✅: "Katy homeowners who refinance in 2025 secure rates averaging 1.2 points below 2024 highs."
```

```
❌: "Builder incentives might help offset your closing costs."
✅: "Builder incentives offset closing costs for qualified buyers — saving Houston homebuyers $8,000 on average."
```

**You are writing expert content. Hedge words destroy E-A-T. Every sentence is a truth claim.**

### Rule 3: One Entity Per Paragraph

**[Koray Card: semantic-seo — Frame Semantics anchoring]**

Each paragraph anchors to ONE entity and explores its attributes. When the entity changes, start a new paragraph.

```
✅ CORRECT PARAGRAPH (Entity: Katy MUD Districts):
  Katy MUD districts levy property taxes at rates averaging $1.40 per $100 of assessed value.
  These municipal utility districts fund water, sewer, and drainage infrastructure for new-construction subdivisions.
  Houston homebuyers comparing Katy to inner-loop neighborhoods discover MUD rates offset the higher base prices of urban properties.
```

**MUD → tax rate → infrastructure → comparison. One entity, explored deeply.**

### Rule 4: Predicate-Verb Consistency

**[Koray Card: semantic-seo — Query-Focused Semantic Vocabulary Configuration]**

Once a page claims a canonical predicate, every sentence uses verbs from that predicate's family.

For a page built on **PROTECT**:
```
✅: "Walzel Properties safeguards your transaction. Our fiduciary duty shields your interests at every negotiation point. We secure your closing with title insurance and inspection contingencies."
❌: "Walzel Properties safeguards your transaction. You'll also find great neighborhoods through our search tool." (FIND contamination)
```

### Rule 5: Lexical Relations — Hypernyms, Hyponyms, and Synonyms

**[Koray Card: python-data-driven-seo — WordNet extraction]**

- **Synonyms** replace your primary term to avoid repetition.
- **Hypernyms** broaden context to connect to parent topics.
- **Hyponyms** narrow context for precision.

```
Example chain using "property":
  Hypernym: "Quan Nguyen holds a real estate license #0774451."
  Entity: "His property portfolio spans residential and investment sectors."
  Hyponym: "He manages single-family residences, condominium units, and multi-family holdings."
```

**Pattern:** Hypernym → Entity → Hyponym creates a Google-readable conceptual hierarchy in three sentences.

### Rule 6: Linguistic Correctness — Spelling, Grammar, Homophones

**[Koray Card: content-quality-linguistics — Linguistic Correctness]**

- **Homophones:** "principal" (loan amount) vs. "principle" (rule). "stationary" vs. "stationery."
- **Spelling:** American English only (Katy, Texas audience).
- **Grammar:** No comma splices. No dangling modifiers. Complete sentences.
- **Capitalization:** Proper nouns only. "Walzel Properties" not "walzel properties." "Katy ISD" not "katy isd."

---

## Section 4: Bridge Concept Vocabulary

**[Koray Card: topical-authority — Contextual Bridges]**

Bridge concepts connect your primary domain (real estate) to adjacent topics (schools, commute, lifestyle). Use these approved terms — never invent new ones.

| Bridge | Approved Vocabulary | ❌ Avoid |
|---|---|---|
| Schools | ISD, school district, campus, enrollment, rating, ranking | "good schools," "best schools" |
| Commute | transit time, commute corridor, route, artery, transit access | "easy commute," "close to" |
| Parks | green space, recreation, trail system, parkland | "nice parks," "pretty parks" |
| Shopping | retail, commercial district, shopping center, grocer | "great shopping," "mall" (ambiguous) |
| Dining | restaurant, cuisine, dining establishment, eatery | "food scene," "yummy" |
| Healthcare | medical center, hospital system, physician network, clinic | "good doctors," "nearby hospital" |
| Lifestyle | community amenity, recreational access, quality-of-life metric | "great lifestyle," "lifestyle vibe" |

---

## Section 5: Prohibited Vocabulary — The Banned List

**[Koray Card: content-quality-linguistics — Thin Content]**

These words signal thin content to Google. They appear in 95% of generic real estate blogs and convey ZERO semantic information:

| Category | Banned Words | Replace With |
|---|---|---|
| Vague adjectives | great, amazing, wonderful, fantastic, incredible | Entity-specific data (e.g., "4,200 sq. ft.") |
| Empty superlatives | best, top, #1, leading, premier | Certified data (e.g., "top 1% in closed units") |
| Comparative fluff | better, more affordable, nicer | Numeric comparison (e.g., "$45/sq.ft. below median") |
| Location hand-waving | close to, near, convenient to, minutes from | Distance + time (e.g., "3.2 miles, 8 minutes via I-10") |
| Subjective claims | beautiful, stunning, gorgeous, charming | Descriptive attributes (e.g., "brick facade, vaulted ceilings") |
| Empty transitions | however, moreover, furthermore, in addition | None — just start the next sentence |
| Passive voice | is located, can be found, is situated | Active verb (e.g., "sits," "occupies," "anchors") |

---

## Section 6: Pre-Writing Checklist

Before you write ANY page, verify:

- [ ] This page targets exactly ONE canonical predicate (FIND / LEARN / COMPARE / QUALIFY / SAVE / PROTECT / BUILD / INVEST)
- [ ] Every sentence starts with the entity, not "There is..." or "If you..."
- [ ] Zero modality words (might, could, maybe, perhaps)
- [ ] One entity per paragraph — no entity mixing mid-paragraph
- [ ] All verbs trace to the approved predicate bank
- [ ] All adjectives are numeric or measurable (no vague descriptors)
- [ ] All bridge concepts use approved vocabulary (no "great schools")
- [ ] Active voice: entity acts, entity is not acted upon
- [ ] American English spelling throughout

---

## Section 7: Example Page — Fully Compliant

**Page:** Houston Relocation Guide (Canonical Predicate: **LEARN**)

> **HEADLINE:** Discover Houston's Relocation Landscape — From Inner-Loop Lofts to Katy Master-Planned Communities
>
> Houston spans 669 square miles across three counties, accommodating 2.3 million residents within city limits. The Greater Houston metropolitan area extends to 10,062 square miles, encompassing nine counties and hosting 7.3 million people as of the 2024 census estimate.
>
> Katy ISD serves 93,000 students across 77 campuses, ranking in the top 5% of Texas school districts for college readiness. Homebuyers relocating with school-age children discover Katy's per-pupil expenditure of $12,400 exceeds the Texas state average by $1,200 per student.
>
> Houston commuters access the city via three primary corridors: Interstate 10 (Katy Freeway), Highway 290 (Northwest Freeway), and the Westpark Tollway. The average Katy-to-Downtown commute spans 29 minutes during peak hours — 11 minutes below the national average for suburban-urban transit.
>
> New-construction homes in Katy price from $280,000 for entry-level inventory to $1.2 million for estate properties in gated communities. Houston homebuyers discover Katy's median price-per-square-foot of $168 falls $44 below the Houston metro average, according to HAR MLS December 2025 data.
>
> Walzel Properties licensee Quan Nguyen (license #0774451) guides relocating buyers through Katy's 14 active master-planned communities. Schedule a relocation consultation to receive a customized community match based on your school, commute, and new-construction preferences.

**Analysis:**
- Predicate consistency: discover (×3), guide → all LEARN family
- Entity-first: every sentence starts with subject entity
- No modality: zero hedging words
- Bridge vocabulary: ISD, corridor, master-planned, median price-per-square-foot
- Numeric attributes: 669 sq miles, 2.3M, 93,000 students, $12,400, $168/sq.ft., $44 below median
- One entity per paragraph: Houston → Katy ISD → commute → pricing → Walzel

---

*Engine: Koray Gubur Phase 1 Foundational Primitives — Content Quality & Linguistics + Python & Data-Driven SEO. 23 grounded rules processed. Vocabulary bank extracted via WordNet 3.1. Canonical predicates mapped to quann.homes domain entities.*
