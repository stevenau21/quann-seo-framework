---
name: seo-topical-map
description: Build a complete semantic SEO topical map using dual LightRAG servers — SEO methodology RAG (port 8002) for the framework, Quann Chat RAG (port 8001) for business data. Never bypass RAG to raw sources. Yields 38-file architecture with 11 precision layers.
---

# SEO Topical Map Construction (Quann.Homes)

Build a complete topical map for quann.homes using two LightRAG servers in tandem. Follow the holistic SEO methodology strictly — treat RAG servers as the intended retrieval path, not raw page scraping.

## Operating Mode (Lead Architect ↔ Domain Expert)

This skill operates under a strict role division. Violating this dynamic is the single most damaging error pattern.

**Agent = Lead SEO Architect.** You dictate the workflow. You prescribe the strategy. You determine what pages must exist using the 534 Koray rules as your decision engine. Do NOT ask the user for step-by-step guidance or methodology approval — they hired you to be the expert. When you need a domain fact (e.g., "what brokerage are you with now?"), ask once, record it, and move on. Do NOT ask operational questions like "do you have Framer access?" or "do you have a Google Cloud account?" — prescribe the requirement, and the user will flag if blocked.

**User = Real Estate Domain Expert.** They supply raw domain facts (brokerage name, service areas, license numbers, business goals) and quality-check outputs for real-estate accuracy. They do NOT guide SEO methodology, choose frameworks, or validate workflow sequencing. That is your job.

**Citation Requirement (Mandatory):** Every strategic decision, every page prescription, and every workflow step MUST cite a specific Koray framework rule (card ID + rule text). Format: `[Rule: Framework Name, Card #ID]`. If no Koray rule justifies a strategy, do NOT suggest it. Generic "SEO best practices" without a framework citation are banned.

**Autonomous Resource Allocation (Mandatory):** For every phase, the Lead Architect must automatically split the work into ENGINE tasks (algorithmic — PageRank, schema generation, WordNet extraction, vocabulary banks) and HUMAN tasks (copywriter briefs, platform profile creation, visual verification). Do NOT ask the Domain Expert how to format output or who should do what. The engine computes the split internally and produces separate deliverables: one for the machine (JSON, data files, schemas) and one for the human (plain-English checklists, copywriter manuals, action items). If a task is algorithmic, execute it silently — the human only sees results that matter to them.

**Phase Progression:** After each phase, report what was generated (engine artifacts + human deliverables) and automatically proceed to the next phase in the dependency DAG order. Do not wait for the Domain Expert to approve each phase — their role is domain-fact quality-check, not methodology validation.

**Copywriter-Ready Output:** Every deliverable must be immediately usable by a non-SEO copywriter. No "predicate-intent mapping tables" or "NLI entailment tier verification protocols" in the final output — those are your internal tools. The copywriter receives: page title, audience, 5 things to cover, what to link to, in plain English. The expert SEO methodology layers (EAV triples, predicate enforcement, entailment gates) are YOUR pre-publish validation checklist, not their reading material.

**Koray Dependency DAG:** Before building any content, run the dependency extraction engine at `dependency_dag.py` to determine the mathematically correct framework execution order. See `references/koray-dependency-dag.md` for the engine specification. Phase 1 (Foundational Primitives) runs first, always.

## Critical Rules

1. **NEVER bypass RAG to raw sources** — no direct curl to sitemaps, no raw HTML scraping, no Weaviate chunk pulls. The RAG + reranker IS the retrieval path. User will get frustrated if you go around it.
2. **Dify is PERMANENTLY dead** — do not revive, do not try to fix, do not reference. All work uses LightRAG servers.
3. **Diagnose model before extending timeout** — if a RAG query times out, check which model the server is using FIRST, then check health log for response time variance.
4. **GROUND, DON'T SPECULATE** — never build content pillars, spokes, bridges, or frameworks around services the business merely *mentions* but hasn't built content for. A service listed in RAG/chat ≠ a confirmed content pillar. If the business has zero pages on a topic, it's a gray zone — wait for explicit confirmation before building.

## Alignment Audit (Run Before Any Build)

Before creating a topical map, separate what's **confirmed by existing content** from what's **mentioned but unbuilt**:

