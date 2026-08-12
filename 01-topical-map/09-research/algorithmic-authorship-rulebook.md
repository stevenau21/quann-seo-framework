# Algorithmic Authorship Rulebook — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Define the mathematical writing rules so every page on quann.homes is indistinguishable from a top-tier real estate expert and distinct from AI-generated content.

---

## Rule 1: Modality Removal

**Principle:** Strip all hedging language from factual statements. Experts assert. Novices hedge.

| ❌ Banned | ✅ Required |
|---|---|
| "You might find that Katy homes..." | "The median home price in Katy is $385,000." |
| "Closing costs could range from..." | "Texas closing costs average 2.6% of the purchase price." |
| "Some buyers should consider..." | "Buyers with less than 20% down pay PMI." |
| "It may be worth looking at..." | "The Katy ISD tax rate is $1.19 per $100 valuation." |

**Banned words in declarative sections:** could, might, may, should, perhaps, maybe, typically, generally, often, sometimes, some people, it's worth considering, you might want to

**Exception:** Modality is acceptable in editorial bridges between sections, but NEVER inside factual blocks, tables, definition lists, or comparison sections.

---

## Rule 2: Order of Operations — Declaration First, Condition Second

**Principle:** State the fact first. Then attach conditions, exceptions, or contextual constraints. Google's NLP extracts the main clause as the primary triple — burying the declaration inside a conditional clause degrades the extracted fact.

| ❌ Wrong Order | ✅ Correct Order |
|---|---|
| "If your down payment is under 20%, you'll need PMI." | "PMI is required when your down payment is under 20%." |
| "When the soil is expansive clay, foundation issues arise." | "Foundation issues arise from expansive clay soil — common across Katy and Houston." |
| "If you're relocating from out of state, Texas has no income tax." | "Texas has no state income tax — a key advantage for out-of-state buyers relocating from high-tax states." |

**Structural rule:** Every `<h2>` or `<h3>` section starts with a declarative sentence. The first sentence of every content block is a statement of fact. Conditions, exceptions, and context follow in subsequent sentences.

---

## Rule 3: Noun/Predicate Matching

**Principle:** Ensure the subject entity (noun phrase) and its predicate (verb/verb phrase) form a valid, domain-appropriate pair. Avoid semantic mismatches that signal non-expert writing.

| ❌ Mismatched | ✅ Matched |
|---|---|
| "Home prices experience growth." | "Home prices increase." |
| "The market demonstrates volatility." | "The market fluctuates." |
| "Buyers undergo pre-approval." | "Buyers obtain pre-approval." |

**Entity-specific predicates for Quan's 12 spokes:**

| Entity | Valid Predicates |
|---|---|
| Home price | rises, falls, averages, ranges from X to Y |
| Interest rate | determines, affects, varies by |
| Property tax | funds (school districts), varies by (county), is assessed at |
| Closing cost | includes, excludes, averages, ranges |
| FHA loan | requires, allows, caps at |
| Down payment | determines (PMI requirement), ranges from |
| Homestead exemption | reduces, caps, requires |
| MUD/PID | taxes, funds (infrastructure), expires after |
| Builder incentive | covers, includes, stacks with |

---

## Rule 4: First Word Sequence = Central Search Intent

**Principle:** The first noun phrase in each article's opening sentence must match the central search intent for that query. If someone searches "Katy home prices," the first words of the page must be about Katy home prices — not a preamble.

| ❌ Diluted | ✅ Matched |
|---|---|
| "Buying a home is one of the biggest decisions you'll ever make. Katy home prices have..." | "Katy home prices averaged $385,000 in Q1 2026, with a median price per square foot of $175." |
| "Texas has a lot to offer home buyers. FHA loans are..." | "FHA loans in Texas allow down payments as low as 3.5% on properties up to the county loan limit." |

**Preamble ban:** No opening paragraphs about "how important buying a home is." The user searched for a specific answer. Deliver it in the first sentence.

---

## Rule 5: Sentence Bank Structure

**Principle:** Every spoke page builds a bank of 15-25 declarative sentences. These are the extractable triples that populate the Knowledge Graph.

