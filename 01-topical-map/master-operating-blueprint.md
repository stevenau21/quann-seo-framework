# Master Operating Blueprint — Human Readable

**Platform:** SEO Topical Authority Framework v2.0  
**Current Client:** quann.homes (Quan Nguyen — Buyer's Agent, Walzel Properties, Katy TX)  
**Last Updated:** 2026-05-28  
**Machine-Readable:** master-operating-blueprint.json

---

## What This Document Is

This is the permanent operating system for this SEO platform. If you (human or AI) open this repository for the first time, this document tells you everything the system has learned, built, and enforces. It prevents amnesia across sessions, agents, and clients.

---

## The 5 Hard Rules

No agent may violate these. They override all default behavior.

### Rule 1: The Review Gate
**After every phase, stop and present the deliverables.** Do not auto-advance. The word "Proceed" from the human is the only key that unlocks the next phase.

### Rule 2: Autonomous Resource Allocation
**The agent silently determines what is ENGINE work and what is HUMAN work.** The human never defines the split. Engine tasks are algorithmic (Python, data, schemas). Human tasks are delivered as simple, actionable checklists with zero SEO jargon.

### Rule 3: Corpus Over Dictionary
**WordNet is banned.** It's a 1985 dictionary. It thinks "estate" means "feudal barony." Google's live index is the semantic corpus. Use SERP scraping and competitor content mining — never NLTK — for vocabulary extraction.

### Rule 4: Autonomous Seed Discovery
**Queries are auto-discovered, never hand-coded.** The Domain KG produces anchor entities, which combine with intent modifiers to generate seed queries. This must work for dentistry, personal injury, SaaS, or any vertical — without changing a line of code.

### Rule 5: Framer Site Rule
**Text is untrustworthy on Framer sites.** Brokerage information lives in images/logos, not footers. On amateur-built sites, the image layer is more current than the text layer. Always visually inspect, and when in doubt, ask the owner.

---

## What We've Built So Far

### Phase 0 — Prerequisites ✅
- Interviewed Quan (5 years experience, buyer-focused, Vietnamese/English bilingual)
- Gathered 10/10 market data points (Katy $340K, Houston $345K, etc.)
- Discovered 11 entity profiles across 7 platforms
- Corrected brokerage 3 times before finding the truth: Walzel Properties
- ISSUE-029 documents the cascade misidentification

### Phase 1 — Vocabulary & Linguistics ✅
- Built Autonomous Seed Query Generator (generates queries from Domain KG)
- Scraped 26 competitor domains across 5 auto-discovered queries
- Extracted 94 high-signal Texas terms (TSAHC, MUD, PID, TREC — things WordNet never knew)
- Produced Copywriter Manual and Texas Entity Glossary
- Created `corpus-driven-vocabulary-extraction` skill for reusability

### Phase 2 — Knowledge Graph Architecture ✅
- Generated JSON-LD schemas (Homepage, About, Article, LocalBusiness)
- Built sameAs manifest: 5 verified, 5 needs verification, 7 needs creation
- Discovered 4 contaminated profiles (wrong brokerages)
- Mapped conversion flywheel

### Phase 3 — Information Retrieval ✅
- Simulated PageRank for internal link distribution
- Built Boolean retrieval matrix
- Mapped RankBrain signals

### Phase 4 — Entity-Semantic Bridge ✅
- Built 37-node entity relationship graph with 94 semantic edges
- Ranked entities by salience (Quan = 1,250.8 — 78× the next entity)
- Constructed 6 contextual bridges tying entities across boundaries
- Delivered disambiguation matrix and information gap analysis

---

## Repository Map

| File | Purpose |
|---|---|
| `master-operating-blueprint.json` | Machine-readable rules — every agent loads this first |
| `phase-dependencies.json` | Topological DAG — the phase sequence |
| `EXECUTION-ISSUES-LOG.md` | 29 issues + 9 patterns — read this before starting anything |
| `MASTER-GAP-LIST.md` | Content gaps — what's missing |
| `02-central-entity/central-entity.md` | Who Quan is — canonical entity |
| `03-web-entity/web-entity.md` | External profile audit |
| `04-eav-triples/eav-triples.md` | Domain Knowledge Graph |
| `06-topical-map/phase1-vocabulary-bank.json` | 94 approved terms |
| `06-topical-map/phase2-schemas.json` | JSON-LD schemas |
| `06-topical-map/phase4-entity-bridge.json` | Entity graph + bridges |
| `07-content-briefs/phase1-copywriter-manual.md` | Writer rulebook |
| `07-content-briefs/texas-entity-glossary.md` | One-page term definitions |

---

## Key Decisions Log

1. **Brokerage is Walzel Properties.** Discovered after 3 wrong answers. Confirmed by owner.
2. **WordNet is banned for domain vocabulary.** Corpus-driven extraction is the standard.
3. **Seed queries are auto-generated, never hand-coded.** Pluggability requires this.
4. **Entity contamination is worse than missing profiles.** Fix wrong before creating new.
5. **DuckDuckGo is primary for multi-step searches.** Google CAPTCHA persists across sessions.
6. **Structural filters, never manual blacklists.** Regex on table syntax — not word lists.

---

## Next: Phase 5

Phase 5 (Technical SEO + International) awaits the Review Gate. 30 grounded rules.
