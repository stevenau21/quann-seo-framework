# Cost of Retrieval Architecture — Quann.Homes

**Date:** 2026-05-04
**Status:** Defined

> **Related:** [Cost of Retrieval (Per Spoke)](../09-research/cost-of-retrieval-per-spoke.md) — specific format assigned to each of Quan's 12 spokes. [SERP Feature Mapping](../09-research/serp-feature-mapping.md) — which format Google expects per query.

## What Is Cost of Retrieval?

Per the methodology: search engines have limited resources for crawling and indexing. A site that is computationally "cheap" for Google to process will outrank a "noisy" disorganized competitor. This is achieved through strategic page segmentation — deciding what information goes where, and using semantic HTML to make extraction trivial.

---

## Page Segmentation Strategy

### Segment Types (Priority Order for Google Extraction)

| Segment | Best For | Google Extraction Ease | Example |
|---|---|---|---|
| **Table** (`<table>`) | Comparisons, checklists, specs, cost breakdowns | 🔴 Fastest — structured data | FHA vs Conventional loan comparison |
| **Definition List** (`<dl>`) | Term-definition pairs, glossaries | 🟡 Fast | Knowledge Domain Terms with plain English translations |
| **Ordered List** (`<ol>`) | Step-by-step processes, rankings, timelines | 🟡 Fast | "10 Steps to Buying Your First Home in Texas" |
| **Unordered List** (`<ul>`) | Features, pros/cons, requirements, categories | 🟡 Fast | "What You Need for Mortgage Pre-Approval" |
| **Short Paragraphs** (2-3 sentences) | Explanations, context, bridges | 🟢 Moderate | Declarative facts with supporting detail |
| **Long Paragraphs** (5+ sentences) | Deep analysis, storytelling | 🔴 Slowest — high extraction cost | Avoid unless absolutely necessary |
| **Pull Quotes / Callouts** (`<blockquote>`) | Key statistics, memorable phrases | 🟡 Fast if marked up | "The median home in Katy sells in 12 days." |

---

## Page Layout Templates

### Template A: Buyer Guide (Informational → Do)

```
[H1] Title with Central Entity + Target Entity

[2-3 sentence intro — what this page covers, why it matters]
  → Short paragraph

[TABLE: Quick Facts / At a Glance]
  → Key numbers in scannable format

[H2] Section 1 — [Core concept]
  [OL] Step-by-step breakdown
  [Short paragraph] Explanation per step

[H2] Section 2 — [Secondary concept]
  [TABLE] Comparison (e.g., programs side-by-side)

[H2] Section 3 — [Actionable section]
  [UL] Checklist / Requirements / Next Steps

[H2] FAQ section
  [DL] Term: Definition pairs for quick answers

[Contextual Bridge paragraph — 2-3 sentences]
  → Answers "now what?" → links to Core Section (Schedule Call)

[CTA] Schedule a Consultation
```

### Template B: Neighborhood Guide (Informational → Know)

```
[H1] Living in [Neighborhood], TX — Complete Guide

[TABLE: Neighborhood at a Glance]
  Median price | School district | Commute | Walk score | Property types

[H2] What It's Like to Live Here
  [Short paragraphs — 2-3 sentences each]
  Vibe, who lives here, what's nearby

[H2] Housing Market Snapshot
  [TABLE] Price trends (YOY), DOM, inventory, price/sqft
  [Short paragraph] What the numbers mean for buyers

[H2] Schools
  [UL] School ratings, programs, boundaries

[H2] Pros and Cons
  [TABLE] Left: Pros | Right: Cons

[H2] Similar Neighborhoods
  [UL] Linked comparisons

[Contextual Bridge → Schedule a personal tour]
```

### Template C: Transactional Page (Sell / List / Invest)

```
[H1] [Service] with Quan Nguyen — [Value proposition]

[Pull quote] Key differentiator or stat

[H2] How It Works
  [OL] 4-5 step process
  [Short paragraph per step]

[H2] Why Work With Quan
  [UL] Differentiators (license, tools, approach)

[H2] What It Costs
  [TABLE] Fee breakdown / comparison

[H2] Results
  [TABLE] Recent sales, DOM, list-to-sale ratio

[CTA] Get Started — Schedule Call
```

---

## Semantic HTML Rules

### Every Page Must Have

1. **One `<h1>`** — contains Central Entity + page entity
2. **`<h2>` for sections** — never skip levels. `<h2> → <h3>`, never `<h2> → <h4>`
3. **Tables with `<thead>` and `<tbody>`** — never layout tables, always data tables
4. **Proper list markup** — `<ol>` for ordered, `<ul>` for unordered. Never use `•` or `1)` as text
5. **Breadcrumb structured data** — `BreadcrumbList` JSON-LD on every page
6. **FAQ structured data** — `FAQPage` JSON-LD on pages answering multiple questions

