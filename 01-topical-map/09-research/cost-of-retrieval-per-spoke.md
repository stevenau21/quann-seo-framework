# Cost of Retrieval Architecture — Quann.Homes

**Date:** 2026-05-05
**Status:** Pre-execution baseline — specific data format assignments per spoke
**Methodology:** Search engines normalize HTML to extract facts. The computational cost of extraction affects indexing priority. Organized, semantic HTML that is "cheap" to process gets indexed faster and ranked higher than disorganized "noisy" pages.

---

## The Core Principle

Every page layout decision answers: **"Does this make extraction cheaper for Google?"**

A page built with tables for data, lists for steps, and definition lists for terms is algorithmically "responsive" — Google extracts facts in one pass. The same information in wall-of-text paragraphs costs Google more CPU cycles and may be deprioritized.

---

## Data Format Assignment Rules

| Data Type | Best Format | Why It's Cheapest | When to Use |
|---|---|---|---|
| **Numbers / stats / comparisons** | `<table>` with `<thead>`+`<tbody>` | Structured extraction in one pass | Market data, loan comparisons, cost breakdowns |
| **Term-definition pairs** | `<dl>` (definition list) | Machine-readable term→definition mapping | Glossary sections, "what is X" sections |
| **Steps / processes / timelines** | `<ol>` (ordered list) | Sequential extraction — preserves order | Buying process, application steps, checklist order |
| **Features / pros-cons / requirements** | `<ul>` (unordered list) | Extraction without order constraint | Program features, eligibility, pros/cons |
| **Key fact / statistic** | `<blockquote>` or `<figure>` | Isolated extraction — not buried in text | Pull quotes, "did you know" callouts |
| **Explanation / context** | Short paragraph (2-3 sentences) | Moderate cost — acceptable for bridges | Contextual bridges, introductions |
| **Deep analysis** | Long paragraph (5+ sentences) | Highest cost — avoid if possible | Only when genuinely needed |

---

## Per-Spoke Format Assignment

### Pillar 1: Buying in Texas

#### Spoke: First-Time Home Buyer Process
| Content Section | Format | Why |
|---|---|---|
| "Quick facts about buying in Texas" | `<table>` | Median price, avg DOM, typical down payment — scannable |
| "10 steps to buying your first home" | `<ol>` | Sequential process — natural ordered list |
| "What you'll need for pre-approval" | `<ul>` | Requirements — unordered |
| Per-step explanation | Short paragraph (2-3 sentences) | Context per step |

#### Spoke: FHA vs Conventional Loans
| Content Section | Format | Why |
|---|---|---|
| Comparison table | `<table>` | FHA vs Conventional — minimum down payment, credit score, PMI/MIP, limits — side-by-side is THE format |
| "Which loan is right for you?" | Short paragraph + `<ul>` | Decision framework in list form |
| "FHA loan details" | `<dl>` | Terms like MIP, UFMIP, loan limits as term→definition |

#### Spoke: Down Payment Assistance Programs
| Content Section | Format | Why |
|---|---|---|
| "Programs at a glance" | `<table>` | TDHCA My First Texas, My Choice, MCC, local programs — name + amount + eligibility + income limit as columns |
| "Do you qualify?" | `<ul>` | Checkbox-style eligibility list |
| Per-program details | Short paragraph | One paragraph per program |
| "How to apply" | `<ol>` | Sequential application steps |

#### Spoke: Closing Costs in Texas
| Content Section | Format | Why |
|---|---|---|
| "Closing cost breakdown" | `<table>` | Line items: lender fees, title fees, escrow, prepaids, taxes — item + typical cost + who pays |
| "What are prepaids?" | `<dl>` | Escrow cushion, per diem interest, tax proration as term→definition |
| "Who pays what?" | `<table>` | Buyer vs seller responsibility per line item |

#### Spoke: Mortgage Pre-Approval
| Content Section | Format | Why |
|---|---|---|
| "Documents you'll need" | `<ul>` | W-2s, pay stubs, bank statements, tax returns — checklist format |
| "Pre-approval vs pre-qualification" | `<table>` | Two columns: pre-qual vs pre-approval — feature comparison |
| "The pre-approval process" | `<ol>` | 4-5 steps in order |

