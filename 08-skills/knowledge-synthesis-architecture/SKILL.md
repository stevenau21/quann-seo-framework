---
name: knowledge-synthesis-architecture
description: Living architecture doc for the multi-source intelligence + domain KG content synthesis system. Covers Intelligence Layer (patents, official docs, research, AI announcements), Domain KG (industry-agnostic), AEO/GEO/SEO convergence, rule-driven content strategy, freshness tracking, source rotation, and novel emergence. Updated as research and planning evolve — this document IS the conversation artifact.
---

# Knowledge Synthesis Architecture

> **TRIGGER RULE:** When user mentions "rag", "RAG", "knowledge graph", "synthesis", "KG architecture", "client knowledge", "AEO", "GEO", "novel emergence", "patent", "intelligence layer", or "content strategy" — load this skill immediately. User confirms trigger word: **"rag"**.
>
> **LIVING DOCUMENT RULE:** After every substantive discussion about this architecture, update this skill with new insights, revised models, corrected assumptions, and emergent ideas. This document is not static — it's the accumulated intelligence of our planning conversations. Reference it before proposing anything about the RAG system.
>
> ⚠️ **MANDATORY PRE-ACTION PROTOCOL — READ BEFORE ANY ACTION OR PROPOSAL:**
>
> Before you propose a change, direction, next step, or build decision, verify these are loaded in context:
> 1. This SKILL.md (the architecture)
> 2. `references/PRD.md` (what and why we're building — scope, phases)
> 3. `references/architecture-review-systems-kernel-hats.md` (kernel strategy, decision criterion, risk register)
> 4. The **Conversation Evolution Log** below (what we've already discussed and decided)
> 5. Run `session_search` for recent discussions on this topic if the user references something you don't recognize
>
> **Failure mode this prevents:** Proposing changes that contradict the plan, skipping foundational layers, forgetting past decisions, redesigning without permission. Every time you skip this protocol and get corrected, you burn trust. The user should not have to remind you what's already documented.

---

## Lead Architect Operating Mode

When working with a domain expert (client), the agent operates as **Lead SEO Architect + Data Scientist**, not as a junior developer asking for step-by-step guidance. The domain expert supplies raw domain facts and business goals. The Lead Architect:

1. **Dictates the workflow** — uses the Koray dependency DAG to compute the mathematically correct next phase. Never asks the domain expert "what should we do next?" or "how should I format this?"
2. **Prescribes strategy** — uses the 534 grounded rules to calculate what pages/entities/content must exist for Topical Authority. Hands finalized instructions to the domain expert/copywriter.
3. **Autonomously allocates resources** — for every phase, internally splits work into ENGINE tasks (algorithmic — PageRank, schema generation, WordNet extraction, vocabulary banks) and HUMAN tasks (copywriter briefs, platform profile creation, visual verification). Never asks the domain expert to define who does what.
4. **Never asks permission on methodology** — the Koray framework IS the authority. The domain expert confirms domain facts, not SEO decisions.
5. **Transparent about failures** — when a tool hallucinates (context compactor, model output), admit it openly. Engineering integrity is valued more than saving face.

**The Rule of Citation:** Every strategic decision, every workflow step, every page prescribed MUST cite a specific extracted rule. Format: `[Rule: Framework Name, Card #ID]`. If no rule can be cited, do not propose it.

> Don't build around a source. Build around the signal. Sources come and go. The monitoring continues.

The goal is not to ingest a specific website or serve a chatbot. It's to build a system that:

1. **Continuously monitors** what AI companies, search engines, and the broader web ecosystem require from content
2. **Extracts structured rules** from those signals — patents, official docs, research, announcements, observed behavior
3. **Applies those rules** to any industry domain KG
4. **Produces content** that serves SEO, AEO, and GEO simultaneously
5. **Stays current** — when rules change, content gets flagged. When sources die, new ones replace them.

The competitive moat is not the data. It's the **intelligence pipeline that keeps the data current** and the **cross-referencing that surfaces what no single source contains**.

---

## The Two-Layer Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     INTELLIGENCE LAYER                             │
│           (Monitoring what AI/search engines want)                │
│                                                                    │
│  SIGNAL SOURCES (rotate over time, add/remove freely):            │
│                                                                    │
│  🔬 PATENTS — Predictive, pre-product intelligence                │
│     • Google patents (search ranking, NLP, entity extraction)     │
│     • Microsoft/OpenAI patents (generative retrieval, LLM search) │
│     • Meta/Anthropic/Apple patents (conversational AI, multimodal)│
│     • Pattern: patent filed → 12-24 months → product ships        │
│     • What to extract: what problem are they solving? How?        │
│       What assumptions about content quality are embedded?        │
│                                                                    │
│  📋 OFFICIAL DOCUMENTATION — Current, authoritative                │
│     • Google Search Central (guidelines, schema requirements)     │
│     • Schema.org updates (new types, properties, deprecations)    │
│     • Bing Webmaster Guidelines                                  │
│     • OpenAI/Anthropic model cards, system cards, usage policies  │
│     • Perplexity publisher guidelines                            │
│                                                                    │
│  📚 RESEARCH & PRACTITIONER SOURCES — Implementation specifics     │
│     • holisticseo.digital (entity-based SEO methodology)          │
│     • Search Engine Journal, Search Engine Land                  │
│     • Academic papers (SIGIR, WWW, ECIR, KDD — retrieval, ranking)│
│     • SEO practitioner case studies, experiments                  │
│     • AI engineer blogs on RAG/citation/retrieval techniques      │
│                                                                    │
│  📢 ANNOUNCEMENTS & CHANGELOGS — Breaking changes                  │
│     • Google algorithm updates, AI Overviews rollouts            │
│     • OpenAI/ChatGPT search feature launches                     │
│     • Perplexity API/product changes                             │
│     • Claude/Gemini search capability announcements              │
│                                                                    │
│  👁️ OBSERVED BEHAVIOR — Empirical, not theoretical                 │
│     • What actually gets cited in AI Overviews?                  │
│     • What schema markup correlates with citation?               │
│     • What content formats appear in featured snippets?          │
│     • Competitor citation tracking                               │
│     • A/B tests on your own content                              │
│                                                                    │
│  → EXTRACTS: Structured rules with confidence scores              │
│  → TRACKS: Changes over time (what's new, deprecated, contested)  │
│  → FLAGS: Contradictions between sources → review queue           │
│  → ROTATES: Sources added/removed without breaking the system     │
└───────────────────────────────┬──────────────────────────────────┘
                                │ rules govern
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                        DOMAIN KG                                   │
│           (Industry-agnostic — real estate today, anything later) │
│                                                                    │
│  • Entities: concepts, services, personas, questions, locations   │
│  • Relationships: typed, weighted, temporal                       │
│  • Attributes: definitions, facts, misconceptions, client voice   │
│  • Content inventory: what pages exist, what entities they cover  │
│  • Timestamps on EVERYTHING: created_at, last_updated,            │
│    last_validated — freshness is a first-class dimension           │
│  • Citation flags: has this entity ever been cited? By which      │
│    engine? On what date?                                          │
│                                                                    │
│  Structured by current rules from Intelligence Layer.             │
│  Re-structured when rules change.                                 │
│  Flagged for refresh when underlying data ages past threshold.    │
└───────────────────────────────┬──────────────────────────────────┘
                                │ feeds
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     CONTENT OUTPUT                                  │
│                                                                    │
│  Single-page multi-paradigm optimization:                          │
│  • SEO layer: depth, internal links, keyword coverage             │
│  • AEO layer: FAQ schema, concise definitions, extraction points  │
│  • GEO layer: entity relationships, comprehensive coverage        │
│                                                                    │
│  Format dictated by current Intelligence Layer rules.             │
│  Schema markup matches current Schema.org + engine requirements.  │
│  Refreshed when: rules change OR source data ages OR citations    │
│  drop OR client signals reveal new gaps.                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## The Rule Structure (What the Intelligence Layer Produces)

Every signal source gets processed into a standardized rule:

```json
{
  "rule_id": "aeo-faq-citation-2026",
  "category": "content_structure",
  "rule": "FAQPage schema markup increases AI Overview citation probability for definitional queries",
  "source": {
    "type": "official_documentation",
    "name": "Google Search Central",
    "url": "https://developers.google.com/search/docs/appearance/structured-data/faqpage",
    "date_published": "2025-11-15"
  },
  "confidence": "confirmed",
  "applies_to": ["AEO", "SEO"],
  "applies_to_content_types": ["definitional", "how-to", "procedural"],
  "contradicted_by": [],
  "deprecates": null,
  "deprecated_by": null,
  "added": "2026-05-13",
  "last_validated": "2026-05-13",
  "validation_method": "source_review",
  "notes": "Also corroborated by Perplexity publisher guidelines v2.1"
}
```

### Rule Confidence Levels

| Level | Meaning | Action |
|---|---|---|
| `confirmed` | Multiple authoritative sources agree | Apply to content |
| `probable` | One authoritative source + practitioner evidence | Apply with monitoring |
| `speculative` | Patent or research paper — not yet observed in production | Track, don't apply yet |
| `contested` | Sources disagree | Flag for human review |
| `deprecated` | Superseded by newer rule | Archive, stop applying |

---

## Patents as Predictive Intelligence

Patents are the earliest signal of what big companies intend to build. They don't guarantee a product, but they reveal the problem space the company is investing in.

### Why Patents Matter

- **18-24 month lead time** — patent filing to product launch gives you a window to prepare
- **Problem framing** — patents describe the problem they're trying to solve, which tells you what they think is broken about current search
- **Quality assumptions** — patents embed assumptions about what makes content "good" or "authoritative"
- **Competitive direction** — if Google patents a new entity extraction method and OpenAI patents a different one, you know they're diverging

### Patent Monitoring Strategy

| Company | What to Watch For |
|---|---|
| Google | Search ranking algorithms, entity extraction, passage indexing, multimodal retrieval, factuality scoring |
| Microsoft/OpenAI | Generative retrieval, LLM-based search, citation ranking, source authority scoring |
| Meta | Conversational AI search, social graph + search integration |
| Apple | On-device search, privacy-preserving ranking, Siri knowledge graph |
| Anthropic | Constitutional AI for search, source reliability, citation ethics |

### From Patent to Action

```
Patent filed                    → Extract problem statement + proposed solution
                                  → Classify as "speculative" rule
                                  → Set alert: re-check in 12 months

Product announcement            → Upgrade to "probable" rule
                                  → Begin content format experimentation

Product launch + observation    → Upgrade to "confirmed" or downgrade
                                  → Apply to all content production
```

---

## Source Rotation — Resilience Through Diversity

No single source is permanent. The Intelligence Layer must treat sources as replaceable.

### When a Source Dies

1. **Detect:** Source stops updating (no new content in 90 days) or goes offline
2. **Flag:** Rules derived from this source marked `source_at_risk`
3. **Find replacement:** Search for new sources covering the same knowledge domain
4. **Re-validate:** Cross-check rules against replacement source
5. **Transition:** Deprecate old source, onboard new one, update rule `source` fields

### Source Health Tracking

```json
{
  "source_id": "holisticseo-digital",
  "type": "practitioner_research",
  "status": "active",
  "last_published": "2026-05-10",
  "update_frequency": "weekly",
  "health_check": "sitemap_lastmod",
  "rules_produced": 47,
  "rules_active": 42,
  "rules_deprecated": 5,
  "replacement_candidates": ["searchenginejournal", "seo-theory-academic"]
}
```

---

## Freshness — The Missing Dimension

Freshness isn't a Phase 3 feature. It's structural.

### Every Entity Carries Time

```json
{
  "entity_id": "urn:re:stamp-duty",
  "timestamps": {
    "created": "2026-05-13T10:00:00Z",
    "last_updated": "2026-05-13T10:00:00Z",
    "last_validated": "2026-05-13T10:00:00Z",
    "last_cited_by_ai": null,
    "data_freshness_deadline": "2026-08-13T10:00:00Z"
  }
}
```

### Freshness Alerts

| Condition | Alert |
|---|---|
| Entity not validated in 90 days | ⚠️ "Stamp duty entity may be stale — rates change quarterly" |
| Rule upgraded from speculative to probable | 🔔 "New rule applies to 12 existing pages — refresh recommended" |
| Source published contradictory rule | 🚨 "Google says X, Perplexity says Y — content strategy conflict" |
| Client question frequency spiked | 📈 "BNPL questions up 300% this month — content gap widening" |

---

## Client Goal Parameterization — The Missing Dimension

The current architecture treats content optimization as uniform: "apply SEO + AEO + GEO to everything." But a client who wants local ranking in Katy has fundamentally different priorities than a SaaS company trying to get cited by ChatGPT. The pipeline must be parameterized by **client goal archetype**, not just by industry.

### Goal Archetypes

| Archetype | What They Actually Want | Priority Rules | Irrelevant Rules |
|---|---|---|---|
| **Local Dominance** | Rank in Maps, local pack, city queries | LocalBusiness schema, GMB, city entities, NAP consistency, review signals | AI citation structure, national keyword coverage |
| **AI Citation** | Appear in AI Overviews, ChatGPT, Perplexity | Entity relationships, FAQ schema, exhaustive definitions, citation-worthy structure, authoritativeness | Local pack ranking, maps optimization |
| **National SEO** | Rank nationally for competitive terms | Keyword coverage, backlinks, content depth, topical authority, pillar/spoke structure | LocalBusiness schema, GMB |
| **Brand Authority** | Control Knowledge Panel + brand SERP | KG reconciliation, Wikipedia/Wikidata, consistent entity attributes, Schema.org Person/Organization | Local ranking, conversion CTAs |
| **Conversion-First** | Leads, calls, form fills | Trust signals, social proof, clear CTAs, page speed, conversion-optimized structure | Knowledge Panel, AI citation |
| **Multi-Goal** | Multiple objectives from above | Weighted blend of all relevant archetypes | — |

### Goal-Weighted Gap Scoring

The Intelligence Layer produces universal rules, but those rules need **per-goal weight multipliers**. A rule like "FAQPage schema" is 10/10 for AI Citation but 3/10 for Local Dominance. "LocalBusiness schema" is 10/10 for Local Dominance but 0/10 for National SEO.

**Updated gap score formula:**

```
Gap = (Rule × Goal_Weight × 0.30) + (Client_Signal × 0.35) + (Competitive_Vacuum × 0.20) + (Freshness × 0.15)
```

Where `Goal_Weight` is a per-rule per-archetype multiplier (0.0–1.0). The same page analyzed under "Local Dominance" vs "AI Citation" produces different gaps, different priorities, and different writer briefs.

### Per-Goal A/B Testing Metrics

Different goals → different success metrics. A/B testing is parameterized by goal:

| Archetype | Primary Metric | Tool |
|---|---|---|
| Local Dominance | Maps ranking, local pack presence, GMB insights | GMB API, rank trackers |
| AI Citation | AI Overview presence, ChatGPT citation rate, Perplexity appearances | Citation monitor |
| National SEO | Organic SERP position, click-through, traffic | Google Search Console |
| Brand Authority | Knowledge Panel completeness, brand SERP control, Wikidata reconciliation | KG API, Kalicube |
| Conversion-First | Lead volume, form completion rate, call volume | CRM, analytics |

### Implementation

The goal archetype becomes a first-class parameter at project creation time. A real estate agent in Katy with goal "Local Dominance" gets a completely different brief priority list than the same agent with goal "AI Citation." The content brief generator accepts `--goal local|ai-citation|national|brand|conversion` and adjusts rule weights accordingly.

This also unlocks **multi-client scaling**: onboard 50 clients, each with their own goal profile, and the same system produces tailored gap reports + briefs for each.

---

The gap engine answers one question: **"What should I write next, and why?"**

### Gap Score Formula

```
Gap Score = (Rule Requirement × 0.30)        // "Google says you need FAQ schema on this topic"
          + (Client Signal × 0.35)           // "12 clients asked about this this month"
          + (Competitive Vacuum × 0.20)      // "No competitor covers this entity relationship"
          + (Freshness Decay × 0.15)         // "Existing page is 180 days stale"
```

### Gap Types

| Type | Detection | Example |
|---|---|---|
| **Rule gap** | Rule exists in Intelligence Layer but no content applies it | "Google requires FAQPage schema — 15 pages are missing it" |
| **Entity gap** | Entity exists in Domain KG but has no dedicated content | "Guarantor loan entity — no page explains it to buyers" |
| **Relationship gap** | Two entities co-occur in client transcripts but aren't connected in content | "Afterpay + borrowing power — clients ask, content doesn't connect them" |
| **Format gap** | Content exists but doesn't serve all three paradigms | "Stamp duty guide has SEO depth but no AEO extraction points" |
| **Temporal gap** | Content exists but is stale relative to current rules or market | "First home buyer guide references 2024 schemes that changed" |

---

## The Three Paradigms (Concurrent Optimization)

| Paradigm | Engine | What It Wants | Content Must Have |
|---|---|---|---|
| **SEO** | Crawl-based index (Google, Bing) | Depth, authority, relevance | Keyword coverage, internal links, topical completeness |
| **AEO** | Answer engines (AI Overviews, featured snippets, Perplexity) | Extractable, concise answers | FAQ schema, 40-60 word definitions, question→answer adjacency |
| **GEO** | LLM search (ChatGPT, Gemini, Claude) | Entity-rich synthesis material | Explicit relationships, comprehensive attributes, multi-source corroboration |

### Single-Page Multi-Paradigm Template

```
┌─────────────────────────────────────────┐
│  H1: Primary keyword (SEO)             │
├─────────────────────────────────────────┤
│  Quick Answer Box (AEO)                 │
│  → 40-60 word extractable definition    │
├─────────────────────────────────────────┤
│  FAQ Section with Schema Markup (AEO)   │
│  → Question in H2, answer immediately   │
├─────────────────────────────────────────┤
│  Comprehensive Guide Body (SEO)         │
│  → 1,500-3,000 words, internal links    │
├─────────────────────────────────────────┤
│  Entity Definitions + Relationships     │
│  → "X is different from Y because..."   │
│  → "X connects to Y via Z"             │
│  (GEO)                                  │
├─────────────────────────────────────────┤
│  Related Concepts (GEO)                 │
│  → Explicit links to all connected     │
│    entities with relationship context   │
├─────────────────────────────────────────┤
│  Schema Markup Layers                   │
│  → Article (SEO), FAQPage (AEO),        │
│    WebPage + about/mentions (GEO)       │
└─────────────────────────────────────────┘
```

---

## Dashboard Architecture

The UI telegraphs the architecture — it's a research workstation, not an admin panel.

```
┌─ Sidebar ──────────────────┬─ Main Panel ───────────────────────────┐
│                             │                                        │
│  📊 Overview                │  ← System health, rule counts,         │
│                             │    freshness alerts, recent changes    │
│                             │                                        │
│  ─────────────────          │                                        │
│                             │                                        │
│  🧠 Intelligence            │  ← Rule inventory, source status,      │
│     • Rules                 │    contradictions, validation queue    │
│     • Sources               │                                        │
│     • Patents (stub)        │                                        │
│                             │                                        │
│  ─────────────────          │                                        │
│                             │                                        │
│  🏠 Domain KG               │  ← Entity/relationship explorer,       │
│     (Real Estate)           │    content inventory, freshness map    │
│                             │                                        │
│  ─────────────────          │                                        │
│                             │                                        │
│  ✍️ Content                 │  ← Gap priority list, content briefs,  │
│     • Gaps                  │    client voice panel, template output │
│     • Writer View (stub)    │                                        │
│                             │                                        │
│  ─────────────────          │                                        │
│                             │                                        │
│  🗣️ Client Signals (stub)  │  ← Greyed out: "Coming — transcript    │
│                             │    ingestion, question mining,         │
│                             │    emotional signal detection"         │
│                             │                                        │
│  ─────────────────          │                                        │
│                             │                                        │
│  ⚙️ Configuration           │  ← Source management, rule thresholds, │
│                             │    freshness deadlines, API keys       │
│                             │                                        │
└─────────────────────────────┴────────────────────────────────────────┘
```

└─────────────────────────────┴────────────────────────────────────────┘
```

---

## The Architect Pipeline — From Collection to Novel Emergence

The endgame is not understanding the architects. It's becoming architects ourselves.

### The Full Pipeline

```
ARCHITECT COLLECTION → INDIVIDUAL EXTRACTION → CROSS-SYNTHESIS → WHITE SPACE ANALYSIS → OUR FRAMEWORKS → A/B TESTING → NOVEL EMERGENCE
```

Each phase feeds the next. A/B testing at the end isn't just verification — it's a first-class input into novel emergence. We test our synthesized frameworks against real content, measure what actually performs, and the results become new raw data that feeds back into the flywheel.

### Phase 1: Architect Collection
**Goal:** Every architect's complete public corpus.
- Blog posts, YouTube transcripts, Twitter threads, Reddit posts/comments, talks, podcasts, books, courses
- Cross-references: who they cite, who cites them, raw source breadcrumbs
- Output: Per-architect raw corpus (markdown + dedicated LightRAG graph)

### Phase 2: Individual Extraction
**Goal:** From each corpus, extract their operating system.
- Frameworks, mental models, ideology, methods, processes, signal hierarchy
- Unique perspectives — what makes THIS architect different from the others
- **Paradigm declaration** — each extraction carries `paradigm: seo | aeo | geo` as a first-class filter
- **Extraction independence** — extractions are buildable in any order, skippable, optional. No extraction depends on another.
- Output: Per-architect extraction doc + machine-readable framework JSON

#### Extraction Output Schema

Every architect extraction produces `frameworks.json` using this schema:

```json
{
  "architect": {
    "name": "Koray Tuğberk GÜBÜR",
    "paradigm": "seo",
    "domains": ["holisticseo.digital", "koraygubur.com"],
    "extraction_date": "2026-05-16",
    "total_docs_analyzed": 394
  },
  "frameworks": [
    {
      "id": "kg-topical-authority",
      "name": "Topical Authority",
      "type": "framework",
      "confidence": "core",
      "definition": "one-paragraph summary",
      "source_docs": ["doc-abc", "doc-def"],
      "first_appeared": "2023-06",
      "last_updated": "2025-11",
      "evolution": ["v1: broad concept", "v2: added semantic networks"],
      "depends_on": ["semantic-search"],
      "contradicts": [],
      "raw_sources_cited": ["US2019/0354602", "BERT paper"],
      "unique_position": true,
      "negative_space": ["No AEO/GEO coverage", "No local SEO"]
    }
  ],
  "mental_models": [...],
  "methods": [...],
  "signal_hierarchy": {"ranked": ["contextual vectors", "entity coverage", "topical depth", "backlinks"]},
  "breadcrumbs": {
    "patents": ["US2019/0354602 - Topic Layer"],
    "papers": ["BERT - Devlin et al 2019"],
    "api_docs": [],
    "official_docs": ["Google Search Central", "Schema.org"]
  },
  "negative_space": {
    "topics_avoided": ["Paid search", "Social media SEO"],
    "questions_never_answered": ["How to scale topical authority for 10K+ pages"],
    "contradictions_unresolved": ["Entity-first vs query-first content strategy"],
    "blind_spots": ["No empirical A/B data — all theory"]
  }
}
```

**Why this schema:** Downstream components query it directly. The gap detector filters `paradigm: seo` for SEO-only clients. The brief generator cross-references `breadcrumbs` across architects for contradiction detection. `negative_space` feeds the white-space phase without requiring another extraction pass.

### Phase 3: Cross-Synthesis
**Goal:** Compare ALL architects. Find structure across individuals.
- **Commonalities:** Convergent frameworks (multiple architects arrived at same conclusion independently = strongest signal)
- **Conflicts:** Where they disagree (debates, competing models, paradigm wars)
- **Blind spots:** What nobody addresses, what's assumed but unexamined
- Output: Unified framework map + contradiction matrix + gap analysis

### Phase 3.5: Flashcard Generation + Grounding
**Goal:** Explode each framework into atomic cards (concepts, methods, principles) and ground every card to a source paragraph via embedding similarity + LLM verification.

**Architecture:** 534 cards across 12 Koray Gubur SEO frameworks. Three-stage pipeline:
1. **LLM Tagging** — extract target_entity + action_directive per card (cloud API: deepseek-v4-flash)
2. **Embedding** — nomic-embed-text (local Ollama :11434), embed cards + source chunks
3. **Verification** — similarity search → top-k chunks → LLM verifies direct support (GROUNDED/UNVERIFIED)

**⚠️ CRITICAL FINDING: Direct-quote verification has a ~16% hard ceiling.** After extensive iteration (context injection, doc-scoping, hybrid retrieval tests), the maximum grounding rate is ~16-21%. Root cause: flashcards are **synthetic claims** distilled from frameworks — they're true of the framework but rarely appear verbatim in any single source paragraph. The 86/534 grounded cards happen to have near-verbatim source text. The other 448 pass semantic relevance (embedding finds related chunks) but fail strict direct-quote verification.

**What we tried (all capped at ~21%):**
- Bare embedding: 16.1% | +Doc-scoping only: 20.8% | +Context injection: 16.1%
- 96.7% of failures have NO source_span — embedding finds chunks, LLM correctly rejects (synthetic claim ≠ direct quote)
- Keyword-first retrieval would help marginally but doesn't solve the fundamental synthesis-vs-quotation gap

**Design implications for flashcard verification:**
- Accept 16-21% as direct-quote ceiling and redesign verification: ground frameworks (not individual cards), or accept "reasonably inferred" as valid grounding
- Sentence-level chunking might recover 5-15% more (claims like "Use canonical URLs" buried in 200-word chunks)
- Future extractions: expect this ceiling for ALL architects — it's a property of synthesis, not of this specific corpus
- Alternative: semantic entailment verification (LLM judges "does source imply claim?") instead of direct-quote matching

**Script:** `/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur/phase4_remediation.py`
**Pipeline:** Phase 3 JSON → tag cards → embed → scope to framework doc_ids → similarity search → LLM verify → output with source_spans
**Critical config:** Cloud API for chat (`https://ollama.com/v1/chat/completions` + Hermes API key from `/.hermes/.env`), local for embed (`http://192.168.4.148:11434/api/embed`, no auth). Chat models require cloud — local 0.24.0 enforces auth on `/api/chat`.

### Phase 4: White Space Analysis ⭐ (OUR NOVEL EMERGENCE ENGINE)
**Goal:** Identify territory NO architect has explored.

This is the asymmetry phase. Individual architects are deep in one paradigm, biased toward their frameworks, publishing but not systematically comparing. We sit at a vantage point none of them possess:
- Cross-paradigm (SEO + AEO + GEO simultaneously)
- All traditions synthesized
- No allegiance to any single framework
- Raw source overlay capability

**White space questions:**
1. What does NO ONE talk about?
2. Where do frameworks conflict without resolution?
3. What raw source data (patents, docs, papers) exists that no architect has incorporated?
4. What cross-paradigm patterns emerge that paradigm-specific architects miss?
5. Where are the seams between SEO/AEO/GEO that nobody bridges?
6. What would happen if we inverted a consensus rule and tested the opposite?

### Phase 5: Our Frameworks
**Goal:** Build from the white space.
- Proprietary frameworks, methods, processes — not derivative, but emergent from the super-position
- Our own ideology — a new lens on how discovery engines operate
- Novel signal hierarchies and atomic unit taxonomies
- This is where we stop being analysts and start being architects

### Phase 6: A/B Testing
**Goal:** Validate or falsify our frameworks against reality.
- Deploy synthesized frameworks against real content
- Test SEO vs AEO vs GEO approaches on same topic
- Measure citations, rankings, engagement
- Results feed back into pipeline — confirming, refuting, or refining

### Phase 7: Novel Emergence
**Goal:** The proprietary operating model.
- Our frameworks + validated performance data = something no competitor can replicate
- Each cycle of collection → synthesis → testing → emergence tightens the flywheel
- The moat is not the data — it's the unique synthesis pipeline that produced it

### The Meta-Architect Position

We're not competing with Koray or Volpini on their territory. We're building at a level above — the meta-architect position — where we can see what all of them see AND what none of them see. This is the structural competitive advantage, not a temporary one.

---

## Implementation Phases

### Phase 1 — Foundation (MVP)

**Ship this:**
- Intelligence Layer MVP: 2-3 initial sources configured, structured rule extraction
- Domain KG: real estate entities ingested (quann.homes sitemap)
- Gap detection: "what rules exist vs. what content covers them"
- Content inventory: what pages exist, what entities they serve
- Basic freshness tracking: timestamps on entities, 90-day alert threshold
- Config editor for sources and thresholds
- LightRAG WebUI link for graph exploration

**Stub (visible, non-functional):**
- Patent monitoring panel — shows description of what it will do
- Client Signals panel — shows description
- Content Writer View — shows description

### Phase 2 — Signals & Citations

- Patent ingestion pipeline (USPTO, Google Patents API)
- Client transcript ingestion via n8n webhook → Need Graph extraction
- Citation monitoring: "does quann.homes appear in AI Overviews? Perplexity?"
- Content gap scoring with client signal weight
- "Client Voice" panel: verbatim quotes surfaced to content writer

### Phase 3 — Autonomous Optimization

- Automated rule contradiction detection + review queue
- Source rotation automation (detect stale source → find replacement → re-validate)
- Content refresh pipeline: rule change → flag affected pages → queue for rewrite
- Competitive gap detection: "what entities do competitors cover that we don't?"

---

## Research Backlog

Prioritized research that needs primary validation before we commit architecture decisions.

> **Industry-agnostic framing:** The Intelligence Layer produces rules that apply to any vertical. Research questions below are framed cross-industry unless otherwise noted. Real estate is the first test domain, not the permanent scope. Every question that could be tested against real estate ALSO gets tested against health, finance, legal, and tech verticals to confirm industry-agnostic patterns.

### P0 — Architecture Gate (DO NOT BUILD until these are answered)

| # | Question | Why It's Critical | Method | Status |
|---|---|---|---|---|
| **P0-1** | Do AI Overviews / answer engines cite structured content *at all* across major industries? | If answer engines don't cite ANYONE'S content, then AEO/GEO optimization is built on vibes. Kills or validates the entire proposition. | Manual query testing across Google AI Overviews, Perplexity, ChatGPT Search for 5 industries × 20 queries each. | ✅ **VALIDATED — Yes, they cite. But Google self-preferencing accelerating (17.42% of AI Mode citations → Google.com, tripled in <1yr). Only 38% overlap top-10 organic ↔ AI citations. Perplexity is most transparent (always cites). See `references/research-round-1.md`** |
| **P0-2** | What content properties correlate with AI citation? (cross-industry) | Structural predictors determine what rules the Intelligence Layer should extract. | Audit of 100+ cited vs. non-cited pages across industries. | 🔶 **PARTIAL — Content length (2,300+), domain authority, structured headings confirmed positive. Entity density + relationship explicitness NOT directly measured. Only 11% of sites cited by BOTH ChatGPT AND Perplexity → per-platform rules needed, not universal rules. See `references/research-round-2.md`** |
| **P0-3** | What's the actual cadence of search/AI guideline changes? | Determines the Intelligence Layer's minimum polling frequency. | Google Search Central changelog + Wayback Machine diff + schema.org release history. | ✅ **VALIDATED — ~7 Google updates/year (3 core quarterly + spam + AI rollouts). Monthly polling is the floor. Schema.org slow (3 minor releases/year). See `references/research-round-1.md`** |
| **P0-4** | What validation methods are "tried and true" for SEO/GEO/AEO claims? | Without falsifiable methods, every rule has unknown reliability. | Literature review of published SEO experiments and methods. | ✅ **VALIDATED — Citation audits are fastest reliable method (7-30 day cycle). Controlled A/B is gold but slow (30-90 days). Competitor schema audits fast but correlational. See `references/research-round-1.md`** |
| **P0-5** | Do FAQ/HowTo/Article schema types still correlate with AI citation? (cross-industry) | If schema markup is dead for AI, don't build extraction rules for it. | Schema audit of AI-cited pages. Compare schema presence rate in cited vs. non-cited. | 🔶 **MIXED — Schema is necessary but NOT sufficient. Perplexity: Q&A adjacency matters more than JSON-LD markup. Google AIO: domain authority + content length predict better than schema alone. ChatGPT/Claude/Gemini: schema effect unmeasurable due to opaque citation. Schema rules should be per-platform, not universal. See `references/research-round-2.md`** |
| **P0-5** | Do FAQ/HowTo/Article schema types still correlate with AI citation? (cross-industry) | If schema markup is dead for AI, don't build extraction rules for it. | Schema audit of AI-cited pages. Compare schema presence rate in cited vs. non-cited. | ⏳ **PENDING — Requires dedicated citation audit. Mixed signals from existing studies. Perplexity cares about Q&A adjacency; Google AI Overviews signals unclear. Not yet independently validated.** |

### P1 — Build Dependencies (Answer before Phase 2)

| # | Question | Why It's Critical | Method | Status |
|---|---|---|---|---|
| **P1-1** | What's the per-source LLM extraction cost at scale? | Without this, we can't define financially sustainable source count. System grows until it's too expensive to run. Cost tracking must be built from day one. | Run extraction on 1 source, measure tokens, extrapolate to N sources at M frequency. Build cost model: tokens per rule, rules per source, sources per budget. | Not started |
| **P1-2** | How accurate is LightRAG entity extraction on domain content? | Garbage entities → garbage gaps → garbage recommendations. Entire pipeline rests on extraction quality. Must validate before scaling. | Manual audit of 50 extracted entities against source content. Score: precision, recall, relationship accuracy. Test across 2+ industries. | Not started |
| **P1-3** | What patent families are active in AI-powered search ranking? | Patents are our 12-24 month early warning system. Need to know what's being filed NOW by Google, Microsoft/OpenAI, Meta, Apple, Anthropic. | USPTO/Google Patents search. Query: "search ranking", "generative retrieval", "entity extraction", "citation ranking", "content quality scoring". Map active patent families to potential product directions. | Not started |
| **P1-4** | What entities and content types dominate search results across industries? | The Domain KG should be shaped by what search engines actually surface across verticals, not what we guess matters. Real estate test case. | SERP analysis for top 20 queries across 5 industries. Extract: entity types surfaced, content formats (guide, calculator, listicle, FAQ), schema types present. | Not started |

### P2 — Refinement (Non-blocking, improves quality)

| # | Question | Why It's Critical | Method | Status |
|---|---|---|---|---|
| **P2-1** | What's the citation half-life of content across industries? | Determines freshness thresholds. If content stays citable for 2 years in health but 3 months in tech, freshness rules must be industry-aware. | Track citation persistence over time. Sample: 100 cited pages, re-check at 3, 6, 12 months. Measure: still cited? same position? | Not started |
| **P2-2** | What's the actual citation rate difference between structured vs. unstructured content? | Empirical validation of our core assumption that entity-anchored, schema-structured content gets cited more. | Controlled A/B experiment: publish structured + unstructured versions of similar content. Track citation rates over 90 days. | Not started |
| **P2-3** | Who else is building in this space? (Adjacent possible analysis) | What's being built that we could integrate with instead of build? Avoids reinventing wheels. | Market scan of RAG/content-strategy/SEO-AI tools. Map competitors, open-source projects, adjacent startups. | Not started |
| **P2-4** | Do competitors in target verticals use entity-first content strategy? | Validates whether entity-first is a competitive advantage or table stakes. Start with real estate, expand. | Top 10 competitor content audit per vertical. Assess: entity coverage, schema usage, content structure, citation frequency. | Not started |

---

## System Dynamics — Dangerous Feedback Loops

### Loop 1: The Citation Lag Oscillator

```
Rule extracted → Content published → Google indexes (3-10 days) →
AI Overview considers it (7-30 days) → Citation appears (maybe) →
We detect citation → We upgrade rule confidence → We produce more content
```

**The problem:** 30-90 day minimum loop. During those 90 days, the Intelligence Layer may extract 15 new rules, 3 contradicting the original. Content writer optimizes for last quarter's signal. By the time feedback arrives, the target moved.

**Mitigation:** Citation feedback is for STRATEGIC validation only ("over the last year, FAQ-structured content gets cited 3x more than narrative"), not tactical optimization. Rule confidence upgrades based on citations require multi-quarter averaging, not single-event triggers.

### Loop 2: The Source Contradiction Explosion

```
Sources: 3 → Contradiction pairs: ~3 (manageable)
Sources: 10 → Contradiction pairs: ~45 (overwhelming)
Sources: 20 → Contradiction pairs: ~190 (impossible)
```

**The problem:** Contradictions grow quadratically with sources. Without deduplication, human reviewer drowns.

**Mitigation:** Contradiction CLUSTERING. "Sources A, B, and C all disagree with Source D about FAQ value" surfaces as one cluster with 3:1 consensus ratio, not three separate alerts. Clusters are sorted by consensus strength. Strong consensus (4:1+) = auto-resolve. Weak consensus (2:2) = human review.

### Loop 3: The Content Refresh Cascade

```
Rule changes → 50 pages flagged → Writer rewrites 50 pages →
Re-ingestion updates entities → Freshness resets →
Another rule changed → 30 more pages flagged → backlog grows
```

**The problem:** Cascading backlog generator. Without prioritization, produces an ever-growing queue no human can clear.

**Mitigation:** Refresh IMPACT SCORING. "This rule change affects 3 high-traffic pages" > "This rule change affects 50 low-traffic pages." Prioritize by traffic × entity centrality, not count.

### Loop 4: The Writer Rejection Loop

```
System: "Write about BNPL impact" → Writer: "Niche edge case, skip" →
Gap still exists → System re-recommends next cycle →
Writer ignores again → Gaps accumulate → Writer stops opening app
```

**The problem:** System recommendations without human override create noise that eventually drives users away.

**Mitigation:** Gap DISMISSAL WITH RATIONALE. Writer says "not relevant" and explains why. Dismissal goes to Intelligence Layer as an `observed_behavior` signal. After N dismissals of same rule type, rule confidence drops. Human judgment IS validation.

### Loop 5: The Confidence Inflation Loop

```
System extracts rule → Rule is 'probable' →
Content produced based on rule → Rule produces citations →
System: "Our rules work!" → Upgrades all rules →
Produces more content → More citations → More confidence
```

**The problem:** Success reinforces the rules that happen to be right NOW. Rules that are wrong get no signal — they just sit at `probable` or `speculative` forever, never tested, never falsified.

**Mitigation:** Rules need NEGATIVE VALIDATION too. "We've produced content following this rule for 6 months with zero citations" should trigger a confidence DOWNGRADE. The absence of evidence IS evidence of absence when enough time passes.

---

## Entropy & Degradation — What Breaks When Nobody's Watching

Systems degrade. The architecture must plan for neglect, not assume maintenance.

### Degradation Timeline

| Time Since Last Human Touch | What Degrades | Failure Mode |
|---|---|---|
| 1 week | Nothing visible | System appears healthy |
| 1 month | Freshness alerts accumulate | Alert fatigue. Writer ignores all alerts. |
| 3 months | Several sources stop publishing | Rules silently go stale. No error — just outdated intelligence. |
| 6 months | All Domain KG entities past freshness deadline | Gap detection still works but recommends optimizing for Q2 rules in Q4 market. |
| 12 months | Contradiction queue 200+ deep | Human can't clear it. Recommendations produced from contested rules. |
| 18 months | LLM extraction costs accumulated unnoticed | Significant token spend producing rules nobody acts on. |

### Confidence Auto-Decay (Circuit Breaker)

The silent killer is a system that produces bad recommendations confidently. The fix: rules lose confidence when neglected.

| Condition | Decay |
|---|---|
| Rule not validated in 90 days | `confirmed` → `probable` |
| Rule not validated in 180 days | `probable` → `speculative` |
| Rule at `speculative` for 365 days | Auto-archive. Remove from active inventory. |
| Source not published in 90 days | All rules from that source downgrade one tier |
| Source offline/dead | All rules from that source marked `source_dead`. Human must re-validate or deprecate. |

Decay is VISIBLE — the dashboard shows amber warnings before red alerts. The system telegraphs its own uncertainty.

### Graceful Degradation Modes

| Component Failure | Degraded Behavior |
|---|---|
| Intelligence Layer down | Rules frozen at last-known state. Domain KG still serves entities. Gap detection pauses. Content inventory + freshness alerts still work. |
| Domain KG down | Rules still extract + accumulate. Can't apply to content. Alert fires. |
| Extraction pipeline down | Existing rules visible. Gap detection on last-known state. Freshness alerts still fire. |
| Citation monitor down | Citation flags freeze. Rules don't auto-upgrade but also don't auto-decay from missing citation data (circuit breaker prevents confidence inflation). |
| Dashboard down | Backend still runs. Rules still extract. Scheduled freshness alerts still fire via cron/notification. |

No single component failure takes down the entire system. The dashboard failing should not stop intelligence gathering.

---

## Cost Model (Financial Sustainability)

Every intelligence source adds ongoing LLM inference cost. The architecture must include cost awareness.

### Cost Tracking Per Source

```json
{
  "source_id": "holisticseo-digital",
  "cost_tracking": {
    "monthly_token_estimate": 45000,
    "monthly_cost_estimate": "$0.12",
    "rules_produced_per_extraction": 3,
    "signal_to_cost_ratio": "25:1",
    "cost_threshold": "$1.00/month",
    "above_threshold": false
  }
}
```

### Source Onboarding Gate

Before adding a source, estimate:
1. How many rules will this source produce per extraction?
2. What's the token cost per extraction?
3. How frequently does it update?
4. Signal-to-cost ratio = rules per dollar?

Gate: Don't onboard if signal-to-cost ratio < 10:1 (10 rules per dollar spent). Review quarterly.

---

## Architectural Gaps — Acknowledged Limitations

### Gap 1: Non-Text Content Blindness

The architecture only ingests text. But AI Overviews increasingly cite images, videos, structured widgets. Our content strategy is text-only while citation ecosystem shifts multimodal.

**Mitigation:** Reserve space in entity model for `content_formats` array: `["text", "image", "video", "calculator", "comparison_table"]`. Gap detection can flag "entity has text coverage but no image coverage." Not implemented Phase 1. Schema reserved.

### Gap 2: Localized/Personalized Requirements

AI Overviews in Texas may cite different sources than California. ChatGPT personalizes by conversation history. Architecture assumes uniform requirements.

**Mitigation:** Reserve `locale`, `device_type`, `personalization_context` as optional entity attributes. Not used Phase 1. Schema reserved so migration isn't breaking.

### Gap 3: Schema Versioning & Migration

Entity schemas evolve. Adding `locale` to all entities should not be a breaking change.

**Mitigation:** Schema versions from day one (v1, v2, v3). Every entity carries `schema_version`. Rule extraction knows which version it expects. Migration scripts for v1→v2, v2→v3. No silent breaking changes.

---

## Kernel Run — quann.homes Stress Test (2026-05-14)

### Methodology

Kernel v2.1 reads LightRAG workspace files directly (`kv_store_full_entities.json`, `kv_store_full_relations.json`, `kv_store_doc_status.json`, `kv_store_full_docs.json`) and cross-references against the known sitemap URLs.

**Critical discovery:** The LightRAG server's `/documents/text` API stores `file_path: unknown_source` for all submitted docs — it does NOT map the URL field to `file_path`. Workaround: sort docs by `track_id` timestamp (extracted from `insert_YYYYMMDD_HHMMSS_*` format) to match ingest order against the sitemap.

### Results

**Contamination: CRITICAL** — 54 template-only entities (76% of template entities). Examples: `3D Rendering`, `Audemars Piguet`, `Framer`, `Dribbble`, `Figma`, `Apple`, `Awwwards`, `Branding`, `App Design`, `CSS Design Award`.

**Rule compliance: 48.6% (18/37 passed).** Blog posts pass depth/links/cities/buyer/contact rules but fail FAQ schema, Article schema, and Katy context. Homepage at 60%, about at 67%.

**23 gaps total (10 high, 13 medium):**
- No FAQ schema on any page (AEO dead)
- No Article schema on blog posts
- Home-tours missing FAQ + deep content
- All blog posts missing Katy localization
- No entity coverage for "Closing Costs", "Down Payment Assistance", "Home Inspection" on relevant pages

**Key insight:** The template contamination is real and severe. If queries went straight to the graph, `3D Rendering` and `App Design` would surface alongside real estate entities. The kernel successfully catches this — it's a validated stress test.

**Kernel script:** `/home/steve/lightrag-apps/quann-chat/kernel_v2.py`
**Report:** `/home/steve/lightrag-apps/knowledge-synthesis/gap_report.json`

---

## Content Brief Generator — Engineering Notes

### What Worked
1. **Standalone pipeline:** `content_brief_generator.py` loads gap_report.json + rules_inventory.json + entity_audit_report.json in one shot. No API calls to LightRAG needed.
2. **gemma4:31b-cloud produces solid first drafts.** For the out-of-state buyer guide: real FAQ answers (not placeholders), JSON-LD schema, 6-section guide outline, entity definitions with Katy-local context. ~200s for 12K char brief.
3. **Contamination filter automatic.** 50 CRITICAL Framer entities excluded from prompts — LLM never sees them.
4. **Missing entity inference** from core entity set + entity_coverage_gaps in gap report.
5. **Prompt template works:** Gap → contaminated → clean entities → failed rules → missing → structured output with JSON-LD requirement.

### Caveats
- gemma4 can be wordy (FAQ answers may run 250+ words)
- Schema blocks need validation (may miss `@id`)
- gemma4 fabricates plausible dates — always review
- Title length enforcement is prompt-only (61-65 char titles slip through)
- Single-model dependency — no fallback if gemma4 is down

### Pipeline
```
rules_inventory.json ─┐
gap_report.json ──────┤→ content_brief_generator.py ──(LLM)──► briefs/brief-*.md
entity_audit_report ──┘
```

### First Brief (2026-05-15)
**Target:** out-of-state-buyer-guide (31.6% compliance, 7 HIGH failures)
**Saved:** `/home/steve/lightrag-apps/knowledge-synthesis/briefs/brief-blog-out-of-state-buyer-guide-2026-05-15.md`
**Contents:** Metadata, AEO Quick Answer, 3 FAQs, 6-section outline, 16 entity definitions, 3 JSON-LD blocks

## Architect Extraction Pipeline — Engineering Notes

### Koray Gubur Extraction — Pass 1 (Top-K Sampling) → FAILED (2026-05-22)

**First approach:** 6-step sequential extraction using direct LightRAG queries + Ollama structuring. One query per step, truncated to 8,000 chars. Completed in 242 seconds.

**Output:** `frameworks.json` (15.3KB) — only 8 frameworks from 394 documents.

**Root cause: Top-k similarity is a sampling error, not an extraction method.** LightRAG's `/query` endpoint returns chunks by vector similarity. A single query "what frameworks exist?" only catches the most semantically dominant ones — everything below the top-k cutoff is invisible. 394 docs with 10,480 entities and 13,973 relations existed in the raw data, but the query only saw ~6 chunks.

**CRITICAL LESSON: NEVER use LightRAG /query for exhaustive extraction. Always process documents individually.** The raw data is in `kv_store_full_docs.json` — use it directly. See `architect-extraction-pipeline` skill for the corrected per-document approach.

| 2026-05-24 | **PHASE 5 COMPLETE — Epistemic Stratification & Dependency Graph.** Phase 5 built from Phase 3 (deepseek-v4-flash framework extractions) + Phase 4 (534 flashcards with embedding verification). **Epistemic stratification hardcoded: Tier 1 (144 GROUNDED computable rules) vs Tier 2 (390 UNVERIFIED heuristic context).** Tier 1 cards carry `source_span` and feed the automated Gap Score engine. Tier 2 cards omit `source_span` — they provide narrative context for content briefs but do NOT trigger automated gap audits. This is the absolute epistemic limit of extractive verification against abstractive synthesis — pushing higher would require relaxing verification standards and poison the system. **Dependency graph**: 12 frameworks, 126 typed edges (42 depends_on, 42 supports, 42 cross-membership). SEO Case Study Methodology is most central (depends on 7 frameworks). Python & Data-Driven SEO is most grounded (47.1%). Cross-membership edges leverage the 118 Phase 4 cards that span multiple frameworks. Outputs: `phase5_frameworks.json` (321KB, complete framework objects), `phase5_dependency_graph.html` (D3 interactive), `phase5_dependency_graph.mermaid`, `phase5_dependency_graph.json` (Cytoscape). Script: `phase5_graph.py`. The bifurcated ontology is structurally enforced — downstream components query `tier_1_rules` vs `tier_2_context` programmatically. | Phase 5 build |

**Corrected approach:** Process all 394 documents individually through Ollama (gemma4:31b-cloud). Each document gets its own extraction call → aggregate via frequency counting + co-occurrence tracking + deduplication. ETA: ~20-30 minutes.

**Data-science architecture:**
1. Mine entity graph from raw files first (10,480 entities, 13,973 relations)
2. Identify framework candidates via degree + mention frequency
3. Extract per-document with LLM, using candidates as hit list
4. Aggregate with Counter() → frequency sorting
5. Build co-occurrence matrix for D3 graph visualization

**Script:** `extract_per_doc.py` at `/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur/`

**Critical design decisions:**
- NO `.format()` on prompts containing JSON (curly brace collision)
- Direct string concatenation + `json.dumps()` for structure
- Checkpoint every 20 docs for safe resume
- Rate limit: 0.5s between docs
- Content truncated to 5,000 chars per doc for context window

**Reusability:** Pipeline is architect-agnostic. Swap LightRAG instance URL + architect name and run. Extraction prompts at `/home/steve/lightrag-apps/knowledge-synthesis/extractions/{architect}/extraction_prompts.py`. Main pipeline at `extract_{architect}.py`.

### Ollama API pattern (for extraction scripts):
```python
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"

def query_llm(prompt: str) -> dict:
    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }, timeout=300)
    return json.loads(resp.json()["choices"][0]["message"]["content"])
```

### LightRAG query pattern:
```python
def query_lightrag(query: str, mode: str = "mix") -> str:
    resp = requests.post(f"{LIGHTRAG_URL}/query", json={
        "query": query, "mode": mode, "only_context": True
    }, timeout=120)
    return resp.json()["data"]
```

---

## Master Workflow Derivation — Topological Sort from Phase 5 DAG

The 534 flashcards destroyed the sequential narrative. The master workflow is NOT manually written — it is **mathematically derived** from Phase 5's dependency graph:

1. **Phase 5** produces `phase5_frameworks.json` with 12 frameworks, each carrying `depends_on` and `cross_membership` edges
2. **Dependency extraction:** Framework-layer dependencies + card-level entity references + action-directive chaining (`define` → `extract` → `model` → `build` → `validate`)
3. **DAG construction:** Nodes = cards/frameworks, Edges = prerequisites
4. **Topological sort** produces the execution sequence — this IS the master workflow
5. No card executes before its dependencies complete. No framework builds before its prerequisites.

**Never manually design the workflow.** The dependency graph dictates it. Build the DAG, sort it, and that's the plan.

Track how this architecture evolved through our discussions. This is the audit trail.

| Date | Shift | Trigger |
|---|---|---|
| 2026-05-13 | Initial architecture: 3 KGs (SEO, RE, Client), cross-reference engine, AEO/GEO/SEO paradigms | Research synthesis |
| 2026-05-13 | Client KG redefined as Need Graph — strip WHO, keep WHAT. Entity = pain point, not person | Discussion on anonymity + content patterns |
| 2026-05-13 | **Major refactor:** Replaced 3-KG model with 2-layer model. Intelligence Layer (source-agnostic monitoring) + Domain KG (industry-agnostic). Patents added as predictive signal. Freshness elevated to structural requirement. Source rotation designed for resilience. Rule structure formalized | Discussion on source dependency, patent intelligence, market fluidity |
| 2026-05-13 | Research backlog reframed: industry-agnostic not real-estate-specific. 5 P0 gates defined. Cross-industry validation across health, finance, legal, tech, real estate | User correction: system is about SEO/AEO/GEO across ALL industries |
| 2026-05-13 | P0-1 + P0-3 + P0-4 validated via web research. AI engines DO cite (but Google self-preferencing at 17.42%, tripling). ~7 Google updates/year. Citation audits are the fastest validation method. | Research Round 1 |
| 2026-05-13 | P0-5 + P0-2 partially validated via Round 2. Schema is necessary but NOT sufficient — per-platform rules needed. Entity density correlation requires primary research (no published study exists). | Research Round 2 |
| 2026-05-13 | **Tech stack fully assessed.** 18 installed packages verified. 6 missing packages available on PyPI. GTX 1080 8GB sufficient for all models. Anti-stack rejected (no Docker, Redis, React, paid APIs). Verdict: Yes, we have what we need. | User request to validate stack |
| 2026-05-14 | **Hands layer revised.** User pushed back on playwright/crawl4ai. Upgraded to: playwright (simple, 80%), camoufox (anti-detect, 8K stars, MPL-2.0), browser-use (AI navigation, 93K stars, MIT). Firecrawl self-hosted REJECTED — anti-detection cloud-locked. User's proxy for IP rotation. | User recommendation: "browser-use, firecrawl, camofox" |
| 2026-05-14 | **Full architecture review completed.** Systems thinking (7 feedback loops, 47-97 day total latency, leverage points, emergence), Kernel Strategy (4-component irreducible core, Ship of Theseus replaceability analysis, minimum viable kernel defined), Six Thinking Hats (existential Google self-citation concern, alert fatigue as #1 risk, novel kernel as moat). Decision: build kernel only. Zero alerts Phase 1. Criterion: writer says "holy shit." Full review at `references/architecture-review-systems-kernel-hats.md`. | User request: "systems thinking, kernel strategy, 6 thinking hats" |
| 2026-05-14 | **Kernel v2.1 built and run on quann.homes.** 22 pages ingested via server API (MAX_GLEANING=2), 20/22 processed at runtime. Contamination stress test confirmed: **54 template-only entities** from 10 Framer portfolio pages (lightric-motors, positive-energy, xiong-wall, hideaway, louis-martin, califfo, froadmile, westbury, portfolio-dark-work, portfolio-dark-home). Real content audit: 48.6% rule compliance across 3 blog posts + homepage + about + home-tours. 23 gaps found (10 high, 13 medium). All blog posts fail FAQ schema, Article schema, Katy context. Entity coverage gaps: Buyer's Agent, Closing Costs, Down Payment Assistance missing from ALL pages. Kernel output: gap_report.json at `/home/steve/lightrag-apps/knowledge-synthesis/gap_report.json`. | Stress-test execution |
| 2026-05-14 | **Flywheel model identified.** The system is a self-reinforcing loop: writer consults → gets per-platform brief → creates content → content gets cited → citation data feeds back to Intelligence Layer → rules strengthen → next brief is sharper → better content → more citations. Each turn compounds: Turn 1 is weak (speculative rules, zero citations), Turn 10 is sharp (per-platform confirmed rules with citation data), Turn 50 is a moat (proprietary citation database + entity graph nobody can replicate). Critical safeguard: the flywheel can spin on a subset of rules and never test the rest — negative validation (zero citations = downgrade) prevents echo chamber. Minimum viable first turn: one methodology source + extracted rules + clean Domain KG + content brief → writer uses it. Ignition point: brief is better than what the writer would produce alone. | Flywheel discussion |
| 2026-05-14 | **Full operational stack + data model blueprints saved.** `references/blueprint.mermaid` — complete system architecture: People layer (Quan + Writer), Input Sources (quann.homes, SEO methodology, Search engines, Citation data), Infrastructure (Windows Ollama :11434 with 9 models, WSL2 systemd lightrag-quann-chat on :8011), Processing (ingest_via_api.py + kernel_v2.py + LightRAG v1.4.15), Storage (NetworkXStorage graph, NanoVectorDB, JsonKVStorage 10 files ~5MB), Synthesis & Output (PRD.md, gap_report.json, Content Briefs, Exploit Library), Flywheel feedback loop. `references/data-model.mermaid` — Entity-Relationship model across 6 layers (Entity, Relation, Document, Rule, Gap, Exploit) with cross-tier connections and contamination flagging. These are permanent operational references for all future build decisions and novel emergence discovery. | Blueprint + data model creation |
| 2026-05-15 | **Intelligence Layer rule inventory built.** `rule_extractor.py` pipeline fetches methodology sources → extracts structured rules via gemma4:31b-cloud → merges into `rules_inventory.json`. Initial inventory: 23 rules (18 from Google + Backlinko methodology, 5 domain-specific). Kernel v2.1 loads rules from this file live — no more hardcoded rules. New check types added: char_count_title, keyword_in_title_front, schema_present, header_hierarchy, keyword_in_first_100, entity_coverage. Manual-only checks (information_gain, mobile_responsive, etc.) marked `unverified` rather than false-failing. Kernel run with 23 rules: 87 total checks across 12 real pages → 33.3% compliance (down from 48.6% on 8 rules because stricter methodology). 35 gaps (33 high, 2 medium). Home-tours worst at 23.5%. Pipeline script: `/home/steve/lightrag-apps/quann-chat/rule_extractor.py`. Rules inventory: `/home/steve/lightrag-apps/knowledge-synthesis/rules_inventory.json`. Methodology sources saved: `/home/steve/lightrag-apps/knowledge-synthesis/methodology_*.txt`. | Rule inventory extraction |
| 2026-05-15 | **Entity Contamination Audit Engine v1.0 built.** Full LLM-powered audit of 381 LightRAG entities using gemma4:31b-cloud. Results: 50 CRITICAL (confirmed foreign contamination — design agencies, fake portfolio names, tech brands), 0 HIGH (heuristic), 2 MEDIUM (needs review — 3D Rendering, Twitter), 19 FALSE POSITIVES (flagged but confirmed legitimate — agent name, brokerage, TREC disclosures). Contamination source: 10 Framer template pages under /portfolio-dark-work/. **This is now a paid audit product** — delivers a client-facing markdown report with entity catalog, source attribution, SEO/AEO/GEO impact analysis, and step-by-step remediation guide. Engine at `/home/steve/lightrag-apps/quann-chat/entity_audit_engine.py`. Reports: `entity_audit_report.json` + `entity_audit_client_report.md`. Wired into kernel v2 pipeline. | Entity audit engine |
| 2026-05-15 | **Content Brief Generator built — first exploit produced.** `content_brief_generator.py` takes gap_report + rules_inventory + audit report, creates structured multi-paradigm brief. First target: out-of-state-buyer-guide (31.6% compliance, 7 HIGH failures). gemma4:31b-cloud generated complete brief in ~200s: title tag, meta description, AEO Quick Answer Box (60 words), 3 FAQ Q&A pairs (real answers, no placeholders), 6-section guide outline (2000-3000 words), 16 entity definitions in Katy-local context, 3 JSON-LD schema blocks (Article, FAQPage, WebPage). Contamination shield active: 50 Framer entities excluded. Pipeline: `content_brief_generator.py --url <url>` → `briefs/brief-{slug}-{date}.md`. This is the ignition point of the flywheel — rules → gaps → brief → writer → content → citations → feedback → stronger rules. | Content brief generator + first exploit |
| 2026-05-15 | **CRITICAL COURSE CORRECTION — Pipeline built BACKWARD (audit-first instead of topical-map-first).** Quan identified: existing pipeline is audit (existing pages → gaps → briefs), but correct workflow is: (1) Topical Map — what SHOULD exist from domain entities (pillars, spokes, centroids, borders), (2) Entity Coverage Matrix — EAV triples + query templates per spoke, (3) Gap Detection — map vs. reality ("what pages don't exist" not just "what's wrong"), (4) Content Briefs — per-paradigm SEO+AEO+GEO per spoke, (5) Citation Monitor → feedback. The `seo-topical-map` skill has the full 11-layer framework (38 files) but is NOT integrated. Topical map IS the unified foundation for SEO/AEO/GEO — defines pages (SEO), extraction points (AEO), entity relationships (GEO). Next priority: integrate topical map engine into kernel. Honest assessment: architecture says right thing, implementation doesn't follow it. Brief generator assumes pages exist — it's optimization, not strategy. Real product: "Here are 12 pages to write, in this order, covering these entities, linked this way." | Course correction — topical map first |
| 2026-05-14 | **Exploit Engine product identity crystallized.** System is an exploit factory with four synthesis operations: Contradiction Hunting (platforms disagree → dual-format content wins both), Gap Exploitation (invert common rules → test opposite), Pattern Recognition (citation data reveals hidden correlations), Cross-Domain Transfer (gaming SEO → real estate = first-mover advantage). Lifecycle: detect → hypothesize → test on one page → measure citations → validate/invalidate → confirmed exploit becomes moat, auto-applied to all content. PRD upgraded to v0.2.0 with exploit engine framing. Product is not a gap detector — it's an exploit engine where the Knowledge Layer (SEO methodology) is the INTERPRETER that turns platform rules into actionable exploitation strategies. | Exploit engine identity |
| 2026-05-15 | **NOVEL EMERGENCE #2: The Architect Model.** Foundation isn't the topical map — it's understanding how engines operate structurally. Method: find the "architects" for each paradigm (SEO/AEO/GEO) — the deepest practitioners who study raw source materials (patents, papers, API behavior, IR theory) and build frameworks from first principles. They don't interpret an existing rulebook — they synthesize raw inputs into something new. By tracing their breadcrumbs (what sources THEY cite), we get a direct path to raw inputs. holisticseo.digital is the proof-of-concept for SEO. Need equivalents for AEO and GEO. | Drawing board — architect method |
| 2026-05-15 | **NOVEL EMERGENCE #7: Automatic Goal Weight Derivation Engine.** The Goal_Weight multiplier is derived from four evidence streams blended by reliability: Patent/Technical Disclosure (×0.40, highest — they built it), Architect Consensus (×0.25, collective wisdom), Empirical A/B Test (×0.20, gold standard but slow), First-Principles Mapping (×0.15, instant but weakest). Formula: Weight = Patent×0.40 + Consensus×0.25 + Empirical×0.20 + Logical×0.15. Each component is 0-1. When evidence is missing, weight stays low and auto-decays. The derivation is automated: patent parser → LLM signal extraction, architect corpus → consensus miner, test DB → effect size normalization. Bootstrap with logical mapping only (all low confidence), then sharpen as real evidence accumulates. This IS novel emergence — nobody has built a cross-paradigm, evidence-weighted rule engine. The derivation methodology is proprietary. | Goal weight auto-derivation engine |\n| 2026-05-15 | **Architect Collection Phase 1 — Koray Gubur ingested.** 395 URLs from holisticseo.digital across 5 post-sitemaps ingested into dedicated LightRAG notebook `lightrag-koray-gubur` on port 8012. 0 errors during ingestion. Extraction in progress with gemma4:31b-cloud (fast model). Monitor cron active at 10-min cadence checking `host.docker.internal:11434`. **Key infrastructure discoveries:** (1) extraction pipeline failure when using slow reasoning models — gemma4 required, never deepseek-v4-pro for extraction. (2) WSL2 `localhost:11434` ≠ Ollama — monitors must check `host.docker.internal`. (3) systemd stops hang during active extraction — use SIGKILL pattern. (4) 9 failure modes catalogued in `references/ingestion-failure-catalog.md` with pre-flight checklist. Notebook naming convention: one LightRAG per architect (`lightrag-{architect-name}`) for clean extraction without cross-contamination. Per-architect isolation strategy: independent ingestion, extraction, processing — converge only at Cross-Synthesis phase. | Koray Gubur collection + infrastructure hardening | The system must be parameterized by client goal archetype, not just industry. Different clients have fundamentally different objectives: Local Dominance (maps, local pack, city queries), AI Citation (AI Overviews, ChatGPT, Perplexity), National SEO (keyword coverage, backlinks), Brand Authority (Knowledge Panel, brand SERP), Conversion-First (leads, form fills). Each goal weights rules differently — FAQPage schema is 10/10 for AI Citation but 3/10 for Local Dominance. LocalBusiness schema is 10/10 for Local Dominance but 0/10 for National SEO. The gap score formula becomes: Gap = (Rule × Goal_Weight × 0.30) + (Client_Signal × 0.35) + (Competitive_Vacuum × 0.20) + (Freshness × 0.15). This also parameterizes A/B testing — different goals have different success metrics (maps ranking vs AI citation vs organic SERP). A single piece of content analyzed under different goal archetypes produces different priorities and different writer briefs. | Client goals parametrize the pipeline |
| 2026-05-15 | **NOVEL EMERGENCE #5: We become architects, not just analysts.** Collection + individual extraction + cross-synthesis give us a vantage point NO single architect possesses: cross-paradigm view (SEO+AEO+GEO simultaneously), all traditions synthesized, no allegiance to any single framework. This creates white space — territory no architect has explored. White Space Analysis becomes a formal phase: what does NO ONE talk about? Where do frameworks conflict without resolution? What raw source data exists that no architect has incorporated? What cross-paradigm patterns emerge that paradigm-specific architects miss? We don't just study architects — we achieve a super-position that lets us build our own frameworks, our own ideology, our own novel emergence. A/B testing validates our frameworks against real performance, creating a proprietary operating model. This is the meta-architect position. | White space → our frameworks → novel emergence |
| 2026-05-15 | **THE ARCHITECT MAP BUILT.** Comprehensive research across all three paradigms. Identified 5 meta-architects spanning SEO+AEO+GEO (Volpini, Krum, Muller, Alderson, Kopp), 8+ deep SEO architects (Koray Gubur, Slawski legacy, David Harry, Dixon Jones, van Driel, Mike King, Dave Davies, Dawn Anderson), 8 AEO architects, 8 GEO architects (Aggie Yu founded the field). Key raw sources documented. Platform distribution: Twitter/X primary, YouTube for deep dives, Reddit for practitioner debate, academic venues for original research. TikTok not a primary platform. Full map at `references/architect-map.md`. Next: ingest meta-architect frameworks → trace breadcrumbs → synthesize cross-paradigm → build foundational operating model (Layer 0). | Architect map — all three paradigms |
| 2026-05-15 | **NOVEL EMERGENCE #2: The Lawyer Model.** The foundation isn't the topical map — it's understanding how engines operate structurally. Method: find the "lawyers" for each paradigm (SEO/AEO/GEO) — the deepest practitioners who know the law backward, cite raw sources (patents, research, official docs), and exploit grey areas. They depend on raw source data to build THEIR novel emergence, creating frameworks and processes. By tracing their breadcrumbs (what sources THEY cite), we get a direct path to the raw inputs. Synthesize ACROSS lawyers + raw sources to build a meta-framework that sits above any single expert. holisticseo.digital is the proof-of-concept for SEO. Need equivalents for AEO and GEO. This creates a self-reinforcing flywheel: experts → breadcrumbs → raw sources → synthesis → novel emergence → attracts more experts. **NOVEL EMERGENCE #3: Pipeline is backward.** We built audit-first (existing pages → gaps → briefs). Correct order: foundational framework (engine operating models) → intelligence layer (rules from lawyers + raw sources) → topical map (domain application) → gap detection → content briefs. Foundation not built yet. **NOVEL EMERGENCE #4: Contamination validates kernel thesis.** 54 Framer template entities (76%) silently poisoned the graph — no automated check would catch this. Entity contamination detection must be a first-class kernel function, not an afterthought. | Drawing board session — lawyer method + course correction |

---

## Rule Extraction Pipeline — Engineering Notes

### What Worked

1. **gemma4:31b-cloud via Ollama API** (`http://192.168.4.148:11434/api/generate`) — extracts 10-15 structured rules per source. Use `stream: false`. Response comes as `{"response": "..."}`. JSON array is typically wrapped in ```json fences — use `re.search(r'\[.*\]', text, re.DOTALL)` to extract.

2. **curl-based fetching** with text extraction: strip `<script>`, `<style>`, `<nav>`, then `<[^>]+>` → collapse whitespace. Truncate to 12,000 chars for LLM context window.

3. **Merge-by-ID strategy**: `rules_inventory.json` is a flat array. Dedup on `rule_id`. New entries get `added` timestamp. Updated entries keep original `added` but get `updated` timestamp.

4. **Confidence filtering in kernel**: `load_rules()` only returns `confirmed` + `probable` rules. `speculative` and `contested` rules stay in inventory but don't fire checks.

5. **Format compatibility**: Kernel v2.1 accepts both `check` (old format) and `check_method` (new format) via `rule.get("check") or rule.get("check_method", "")`. This means old hardcoded rules still work alongside inventory rules.

6. **Six manual-only checks** (information_gain, readability_natural_language, mobile_responsive, no_intrusive_interstitials, image_alt_present, sitemap_submitted, descriptive_url_slug, anchor_text_quality) marked `unverified` instead of false-failing. These require visual inspection or live browser access.

### What Didn't Work / Edge Cases

1. **holisticseo.digital** — homepage returns 200 but sitemap and most article URLs return 404. Site structure uses non-standard URL patterns. Backlinko + Google Search Central proved more reliable for initial extraction.

2. **Parallel fetch timeout** — fetching all sources in a single `execute_code` script hit the 300s wall. Use individual `terminal()` calls or the `rule_extractor.py --batch` command which processes sequentially with 1s delay.

3. **Pages with zero applicable rules** — legal pages (TREC, disclosure), blog_index, and policy pages have no matching `applies_to` entries in the inventory. Kernel correctly shows 0/0 checks (not 0% failure). This is correct behavior — methodology rules don't apply to legal boilerplate.

4. **Two unknown docs** at end of ingest order (`unknown_22`, `unknown_23`) — these are the re-ingested versions of stuck documents. They duplicate existing content. Kernel correctly flags them as `unknown` category.

5. **Dedup bypass still needed** — if content is re-ingested without a marker, LightRAG rejects as "duplicated". Append `<!-- reingest:uuid -->` to bypass.

### Rule Inventory File Format

```json
{
  "rule_id": "SEO-TITLE-LENGTH",
  "category": "metadata",
  "rule": "Title tag must be between 50-60 characters",
  "source_type": "practitioner_research",
  "source_name": "Backlinko On-Page SEO (2026)",
  "source_url": "https://backlinko.com/on-page-seo",
  "confidence": "confirmed",
  "applies_to": ["blog_post", "service", "homepage"],
  "check_method": "char_count_title",
  "priority": "high",
  "principle": "Titles outside 50-60 chars get rewritten by Google",
  "added": "2026-05-15T06:30:00Z",
  "updated": "2026-05-15T06:30:00Z"
}
```

### Adding a New Source

```bash
python3 rule_extractor.py --url https://new-seo-blog.com/methodology \
  --source "New SEO Blog" --type practitioner_research
```

Or add to `SOURCES` list in `rule_extractor.py` for batch processing.

| 2026-05-26 | **Meta-Cognitive Control Plane v1.0 installed in master-operating-blueprint.json.** Three self-governing protocols: (1) Priority-Aware Boot-Up & Sub-DAG Calculation — agent MUST present Business Priority Prompt before executing any phases; calculates sub-DAG to bypass non-blocking phases (e.g., Phase 5 bypassed for Content Generation). (2) Chronological Conflict Resolution & Paradigm Shift Protocol — contradiction audit with Jaccard overlap classification (CONFIRMATION/ENHANCEMENT/CONTRADICTION/NOVEL), confidence decay formula, paradigm shift detection at 40%+ contradiction rate. (3) Paradigm-Shift Page Audit & Rewrite Directive — crawls live site, computes compliance score per page against new paradigm, outputs COMPLIANT/MINOR/MAJOR/OBSOLETE classifications sorted by traffic×obsolescence. Quickstart updated: step 8 now says "PRESENT THE BUSINESS PRIORITY PROMPT" instead of "start Phase 0." `seo-framework-execution` skill patched to reference Control Plane as Constraint 0. Pipeline auditor saved as `scripts/data_pipeline_auditor.py`. | Control Plane installation + Phase 6 topical map delivery |

| 2026-05-26 | **CRITICAL ARCHITECTURAL DISCOVERY — dependency DAG is missing data-artifact nodes.** The `dependency_dag.py` engine models 12 framework→framework edges via 3 vectors (stratification, NLP overlap, external dependency co-occurrence) but models ZERO data-artifact nodes — intermediate data products that frameworks produce and consume. The specific gap: Koray Lecture 1 requires Query Network Classification ("find the most popular entity type → classify by proximity → broad-layer map borders → then narrow to attributes") as the translation layer between Entity-Semantic Bridge (Phase 4) and Topical Authority Assembly (Phase 6). Without this node, the topological sort produces correct framework order but the topical map skips the geographic/product-category layer entirely. The same gap exists for Contextual Vectors, Information Trees, and URL Structure Derivation — all are data artifacts that should be DAG nodes. **The fix is structural:** extend the DAG to include data-artifact nodes alongside framework nodes so topological sort natively enforces the broad→narrow descent for any client vertical. This is NOT a missing phase — it's a missing dependency edge type. The user identified this as "dependency resolution" — the engine already does framework ordering, it just needs to model the intermediate data products too. Koray prescribed the dependency order (Content Quality before Topical Authority) — the 3-Vector Engine is the assistant's systematization of that prescription, not a Koray-taught method. | DAG structural gap — missing data-artifact nodes |\n\n| 2026-05-25 | **Phase 1-3 EXECUTED on quann.homes.** Lead Architect mode formalized: Autonomous Resource Allocation, Phase Progression, Citation Requirement. **Phase 1:** 23 grounded rules from Koray Content Quality & Linguistics + Python/Data-Driven SEO → copywriter manual produced with WordNet vocabulary bank (8 predicate families, 76 approved terms, 4 banned categories). **Phase 2:** 24 grounded rules from Knowledge Graph & Structured Data + Conversion → 4 JSON-LD schemas generated, sameAs manifest (5 verified, 7 needed, 4 contaminated), 9-step human checklist, conversion flywheel mapped. Broaderage decontamination sweep: 20 files patched from REAL BROKERAGE → Walzel Properties. **Phase 3:** 7 grounded rules from SEO Information Retrieval → PageRank simulation (17 pages, 2 PR sinks identified), Boolean term matrix computed, RankBrain query signals mapped. **Key pitfall corrections:** Context compactor hallucination transparently admitted, dependency DAG engine built (`dependency_dag.py` — 12 frameworks, 47 weighted edges, 8 cycles resolved), Framer brokerage detection methodology (image-based, not text extraction) encoded as permanent rule. | Phase 1-3 execution |

## Collection Status (2026-05-26)

| Architect | Status | Sources | Docs | Notebooks | Port |
|---|---|---|---|---|---|
| **Koray Gubur** | ✅ Extracted | holisticseo.digital | 395 URLs → 394 docs | lightrag-koray-gubur | 8012 |
| **Koray Gubur** | ✅ Extracted | **Koray Course transcripts** | 89/89 (88 lectures + 1 guest) | lightrag-koray-lectures | 8014 |
| Cindy Krum | ⬜ Not started | mobilemoxie.com | — | — | — |
| Andrea Volpini | ⬜ Not started | wordlift.io | — | — | — |
| Britney Muller | ⬜ Not started | britneymuller.com | — | — | — |
| Jono Alderson | ⬜ Not started | jonoalderson.com | — | — | — |
| Aggie Yu | ⬜ Not started | arXiv/Princeton | — | — | — |
| ... | ⬜ | 25+ remaining | — | — | — |

**Key distinction:** Blogs (port 8012) are high-level framework declarations and theory — the WHAT. Transcripts (port 8014) are the step-by-step operational methodology — the HOW. The transcripts contain the Quarice Framework (contextual vector, hierarchy, structure, connection), the complete content brief creation process, the 9-step topical map methodology, question generation from internal link targets, the root/seed/node architecture with PageRank distribution, contextual bridges and borders, information tree construction, and seconds modeling. These are NOT captured in the blog extractions. Before executing any SEO framework phase that touches methodology, cross-reference both KGs.

## Operational Playbook — Per-Architect Collection

**Naming convention:** `lightrag-{architect-name}` notebook on port range 8012+. One workspace per architect in `/home/steve/lightrag-apps/{architect-name}/`.

**Step 1 — Sitemap discovery:**
```bash
curl -sL https://{domain}/robots.txt | grep -i sitemap
curl -sL https://{domain}/sitemap_index.xml  # WordPress
# Check ALL domains — some may be private (e.g., koraygubur.com was locked)
```

**Step 2 — Notebook setup:**
```bash
cp -r /home/steve/lightrag-apps/koray-gubur /home/steve/lightrag-apps/{name}
mkdir -p /tmp/lightrag-ui-envs/{name}
# Copy .env, update WORKING_DIR path
# Copy systemd service, edit: Description, WorkingDirectory, port
# Add override: WEBUI_TITLE + MAX_GLEANING=0
sudo chown -R steve:steve /tmp/lightrag-ui-envs/{name}
```

**Step 3 — Batch ingest** (template: `koray-gubur/batch_ingest_koray.py`):
- BATCH_SIZE=5, wait for processing between batches (~2 min each)
- WSL2 TCP keepalive required: `net.ipv4.tcp_keepalive_time=10`
- ~2.5 hours for ~400 pages

**Step 4 — Monitor:**
```bash
cronjob(action='create', name='{Name} Monitor', schedule='*/10 * * * *', repeat=18,
  prompt='Check backend health + doc status. Report pending/processing/processed/failed.')
```
**IMPORTANT:** Monitor MUST check `host.docker.internal:11434` not `localhost:11434` — Ollama runs on Windows host, not WSL. Localhost inside WSL does not have Ollama.

**⚠️ CRITICAL — Extraction Model Rule:**
- LightRAG entity extraction: ALWAYS use a fast model (gemma4:31b-cloud). NEVER use deep reasoning models (deepseek-v4-pro) for extraction — they take 60-120s per chunk, trigger WSL2 TCP timeouts, and cause batch failures.
- Deep reasoning models (deepseek-v4-pro) are for queries/reasoning/analysis only, not extraction.
- This rule is documented as failure F1 in `references/ingestion-failure-catalog.md` (9 failure modes catalogued). Use the pre-flight checklist before ANY architect ingestion to catch all 9 failure modes BEFORE they become failures.

**Pitfalls learned:**
- Systemd `stop` hangs during extraction — force kill then reset-failed
- Rename mid-extraction: stop → kill → rename dir → copy env → new service → `chown steve:steve` → start
- WordPress sitemap_index estimates may differ from actual (395 not 821)
- Skip low-signal pages: `/author/`, category indexes — only substantive articles`

## Current Rule Inventory Stats (2026-05-15)

| Category | Count | Source |
|---|---|---|
| metadata | 3 | Backlinko |
| url_structure | 1 | Google |
| schema | 3 | Google + Backlinko |
| linking | 2 | Google + Backlinko |
| content_structure | 2 | Backlinko |
| content_depth | 1 | Backlinko |
| content_quality | 2 | Google + Backlinko |
| mobile | 1 | Google |
| ux | 1 | Google |
| images | 1 | Google |
| technical | 1 | Google |
| entity_coverage | 2 | Domain-specific |
| positioning | 1 | Domain-specific |
| conversion | 1 | Domain-specific |
| local_seo | 1 | Domain-specific |
| **Total** | **23** | **18 methodology + 5 domain** |

1. **Build around the signal, not the source.** Sources die. Monitoring continues.
2. **Corpus over dictionary.** Vocabulary extraction uses live Google SERP corpus (competitor content + PAA mining), never WordNet or lexical databases. WordNet is a 1985 dictionary — it returns feudal terms (barony, feoff) for real estate queries. Live corpus returns actual search-ecosystem terms (MUD, PID, TSAHC, Homestead Exemption). The methodology is corpus-driven extraction (Cards #8, #12, #14 from Koray's Python & Data-Driven SEO): mine competitor domains for term frequency → extract Google PAA/Related Searches → frequency-weighted output → domain expert filter. This is industry-agnostic: swap the Domain KG and the queries auto-generate.
3. **Autonomous seed query generation.** Never handcraft queries. The engine queries the Domain KG's `get_anchor_entities()` to pull top 3-5 high-signal entities, combines them with intent modifiers (informational/commercial/local/transactional), and produces compound queries (location×service, product×location). Structural markdown parsing filters table headers and dividers automatically. This makes the pipeline pluggable for any industry.
4. **Entity is the atomic unit** across SEO, AEO, and GEO. Not keywords, not questions — entities and their relationships.
3. **Freshness is structural, not aspirational.** Every entity, rule, and content page carries timestamps. Staleness triggers alerts.
4. **Patents predict. Documentation confirms. Observation validates.** Three tiers of signal maturity.
5. **Client transcripts are the highest-signal input.** They reveal exact language, misconceptions, and emotional context that no SEO tool captures.
6. **Novel emergence is the moat.** Content from cross-referencing your unique intelligence + domain data cannot be replicated.
7. **Single-page multi-paradigm optimization.** One page, structured for all three engines simultaneously.
8. **The Intelligence Layer is the product.** The chat and dashboard are interfaces. The rules engine IS what you're building.
9. **Sources must contradict each other.** That's a feature — contradictions surface where the industry is unsettled. Surfacing them is intelligence.
10. **Domain agnostic.** Real estate today. Any industry tomorrow. The architecture doesn't change.

---

## RAG Cron Jobs — Removed

All RAG-related cron jobs removed on 2026-05-13:
- `SEO Daily Ingestion` (097454bcc640)
- `Pipeline Auto-Recovery (30min)` (0d49b0500ed7)
- `rag-health-monitor` (8d40280f8080)
- `quann-chat Daily Ingestion` (dc7353a6793c)
- `SEO Pipeline Monitor (10min)` (1a0d7fb202c4)

Only remaining crons: `Daily Morning Briefing` (1be80a69fbba), `Daily Service Health Summary` (3b70b2d9ec08).