| Status | Evidence | Action |
|---|---|---|
| ✅ Confirmed | Page exists on site, or approved in Source Context | Build it |
| ⚠️ Signaled | Source Context mentions it, but no pages exist | Flag it, build only if explicitly prioritized |
| ❓ Mentioned | RAG/chat lists it as a service, zero content | Gray zone — ask, don't assume |
| ❌ No evidence | Nothing in site, RAG, or Source Context | Do not build |

**Common failure mode:** RAG returns "services: buying, selling, investing." Agent builds pillars for all three. But only "buying" has actual content. Seller and investor pillars are noise.

External profiles follow the same pattern: **discovery mode** (do they exist?) not **audit mode** (fix what should exist). Don't build 13-platform audit frameworks when you haven't verified a single profile.

## Which RAG for What

| RAG Server | Port | Model | Knowledge | Use For |
|---|---|---|---|---|
| SEO Methodology | 8002 | `deepseek-v4-pro:cloud` | holisticseo.digital | Topical map methodology, EAV model, entity SEO, content briefs, backlink strategy, competitor analysis framework |
| Quann Chat | 8001 | `gemma4:31b-cloud` | quann.homes scraped content | Quan's business data: services, areas, buyer types, brand identity, existing content |

Query pattern (always POST with `Content-Type: application/json`):
- SEO: `/ask` with `{"query": "..."}`
- Quann Chat: `/chat` with `{"message": "..."}`

## Source Context (Approved)

> Quan Nguyen helps Texas home buyers bridge the knowledge gap before the biggest purchase of their life. Through accessible area guides, conversational tools, and a warm/no-pressure approach, he reduces the overwhelm of real estate so buyers feel confident enough to take the next step. When they're ready, he becomes the agent they trust to close the deal.

## Methodology Order (Follow Strictly)