**Format:**
```
[ENTITY] → [PREDICATE] → [VALUE/OBJECT]
```

**Examples for Quan's content:**

```
Katy median home price → is → $385,000
Texas closing costs → average → 2.6% of purchase price
Homestead exemption → caps → taxable value increase at 10% per year
MUD tax → funds → water, sewer, drainage infrastructure in new communities
FHA loan limits → cap at → $472,030 in Harris County (2025)
Builder incentive → can include → closing cost credit, rate buydown, upgrade allowance
```

---

## Rule 6: Anti-Patterns (Never Do These)

1. **AI word salad openers:** "In the vibrant and ever-evolving landscape of Texas real estate..."
2. **Question stacking:** Opening with 3-4 rhetorical questions instead of delivering the answer
3. **Fluffy transitions:** "Now that we've covered X, let's explore Y." Just state Y.
4. **Personal opinion without citation:** "I think Katy is the best suburb." → "Katy is ranked #3 best Houston suburb by..."
5. **Buried conclusions:** The answer should be in the first paragraph, not the last.

---

## Rule 7: Discourse Integration (Concept Sequencing)

**Principle:** Search engines check for "coherence" by examining the sequence of concepts across sentences. If sentence A discusses "Closing Costs" and sentence B abruptly switches to "Backyard Landscaping" without a connecting bridge, the document's relevance score drops. Every sentence must flow from the previous one via shared entities.

| ❌ Broken Discourse | ✅ Integrated Discourse |
|---|---|
| "Texas closing costs average 2.6%. Backyard landscaping adds resale value." | "Texas closing costs average 2.6%. Once you've budgeted for closing, consider what adds long-term value — starting with landscaping, which recovers 100% of its cost at resale." |
| "FHA loans require 3.5% down. Katy ISD is rated A." | "FHA loans require 3.5% down — making Katy homes accessible to first-time buyers. Katy ISD's A rating from TEA adds another reason buyers target this area." |

**The Bridge Rule:** Every paragraph transition must share at least one entity (noun or concept) with the paragraph before it. If no natural entity exists, insert a one-sentence contextual bridge.

**Example Bridge:**
> "[Previous concept] connects directly to [next concept] because..."

---

## Rule 8: Modality Matching (Match the Query's Linguistic Profile)

**Principle:** The previous Rule 1 banned modality in declarative/factual sections. But when a query itself is modal, the response MUST match that modality. If a user searches "Should I buy a home in Texas right now?", the answer must engage with "should" — not dodge it with a purely declarative answer.

| Query Type | Required Response Modality | Example |
|---|---|---|
| "Should I...?" | Must use should/could/ought to in bridge, then ground in facts | "Whether you **should** buy right now depends on your timeline. Here's the data to make that call: rates are at X, inventory is at Y..." |
| "Can I...?" | Must use can/be able to | "You **can** qualify for an FHA loan with a 580 credit score. Here are the exact steps..." |
| "What is...?" | Zero modality. Pure declaration. | "The homestead exemption is..." (no should/could/might) |
| "How do I...?" | Imperative + declaration | "Obtain pre-approval by submitting these three documents..." |

**The Modality Rule:** Match the query's modality in your opening paragraph. Then transition to Rule 1 (modality removal) for the factual body. The opening acknowledges the user's linguistic frame. The body delivers grounded expertise.

**Exception to Rule 1 (revised):**
- Banned in: factual blocks, tables, definition lists, comparison sections, statistics
- Permitted in: opening paragraph (when matching query modality), editorial bridges between sections, CTA language ("Should we schedule a call?")
- Required in: answers to modal queries ("Should I buy?", "Can I qualify?") — match the modality, then ground in facts

---

## Enforcement

| Layer | How |
|---|---|
| Content briefs | Every brief includes 15+ declarative sentences in the Sentence Bank section |
| Writer guidelines | Writers receive this document. Every draft checked against rules 1-6. |
| Editorial review | Before publish: scan for banned modal verbs. Check first sentence matches title intent. |
