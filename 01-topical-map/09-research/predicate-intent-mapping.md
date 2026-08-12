# Predicate & Intent Mapping — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Map every content page to its correct search intent via precision predicates (verbs). Search engines index the world in triples — [Subject] → [Predicate] → [Object]. Wrong verbs = wrong classification. Static keywords say what you're about. Verbs say what you *do*.

---

## Core Principle

A page about "Texas luxury homes" using verbs like "wonder," "explore," and "imagine" gets classified as **editorial content**. The same page using "negotiate," "acquire," and "maximize" gets classified as a **service page**. The difference determines whether Google shows your page to a buyer ready to act or a browser killing time.

---

## Intent-to-Predicate Mapping

### Intent: Learn (Informational / Know)

User wants to understand a concept. They are NOT ready to transact.

| ✅ Use These Predicates | ❌ Avoid |
|---|---|
| understand, define, explain, break down, clarify, distinguish, identify | buy, schedule, hire, acquire, negotiate |

**Example sentence structures:**
> "First-time home buyers often confuse pre-qualification with pre-approval. Here's how to **distinguish** them."
> "The homestead exemption **caps** your taxable value increase at 10% per year."
> "We **break down** Texas closing costs line by line so nothing surprises you at the table."

### Intent: Compare (Commercial Investigation)

User is evaluating options. They are comparing A vs B before deciding.

| ✅ Use These Predicates | ❌ Avoid |
|---|---|
| compare, contrast, weigh, stack up, differ, outperform | learn, explore, wonder (too passive) |

**Example sentence structures:**
> "FHA loans **differ** from conventional loans in three critical ways: down payment minimums, PMI duration, and property standards."
> "We **weigh** Katy neighborhoods across price, schools, and commute — side by side."

### Intent: Do / Act (Transactional)

User is ready to move. They want to execute.

| ✅ Use These Predicates | ❌ Avoid |
|---|---|
| apply, qualify, obtain, schedule, lock in, secure, claim, capture | understand, learn, explore (wrong funnel stage) |

**Example sentence structures:**
> "**Lock in** your mortgage rate before the Fed's next meeting."
> "Texas down payment assistance programs let you **qualify** with as little as $500 out of pocket."
> "**Capture** builder incentives worth $5,000–$15,000 on new construction homes."

### Intent: Maximize / Negotiate (Quan's Differentiator)

User wants an edge. Quan's unique value proposition.

| ✅ Use These Predicates | ❌ Avoid |
|---|---|
| maximize, negotiate, capture, stack, leverage, reduce, offset | consider, think about, maybe (hedging kills authority) |

**Example sentence structures:**
> "We **negotiate** builder incentives most buyers don't know exist."
> "**Stack** closing cost credits with lender rate buy-downs and builder upgrade allowances."
> "**Reduce** your effective purchase price by **leveraging** the option period strategically."

---

## Predicate-to-Page Assignment (12 Spokes)

| Spoke | Primary Intent | Mandatory Predicates | Page Classification |
|---|---|---|---|
| First-Time Home Buyer Process | Learn | understand, identify, prepare | Informational guide |
| Out-of-State Relocation Guide | Learn + Compare | compare, weigh, break down | Informational + commercial |
| Builder Incentives / Get Paid to Buy | Maximize | negotiate, capture, stack, leverage | Service page |
| Katy Neighborhood Guide | Compare | compare, contrast, rank | Comparison tool |
| Katy ISD School Guide | Learn + Compare | distinguish, compare, feed into | Informational + comparison |
| New Construction Communities | Compare + Do | compare, identify, tour | Commercial investigation |
| Commute Guide (Katy → Houston) | Learn | estimate, plan, map | Informational tool |
| Down Payment Assistance Programs | Do | qualify, apply, access | Transactional |
| FHA vs Conventional Loans | Compare | compare, differ, weigh | Comparison tool |
| Closing Costs in Texas | Learn + Do | break down, budget, reduce | Informational + transactional |
| Mortgage Pre-Approval Process | Do | obtain, prepare, accelerate | Transactional |
| About Quan Nguyen | Website | represent, serve, specialize | Entity anchor |

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| Use "learn" on a page where Quan wants them to schedule | Use "schedule," "book," "reserve" |
| Use "buy" on a purely educational page | Use "understand," "prepare," "equip" |
| Mix intent predicates on one page | One primary intent per page. Match all predicates to it. |
| Hedge transactional verbs: "you might want to apply" | "Apply for Texas DPA. Here's how." |