#### Spoke: First-Time Buyer Mistakes
| Content Section | Format | Why |
|---|---|---|
| "Top mistakes (ranked)" | `<ol>` | Ordered by frequency/cost — natural numbered list |
| Per-mistake detail | Short paragraph + "how to avoid" in `<ul>` | Mistake → explanation → avoidance tips structure |
| "Mistake cost impact" | `<table>` | Mistake → potential cost → how Quan prevents it |

### Pillar 2: Katy & Houston Areas

#### Spoke: Katy Neighborhood Guide
| Content Section | Format | Why |
|---|---|---|
| "Neighborhoods at a glance" | `<table>` | Neighborhood + median price + school zone + commute + vibe — comparison table |
| "What it's like to live here" | Short paragraphs (2-3 sentences each) | Descriptive — acceptable as short text |
| "Housing options" | `<ul>` | SFH, townhome, condo, new construction — property types available |
| "Pros and cons" | `<table>` | Two-column pro/con per neighborhood |

#### Spoke: Katy ISD School Guide
| Content Section | Format | Why |
|---|---|---|
| "School ratings (TEA)" | `<table>` | School + rating + grade levels + programs — structured data |
| "School zone map overview" | Short paragraph + link to interactive map | Description + functional component |
| "What ratings mean" | `<dl>` | A/B/C rating system as term→definition |
| "School → neighborhood mapping" | `<table>` | Which elementary feeds which middle feeds which high school |

#### Spoke: New Construction Communities
| Content Section | Format | Why |
|---|---|---|
| "Active communities" | `<table>` | Community + builder + price range + sqft range + incentives — comparison |
| "Builder comparison" | `<table>` | Builder + reputation + standard features + incentive typical range |
| "New vs existing homes" | `<table>` | Two columns — pros/cons, cost factors, timeline |

#### Spoke: Commute Guide (Katy → Houston)
| Content Section | Format | Why |
|---|---|---|
| "Commute times by corridor" | `<table>` | Destination + peak time + off-peak + toll cost — structured data |
| "Toll road overview" | `<dl>` | Westpark Tollway, Grand Parkway, Katy Freeway as term→definition with cost |
| "Best neighborhoods for commuters" | `<ul>` + short paragraphs | Neighborhood → commute advantage |

### Trust & Credibility

#### Spoke: About Quan Nguyen
| Content Section | Format | Why |
|---|---|---|
| "At a glance" | `<dl>` | Name + license + brokerage + phone + email + areas — entity attributes as term→value |
| "Testimonials" | `<blockquote>` | Pull quotes — semantically correct and visually distinct |
| "Quan's approach" | Short paragraphs | Narrative — acceptable as short text |
| "Certifications & memberships" | `<ul>` | List format for badges/credentials |

---

## Semantic HTML Rules

### Every Page Must Have

1. **One `<h1>`** — contains Central Entity + page entity
2. **Proper heading hierarchy** — `<h2>` for sections, `<h3>` for subsections. Never skip levels.
3. **Tables with `<thead>` and `<tbody>`** — never layout tables, always data tables
4. **Proper list markup** — `<ol>` for ordered, `<ul>` for unordered, `<dl>` for definitions. Never use `•` or `1)` as text.
5. **BreadcrumbList JSON-LD** on every page
6. **FAQPage JSON-LD** on pages containing multiple Q&A pairs

### What to Avoid

| ❌ Avoid | ✅ Use Instead |
|---|---|
| Wall of text (5+ sentence paragraph) | Break into short paragraphs + list |
| "We help you..." sentences | Declarative facts with entities |
| Images without `alt` text | Entity-rich alt text: "Katy TX new construction community by Lennar Homes" |
| `<div>` soup without semantic markers | Proper `<section>`, `<article>`, `<nav>`, `<aside>` |
| Generic meta descriptions | Entity-rich meta: "Katy TX first-time home buyer programs: TDHCA, FHA, USDA loan eligibility and down payment assistance. Quan Nguyen, REAL BROKERAGE license #0774451." |

---

## Extraction Cost Scorecard (per page)

| Factor | Low Cost (Score 5) | Medium Cost (Score 3) | High Cost (Score 1) |
|---|---|---|---|
| HTML structure | Tables + lists + `<dl>` | Some divs but structured | All divs, no semantics |
| Paragraph length | 2-3 sentences max | 4-5 sentences | Wall of text |
| Entity mentions | Named entities throughout | Some entities | No named entities |
| Structured data | JSON-LD on every page | Only on homepage | No structured data |
| Image alt text | Descriptive, entity-rich | Generic | Missing |

**Target:** Every spoke page scores 4-5 on this scale.