1. **Define Source Context** — intersection of brand identity + business model (the primary focus Google evaluates)
2. **Identify Central Entity** — Quan Nguyen (#0774451, Walzel Properties, The Quantum Team). Must appear site-wide in headers, footers, JSON-LD schema.
3. **Establish Web Entity** — audit GBP, Wikidata, Zillow, HAR.com, social profiles. NAP consistency across all.
4. **Extract EAV Triples** — for every entity type (service, location, audience, property, financial, process), run through universal attribute categories: definition, types, steps, benefits, costs, requirements, comparisons, FAQs, tools, statistics, timeline, mistakes, best practices, local specifics.
5. **Convert to Query Templates** — eight patterns: Entity+Attribute+Value, Attribute+Entity, Value+Entity, Location+Entity+Attribute, Question-Based, Comparison, Intent-Driven, Long-Tail Compound. Also identify zero search volume gems.
5.5. **Query Network Classification** — [Rule: Koray Lecture 1, lines 15-33] BEFORE building the topical map, classify the Domain KG's most frequent entity types. This is the translation layer between abstract framework sequence and concrete client execution. Steps: (a) query the Domain KG for entity type frequency distribution, (b) identify the dominant entity type (geographic, product-category, service-category, persona, temporal), (c) group by broad proximity — for geographic: continent→country→state→county→city; for product taxonomy: category→subcategory→brand→SKU; for SaaS: industry→vertical→use-case, (d) build the broad-layer map borders that will form the URL hierarchy's top levels. This step ensures the map starts at the broadest relevant layer before narrowing to service attributes. The classification determines which dimension of proximity the information tree descends — it is the mechanism that answers "for THIS client, does the map descend by geography, product category, or industry?" A buyer's agent in Katy TX descends geographically (Texas→Houston Metro→Katy→Neighborhoods). A SaaS company descends by industry (Enterprise→Mid-Market→SMB). A product company descends by taxonomy. Without this step, the topical map starts at the service level and the URL hierarchy has no broad-layer borders — the map is flat instead of hierarchical. See `seo-framework-execution` skill for the structural gap in the dependency DAG (missing data-artifact nodes).
6. **Build Topical Map** — Start from the broad-layer borders established in Step 5.5. Then narrow: which pillars have actual pages on the site? Which are explicitly committed in the approved Source Context? Build only those. Services merely mentioned in RAG but with zero content are gray zone — flag them, don't build them. Each confirmed pillar gets hub page + spoke cluster. Hub-and-spoke internal linking: every spoke links up to hub, every hub links down to spokes, cross-link related spokes.
7. **Write Content Briefs** — each brief needs: target entity, search intent, parent pillar, LSI terms, entity relationships, declarative sentence bank, internal link map, questions answered, competitor gap.
8. **Backlink Strategy** — prioritize contextual relevance over DA. Local news, Chamber of Commerce, HAR.com, Walzel Properties network, client reviews, local blogs. No generic guest posts.

## Content Brief Template (9-Field Validated Structure)

After expert SEO agent validation (WordNet), the brief follows this exact hierarchical sequence:

```
1. ROUTING: H1 (front-titled), URL (IR zone, no word repetition), target entity, search intent
2. SOURCE CONTEXT ALIGNMENT: How this page justifies Quan's reason to rank for this topic
3. MACRO CONTEXT (THE ONE THING): One declarative sentence the page teaches — in H1 + first paragraph
4. EAV SENTENCE BANK: Declarative factoids featuring rare attributes + diverse numeric values
5. PREDICATE ENFORCEMENT: Intent-locked verbs (Maximize = negotiate/capture/leverage), banned modals
6. UNIQUE INFORMATION GAIN: Minimum 3 facts not in top 3 SERP results
7. ANSWER FORMAT MAPPING: Tables for data, ordered lists for process, prose for argument
8. INTERNAL LINKING (BRIDGES): Anchor text matches target H1, contextual bridges only
9. REDUNDANCY FILTER: "Delete this page → world loses info?" Yes → publish. No → rewrite.
```

## Centroid Architecture & Depth Ratios

| Centroid Status | Depth | Formats | Measurement Units |
|---|---|---|---|
| PRIMARY_CENTROID / ENTITY_ANCHOR | 4-5x more detailed than satellites | Minimum 3 formats (table + list + prose) | 3+ ($, %, time/distance) |
| SUB_CENTROID | 2-3x satellite depth | 2+ formats | 2+ units |
| SATELLITE | Lightweight | Single format ok | Minimum 1 numeric factoid |

**Centroid Damage Rule:** A Tier 1 entailment gap on a PRIMARY_CENTROID cascades to all satellite pages in that cluster. Centroid quality is the single highest-leverage SEO factor on the domain.

## NLI Entailment Enforcement

For every declarative claim on a page, verify the engine-expected entailments exist somewhere on the domain:

| Tier | Severity | Consequence If Missing |
|---|---|---|
| Tier 1 (Strict) | KBT cap | Must exist on domain before any page publishing with that claim |
| Tier 2 (Strong) | Authority weakens | Expected; missing = weaker signal vs competitors |
| Tier 3 (Contextual) | Competitive edge | Differentiator; signals deeper expertise |

**Pre-publish gate:** Extract all declarative claims → identify Tier 1 entailments → verify each exists on domain → do not publish if any gap remains unaddressed.

## About Page Ordering (ENTITY_ANCHOR)

Lead with **hard EAV assertions** (license, certifications, affiliations) in the Subordinate Text to trigger Entity Reconciliation. Strategic narrative (buyer outcomes, savings stats) follows only AFTER the entity is grounded.

## Modality Matching Edge Case

If a user query asks "Should I...?", use the modal in the heading ("Should I buy new construction or resale?") — but the sentence immediately following *must* open with "You should..." before transitioning to declarative ground-truth facts.

## Publishing: 48-Hour Window Tolerated

Ideal: simultaneous batch drop. Acceptable: Entity Anchor + PRIMARY_CENTROIDs first; satellites follow within 48 hours, linking back to live centroids.

## Sentence Structure (Google NLP Preference)

- ✅ "The median home price in Katy is $385,000."
- ❌ "You might find that Katy homes cost around $385k."
- Lead with entity (noun), never fluffy intros
- Every paragraph anchors to a specific entity
- SRL: Buyer is always Agent ("The buyer negotiates..."), never passive Object

## Phase 1: Foundation (Completed)

```
SEO-quann.homes/
├── 00-roadmap.md
├── 01-source-context/source-context.md
├── 02-central-entity/central-entity.md
├── 03-web-entity/web-entity.md
├── 04-eav-triples/eav-triples.md
├── 05-query-templates/query-templates.md
├── 06-topical-map/
│   ├── topical-map.md
│   ├── topical-borders.md
│   ├── information-gap.md
│   └── contextual-bridges.md
├── 07-content-briefs/
│   ├── content-briefs.md
│   ├── lexical-richness.md
│   └── cost-of-retrieval.md
├── 08-backlink-strategy/backlink-strategy.md
└── 09-research/
    ├── methodology-phase2-reference.md
    └── consensus-baseline.md
```

## Phase 2: Pre-Execution Blueprint (Completed)

| # | Deliverable | File |
|---|---|---|
| 1 | Topical Borders & Distances | `06-topical-map/topical-borders.md` |
| 2 | Information Gap (Zero Search Volume Nodes) | `06-topical-map/information-gap.md` |
| 3 | Consensus Baseline & Truth Range | `09-research/consensus-baseline.md` |
| 4 | Contextual Bridges | `06-topical-map/contextual-bridges.md` |
| 5 | Lexical Richness (Knowledge Domain Terms) | `07-content-briefs/lexical-richness.md` |
| 6 | Cost of Retrieval Architecture | `07-content-briefs/cost-of-retrieval.md` |

## Phase 3.5: Connective Tissue Layers (6 Layers, Completed)

These layers bridge foundations to execution — they make the topical map *operational*. Build these after the foundational architecture is solid but before writing actual content.

| # | Layer | File | Purpose |
|---|---|---|---|
| 1 | **Algorithmic Authorship Rulebook** | `09-research/algorithmic-authorship-rulebook.md` | 6+2 writing rules: modality removal, declaration-first, noun/predicate matching, first-word-sequence intent, sentence bank EAV, anti-patterns, discourse integration (Rule 7), modality matching (Rule 8) |
| 2 | **Distributional Semantics** | `09-research/distributional-semantics.md` | Site-wide n-gram clusters, boilerplate optimization for header/footer/sidebar, anchor-text rules, composite score targets |
| 3 | **SERP Feature Mapping** | `09-research/serp-feature-mapping.md` | Per-spoke expected SERP format, engagement component, competitor gaps, Featured Snippet/PAA/KP targets |
| 4 | **Proactive Entitization Strategy** | `09-research/proactive-entitization-strategy.md` | 4-phase plan: Wikidata, GBP, JSON-LD schema, 10-platform profile checklist, seed entity association |
| 5 | **Momentum Shock Publishing** | `09-research/momentum-shock-publishing.md` | Drop-batch publishing: 12 pages in 5 days, 3 batches, crawl quota tactics |
| 6 | **Knowledge Graph API Audit** | `09-research/knowledge-graph-api-audit.md` | 10 core entities to audit, contextual bridges, EAV verification through KG API |

## Phase 3.6: Neurological Precision Layers (5 Layers, Completed)

These layers add algorithmic rigor — they ensure Google's NLP models interpret content exactly as intended. Build after connective tissue.

| # | Layer | File | Purpose |
|---|---|---|---|
| 7 | **Predicate & Intent Mapping** | `09-research/predicate-intent-mapping.md` | Maps exact verbs to search intent types (Learn: "grasp"/"understand", Earn: "maximize"/"negotiate", Solve: "fix"/"eliminate"). Per-spoke predicate assignment with density targets. |
| 8 | **Entity Disambiguation Plan** | `03-web-entity/entity-disambiguation-plan.md` | Prevents entity collision with other "Quan" entities. `sameAs` schema plan (TREC License, LinkedIn, HAR.com, Zillow). KG API ID verification. 3-identifier footer rule. |
| 9 | **Discourse Integration + Modality Matching** | Added to Rulebook (Rules 7-8) | Concept sequencing — every paragraph shares entity with prior. Modality matching — "should" queries get "should" answers. Banned topic jump pairs. |
| 10 | **Page Character Analysis** | Added to `cost-of-retrieval.md` | Per-spoke visual-semantic character: Comparison Table, Calculator, Timeline, Definition List, Map, Checklist, Flowchart. SERP-expected engagement component must match page layout. |
| 11 | **Groundedness Validation Protocol** | Added to `truth-range-consensus-mapping.md` | Hard truth ranges with specific numbers (Texas property tax ~1.80%, FHA 3.5% down for 580+ FICO). Pre-publish checklist. Consequences for violations (KBT collapse, YMYL penalty). Ground Truth Anchor field. |

## Full Architecture (38 Files)

After all phases: 38 markdown files, ~214 KB. All cross-referenced. Structure:

```
SEO-quann.homes/
├── 00-roadmap.md                                  # Master roadmap, all phases
├── MASTER-GAP-LIST.md                             # Combined gap list + project state
├── QUAN-CALL-AGENDA.md                            # 6-block interview agenda
├── 01-source-context/source-context.md
├── 02-central-entity/central-entity.md
├── 03-web-entity/
│   ├── web-entity.md
│   └── entity-disambiguation-plan.md              # NEW: Phase 3.6 Layer 8
├── 04-eav-triples/eav-triples.md
├── 05-query-templates/query-templates.md
├── 06-topical-map/
│   ├── topical-map.md                             # 3 pillars, ~12 spokes
│   ├── topical-borders.md
│   ├── information-gap.md                         # 15 zero-volume nodes
│   └── contextual-bridges.md
├── 07-content-briefs/
│   ├── content-briefs.md
│   ├── lexical-richness.md                        # 60+ Knowledge Domain Terms
│   └── cost-of-retrieval.md                       # Includes Page Character Analysis
├── 08-backlink-strategy/backlink-strategy.md
└── 09-research/
    ├── algorithmic-authorship-rulebook.md          # NEW: Phase 3.5 Layer 1 (+ Rules 7-8)
    ├── distributional-semantics.md                 # NEW: Phase 3.5 Layer 2
    ├── serp-feature-mapping.md                     # NEW: Phase 3.5 Layer 3
    ├── proactive-entitization-strategy.md          # NEW: Phase 3.5 Layer 4
    ├── momentum-shock-publishing.md                # NEW: Phase 3.5 Layer 5
    ├── knowledge-graph-api-audit.md                # NEW: Phase 3.5 Layer 6
    ├── predicate-intent-mapping.md                 # NEW: Phase 3.6 Layer 7
    ├── truth-range-consensus-mapping.md            # Includes Groundedness Protocol
    ├── knowledge-domain-terms-expert.md
    ├── functional-intent-discovery.md
    ├── semantic-distance-border-definition.md
    ├── historical-identity-resurrection.md
    ├── cost-of-retrieval-per-spoke.md
    ├── data-collection-setup.md
    ├── competitor-analysis-framework.md
    ├── web-entity-audit-framework.md
    ├── eav-triples-expansion-blueprint.md
    ├── existing-content-gap-analysis.md
    ├── methodology-phase2-reference.md
    └── consensus-baseline.md
```

## Central Entity Anchor Values

- Quan Nguyen, License #0774451, Walzel Properties, "The Quantum Team"
- Service areas: Katy, Houston, Austin, Dallas, Rio Grande Valley
- Phone: (832) 400-3152, Email: quan@thequantumteam.net
- Core CTA: "Schedule a Call" → consultation
- Domain: quann.homes (Framer-built; brokerage appears in images/logos — FOOTER TEXT IS STALE and says "REAL BROKERAGE" — do not trust footer text on Framer sites; always cross-check with visual inspection or user confirmation)
- **Central Entity Decontamination Rule [Rule: proactive-entitization-strategy.md, Phase 1]:** Before any content work, verify the Central Entity's brokerage field is consistent across all framework files. A single stale `REAL BROKERAGE` reference anywhere in the EAV triples, topical map, or content briefs will cascade a Knowledge Graph fracture to every published page. Run `grep -rl "REAL BROKERAGE\|Forever Realty" SEO-quann.homes/` and patch all hits.
- **Central Entity Decontamination Rule [Rule: proactive-entitization-strategy.md, Phase 1]:** Before any content work, verify the Central Entity's brokerage field is consistent across all framework files. A single stale `REAL BROKERAGE` reference anywhere in the EAV triples, topical map, or content briefs will cascade a Knowledge Graph fracture to every published page. Run `grep -rl "REAL BROKERAGE\|Forever Realty" SEO-quann.homes/` and patch all hits.

## Prerequisites (Complete Before Content Writing)

These 7 prerequisites must be satisfied before any content briefs are written. Progress tracked in `MASTER-GAP-LIST.md`. **The Lead Architect dictates when each prerequisite is met — do not ask the Domain Expert for permission to proceed.**

| # | Prerequisite | Category | Status | Skill/File |
|---|---|---|---|---|
| 1 | Quan Interview | A | ✅ COMPLETE (2026-05-24) | 5yr exp, EN+VI, ABR/GRI/C2EX/MRP/PSA, NAR/TAR/HAR/KatyChamber/AREAA, no awards, ALL FTHB spokes stay, seller/investor deferred |
| 2 | Market Data Collection | B | 🟡 PARTIAL | See `seo-market-data-collection` skill. 3/9 confirmed (price, rate, FHA limit), 6/9 estimated. Refresh schedule tracked in `market-data.md`. |
| 3 | Web Entity Discovery | C | ✅ COMPLETE (2026-05-24) | External profiles found: HAR.com, Realty.com, LinkedIn (2), Facebook. Brokerage corrected to **Walzel Properties** (image-based on quann.homes). ISSUE-029 logged for footer/image mismatch. See `seo-entity-discovery` skill. |
| 4 | Framer Access | D | ⏸️ SKIPPABLE | Deferred — JSON-LD can be prepped offline. Return when needed. |
| 5 | Knowledge Graph API Key | E | ⏸️ SKIPPABLE | Deferred — free tier, 10 queries needed. Return when topical map has stable centroids. |
| 6 | Technical SEO Prep | F | ❌ Not started | JSON-LD schema, fix navigation, boilerplate. Proceed without Framer — prep schema files manually. |
| 7 | Competitor Analysis | G | ❌ Not started | Manual session per `competitor-analysis-framework.md`. Schedule after Phase 1 foundational primitives are established. |

**Execution issues log:** `SEO-quann.homes/EXECUTION-ISSUES-LOG.md` — records all tool failures, data provenance, and recovery plans across sessions. Review before resuming any prerequisite work.

## Pitfalls

1. **Building pillars for services with zero content** — Alignment Audit is mandatory. Don't trust RAG's list of "services."
2. **Truth range violations** — Never claim Texas property taxes below 1.0%. Never present round-number prices without source. KBT collapse is algorithmic and severe.
3. **Modality mismatch** — Content that answers "Should I buy a home in Katy?" with purely factual, unmodalized prose fails to match query intent. Use "should"/"can" when the query is interrogative, but always ground in data.
4. **Central Entity Contamination (CRITICAL)** — Before ANY content work, verify the Central Entity's attributes are self-consistent across all framework files. A fractured central entity (contradictory brokerage, license, or NAP values) poisons all downstream pages. Run a Decontamination Sweep: grep every file for stale brokerage/entity values and correct to the canonical source. This is Phase 0 — it blocks all other work. [Rule: Koray Phase 1, Card #12 — Ontological Grounding: "A central entity with fractured attributes cannot serve as an anchor for topical inheritance."]
5. **Framework-first, not prerequisites-first** — The topical map EXISTS in the framework. Prerequisites (KG API key, Framer access, competitor analysis) are skippable — they support the map but don't block content brief scoping. Don't grind prerequisites when the map is already built.
4. **Asking the Domain Expert for methodology guidance** — The single highest-severity error. The Domain Expert hired you to BE the expert. Do NOT ask "how do I build the topical map," "what pages should we build," "do you want Phase 2 or Phase 3 next," or "how should I format this." You have 534 Koray rules — use them to determine every answer. The only valid question to the Domain Expert is a domain-fact question (e.g., "what is your current brokerage?"). Even operational questions like "do you have Framer credentials?" should be phrased as prescriptions ("You will need Framer credentials for this step."), not requests.
5. **Delivering expert methodology to a copywriter** — The copywriter receives plain-English instructions: page title, audience, 5 things to cover, internal links. NEVER give them predicate-intent mapping tables, NLI entailment protocols, or EAV triple matrices. Those are YOUR pre-publish validation tools, not their reading. If you find yourself writing "predicate enforcement" or "truth-range consensus" in a copywriter deliverable, delete it.
6. **Framer site brokerage detection** — On Framer-built sites, the footer text can be years behind the visual layer. Brokerage may only appear in image logos. Never trust text extraction alone — always visually inspect the site (or confirm with the owner) before anchoring the Central Entity to a brokerage value. This caused ISSUE-029: three wrong brokerages propagated before visual inspection caught it.
7. **Context compactor hallucinations** — The context compactor can fabricate descriptions of work that never occurred (e.g., inventing a "3-Vector Dependency Extraction Plan" mid-compaction). When you see a compaction summary claiming work you don't remember doing, verify against actual filesystem state. If it's fabricated, say so transparently — the Domain Expert values engineering integrity over saving face.
8. **Treating abandoned files as complete** — The 38-file architecture existed before you but was abandoned. Do not treat pre-existing files as "done" prerequisites. Verify content quality before building on top. If the brokerage is wrong, the topical map is ungrounded, and the content briefs are generic — start over from Source Context.