### JSON-LD on Every Page

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "about": {"@id": "https://quann.homes/#agent"},
  "breadcrumb": {
    "@type": "BreadcrumbList",
    "itemListElement": [...]
  }
}
```

---

## Extraction Cost Scorecard

| Factor | Low Cost (Good) | Medium Cost | High Cost (Bad) |
|---|---|---|---|
| Semantic HTML | ✅ Tables, lists, proper headings | ⚠️ Some div-heavy sections | ❌ All divs, no structure |
| Paragraph length | ✅ 2-3 sentences max | ⚠️ 4-5 sentences | ❌ Wall of text |
| Entity density | ✅ Named entities throughout | ⚠️ Some entities present | ❌ No named entities, all pronouns |
| Structured data | ✅ JSON-LD on every page | ⚠️ Only on homepage | ❌ No structured data |
| Image alt text | ✅ Descriptive, entity-rich | ⚠️ Generic ("house.jpg") | ❌ No alt text |
| Mobile rendering | ✅ No horizontal scroll | ⚠️ Minor overflow | ❌ Broken on mobile |

---

## Page Character Analysis — Per Spoke

**Principle:** Beyond HTML structure, Google evaluates whether a page's *visual-semantic character* matches the expected result type for that query. If the top 3 results for "Texas luxury property taxes" all feature HTML comparison tables, a page using only numbered lists has a **discordant character** — it fails the Information Foraging expectation and ranks lower.

### Character Types

| Character Type | Visual-Semantic Cue | Best For | Google's Expectation |
|---|---|---|---|
| **Comparator** | Side-by-side table, column alignment | FHA vs Conventional, neighborhood comparisons | User expects to scan horizontally across options |
| **Calculator** | Input fields + dynamic output | Affordability, mortgage payment, closing cost estimate | User expects interactive tool, not static text |
| **Step Sequencer** | Numbered list with clear phases | FTHB process, pre-approval, relocation checklist | User expects chronological progression |
| **Definer** | Bold term + plain-English definition pairs | Knowledge Domain Terms, TREC concepts, MUD/PID | User expects rapid term lookup |
| **Data Sheet** | Stat-heavy with tables and source citations | Market stats, tax rates, school ratings | User expects authoritative numbers |
| **Narrative Bio** | Photo + timeline + testimonial blocks | About Quan, Client Success Stories | User expects personal/professional story |
| **Map + Table** | Geographic data paired with comparison table | Commute guide, neighborhood guide | User expects spatial + tabular data together |

### Spoke-to-Character Assignment

| Spoke | Required Character | Page Must Feature | Competitor Gap |
|---|---|---|---|
| First-Time Home Buyer Process | **Step Sequencer** | Numbered phases with Texas-specific docs at each step | Most are generic 10-step lists |
| Out-of-State Relocation | **Data Sheet + Step Sequencer** | Cost comparison table + relocation timeline | Most are moving-company blogs |
| Builder Incentives / Get Paid to Buy | **Comparator + Definer** | Incentive type table + negotiation term glossary | Almost no content exists |
| Katy Neighborhood Guide | **Comparator + Map + Table** | Side-by-side table + embedded map + price/school data | Most are national listicles |
| Katy ISD School Guide | **Data Sheet + Definer** | Rating table + feeder pattern diagram + term glossary | Third-party sites, not agent-authored |
| New Construction Communities | **Comparator** | Builder × price range × incentive table | Builder sites dominate — no comparison |
| Commute Guide | **Map + Table** | Commute time table (neighborhood × destination) | Google Maps — no agent context |
| Down Payment Assistance | **Comparator + Step Sequencer** | Program comparison table + eligibility checklist | Government sites — hard to navigate |
| FHA vs Conventional | **Comparator** | Side-by-side table (down, PMI, limits, rates) | National lending sites, not Texas-specific |
| Closing Costs | **Data Sheet + Definer** | Line-item breakdown table + term definitions | National averages, not Texas line items |
| Pre-Approval Process | **Step Sequencer** | Document checklist + timeline + "what lenders skip" | Lender-biased, not agent-advocate |
| About Quan | **Narrative Bio** | Photo + timeline + certs + testimonials + CTA | Generic bios without EAV triples |

### Character Discordance Check (Before Publish)

For every page, ask:
1. What's the dominant SERP format for this query? (open Google, look at top 3)
2. Does my page use the same visual-semantic character? (if they use tables, I must use tables)
3. Does my page go *beyond* the expected character? (their table has 4 columns — mine has 6 with Texas-specific data)

If the answer to #2 is "no," the page is broken regardless of content quality. Fix the character first.

---

## Rule

> Every decision about page layout answers two questions: "Does this make extraction cheaper for Google?" AND "Does this match the visual-semantic character Google expects for this query?"