---

## Predicate Consistency Rule

Once you assign a primary intent to a page, **every predicate on that page** must belong to the same intent family. A page that uses "understand" in paragraph 1, "buy" in paragraph 3, and "explore" in paragraph 5 has no coherent intent signal. The search engine can't classify it — so it ranks for nothing.

---

## Semantic Role Labeling (SRL) SOP: Agent-Object Logic

Predicate mapping tells the engine *what action* the page performs. Semantic Role Labeling tells the engine **who is doing it to whom** — and consistency here is what makes indexing cheap.

### The Problem: Role Inversion

Every time you flip the Agent ↔ Object relationship, the search engine must perform an extra **normalization pass** to reconcile the inconsistency. Normalization is computationally expensive. Search engines optimize for domains that never force unnecessary normalization.

| ❌ Role Inversion (Expensive) | ✅ Consistent Role Assignment (Cheap) |
|---|---|
| "The house was sold to the buyer." → "The buyer acquired the house." | "The buyer acquires the home." → "The buyer secures financing." → "The buyer closes on the property." |
| "Builder incentives are offered by the developer." → "The agent negotiates the incentive." | "The builder offers incentives." → "The builder structures upgrades." → "The builder allocates closing cost credits." |
| "The loan is approved by the lender." → "The buyer applies for financing." | "The buyer applies for the loan." → "The buyer submits documentation." → "The buyer receives pre-approval." |

In every inverted example, the engine must resolve two different syntactic structures that encode the same semantic fact. That resolution consumes crawl budget and indexing priority.

### SRL Role Definitions

For Quan's content, define these fixed role assignments:

| Role | Definition | Quan's Content Assignment |
|---|---|---|
| **Agent** | The entity performing the action (the "doer") | The Buyer (Quan's client) — for all buyer-content spokes |
| **Theme / Patient** | The entity the action is performed upon | The Home / The Transaction / The Loan |
| **Recipient / Beneficiary** | The entity that receives the outcome | The Buyer (again — buyer is both Agent and Beneficiary) |
| **Instrument** | The means by which the action is performed | Quan Nguyen / The Quantum Team / REAL BROKERAGE |
| **Location** | Where the action occurs | Texas / Katy / Houston metro |

### Per-Spoke Role Template

Every spoke page must open with a Role Declaration block that locks the role assignments before the first sentence is written:

```
<!-- SRL ROLE DECLARATION — DO NOT DEVIATE -->
Agent: The Texas Home Buyer
Theme: The Home Purchase Transaction
Recipient: The Buyer (same entity — self-benefiting action)
Instrument: Quan Nguyen / The Quantum Team
Location: [Katy, TX | Houston Metro | Texas — per spoke]
```

### The SRL Consistency Rule

Once you declare the role assignments for a page:

1. **The Agent never becomes the Object** of a passive construction. No "The home was bought by..." — the Buyer is ALWAYS the subject of active verbs.
2. **The Instrument (Quan) is never the Agent** on buyer-content pages. The buyer takes action. Quan enables. "Quan negotiates" is correct when Quan is the Agent, but that sentence belongs on the About page, not a buyer education page.
3. **Location roles stay static.** Don't write "Texas offers homestead exemptions" and then "Homeowners in Texas receive exemptions." The first makes Texas the Agent. The second makes the Homeowner the Agent. Pick one and stick with it.

### The Normalization Cost Analogy

Think of inconsistent SRL like a database with duplicate records in different schemas. The query engine must run `DISTINCT` and `UNION` operations before it can produce a result. Search engines penalize domains that force them to de-duplicate semantic roles — it's the same cost logic. Consistent SRL = pre-normalized data = cheaper to index = higher ranking priority.
