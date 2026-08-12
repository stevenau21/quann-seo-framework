---
name: seo-framework-execution
description: Execute the SEO Topical Authority Framework — an industry-agnostic pipeline from Domain KG to content briefs. Governs the 8-phase topological sequence, autonomous resource allocation (engine vs. human tasks), and the Review Gate that prevents auto-advancing. Load this BEFORE running any SEO task in a repository with a master-operating-blueprint.json.
category: seo
triggers:
  - "topical map"
  - "SEO framework"
  - "Koray framework"
  - "run Phase"
  - "content brief"
  - "entity bridge"
  - "topical authority"
  - "semantic SEO"
  - "quann.homes"
  - "SEO pipeline"
  - "execute Phase"
  - "dependency DAG"
---

# SEO Framework Execution

This skill governs HOW the Lead Architect (agent) executes the SEO Topical Authority Framework. It encodes the operational rules proven on the quann.homes deployment — and designed to be portable to any industry.

## Critical: Read the Blueprint First

Before executing ANY SEO task in a repository, check for `master-operating-blueprint.json` in the repository root. If it exists, read it to understand:
- Which phases are complete vs. pending
- What the canonical entity and Domain KG contain
- What issues and patterns were discovered in prior sessions
- The 5 hard constraints (see below)
- **The Meta-Cognitive Control Plane** (`meta_cognitive_control_plane`) — if present, Protocol 1 (Boot-Up Sequence) overrides the default sequential execution. The skill's quickstart steps (7-10) say "start Phase 0" — but if the Control Plane exists, step 8 says **"PRESENT THE BUSINESS PRIORITY PROMPT"** instead. The agent must ask the user what they need (Content Generation / Technical Audit / Entity Cleanup / Full Pipeline) and calculate a SUB-DAG — NOT blindly execute Phase 0→1→2→3. Phase 5 can be legally bypassed for Content Generation. Phase 7 is always deferred until content exists.

If the blueprint doesn't exist, offer to create it from the current state.

## The 6 Hard Constraints (+ Control Plane)

These rules override ALL default agent behavior for SEO framework tasks. No agent may violate them.

**Constraint 0 — Meta-Cognitive Control Plane (added 2026-05-26):** On ANY fresh start in a repository with a `master-operating-blueprint.json` that contains `meta_cognitive_control_plane`, the agent MUST NOT begin sequential phase execution. Instead: load the blueprint → read the Domain KG → present the Business Priority Prompt using clarify() → calculate the sub-DAG → execute only what the user needs. This constraint supersedes all other phase-ordering rules. The Control Plane's `protocol_1_boot_up_sequence` provides the exact 14-step bootstrap. The Control Plane's `protocol_2_evolution` governs paradigm shifts (new data sources triggering contradiction audits and confidence decay). The Control Plane's `protocol_3_output_delta` governs page-level rewrite directives after paradigm shifts.

### Rule 1: The Review Gate
**After every phase, STOP and present deliverables.** Output the human-readable summary and files into the chat. Wait for the user's explicit "Proceed" command before starting the next phase. NEVER auto-advance across multiple phases.

### Rule 2: Autonomous Resource Allocation
**The agent silently determines ENGINE vs. HUMAN task split.** Never ask the user to define the split or format. ENGINE tasks (algorithmic) are executed silently. HUMAN tasks are delivered as simple, actionable checklists with zero SEO jargon.

**Classification guide:**
- ENGINE: Python computation, data extraction, schema generation, graph construction, PageRank simulation, JSON-LD generation, SERP scraping, vocabulary extraction, dependency computation, cycle resolution
- HUMAN: Profile verification, brokerage updates, account creation (GBP, Wikidata, Zillow), domain expert vocabulary filtering, contextual bridge review, content brief approval

### Rule 3: Corpus Over Dictionary
**WordNet/NLTK is BANNED for domain vocabulary extraction.** WordNet is a 1985 lexical database. It returns "barony" for "estate" and "trafficker" for "seller." Google's live index IS the semantic corpus.

Use the corpus-driven pipeline: Domain KG → Autonomous Seed Query Generator → DuckDuckGo SERP scraping → competitor term extraction → expert filter → vocabulary bank.

### Rule 4: Autonomous Seed Discovery
**Queries are auto-discovered from the Domain KG, never hand-coded.** Use `get_anchor_entities()` → intent modifier combination → compound query generation. This must work identically for dentistry, personal injury, SaaS, or any vertical.

**Structural filtering only:** Use structural/regex parsing to exclude markdown table headers, dividers, and schema type names. Never hardcode a manual exclusion list — the filter must work for any domain.

### Rule 5: Framer Site Rule
**On Framer-built (or amateur-built) sites, text is untrustworthy.** Brokerage information often lives ONLY in images/logos. The footer can be stale. External profiles (HAR, Realty.com, LinkedIn) can be 2+ brokerages behind. Always visually inspect images, and when in doubt, ask the owner directly.

## Execution Checklist

Before starting any phase:

- [ ] Read master-operating-blueprint.json (or create it if missing)
- [ ] Read EXECUTION-ISSUES-LOG.md — learn from prior errors
- [ ] Load corpus-driven-vocabulary-extraction skill (for Phase 1/4 tasks)
- [ ] Classify the phase's tasks as ENGINE or HUMAN (silently — don't ask user)
- [ ] Execute all ENGINE tasks with execute_code + terminal
- [ ] Format all HUMAN tasks as simple action checklists
- [ ] Save phase output to phase-specific files (phase{N}-*.json, phase{N}-*-report.md)
- [ ] Update the master blueprint with new artifacts
- [ ] STOP — present deliverables in chat and wait for "Proceed"

## Anti-Patterns

- ❌ Executing Phases 2-3-4 in one go without stopping for review
- ❌ Asking the user "should I make this engine or human?" — you decide
- ❌ Using WordNet for vocabulary — it's banned
- ❌ Hardcoding "Katy TX home buyer" as a seed query — auto-discover from Domain KG
- ❌ Trusting footer text on Framer sites for brokerage information
- ❌ Using manual keyword blacklists for entity filtering — use structural regex
- ❌ Running Google searches for multi-step scraping — DuckDuckGo is primary
- ❌ Creating static audit reports instead of workflow checklists for human tasks
  - ❌ **Proceeding to a new phase using only blog extraction when richer course/transcript sources exist.** Blogs (e.g., holisticseo.digital) are high-level theory and framework declarations. Course transcripts (e.g., Koray Lectures) contain the actual step-by-step operational methodology — the Quarice Framework, content brief templates, 9-step topical map process, contextual vector/hierarchy/structure/connection system, question generation methodology, and information tree. Before executing any phase that touches methodology (Phases 1-4), query the transcript KG first. If the transcripts reveal deeper process detail that the blog extractions missed, pause and cross-reference before proceeding. The user will catch this — blogs are the WHAT, transcripts are the HOW.
  - ❌ **Running ad-hoc curl queries against LightRAG KGs to explore new data sources.** This creates a non-deterministic, non-reproducible pipeline. If we add data for a different client tomorrow, those manual queries break. Instead: run the deterministic `data_pipeline_auditor.py` script (see `knowledge-synthesis-architecture` skill references). The auditor uses a FIXED matrix of 10 structured queries, extracts structural patterns (regex/key-based, not LLM interpretation), computes the Semantic Delta against the 534-card flashcard baseline, and outputs deterministic patch files. Same queries every run → same results. The user will call this out immediately — ad-hoc querying is a systemic vulnerability, not a shortcut.
  - ❌ **Phase 5 scope creep into IT plumbing.** Technical SEO (robots.txt, sitemaps, page speed) is deferred maintenance — it doesn't tell the copywriter what to write. When the business priority is content production, Phase 5 can be explicitly bypassed in favor of Phase 6 (Topical Authority Assembly). The correct sequence is: 0→1→2→3→4→6→5→7. Phase 5 (Technical SEO) runs after the content map exists, not before. The user will call this out when the agent starts auditing server configs instead of producing content briefs.
  - ❌ **Building a topical map without Query Network Classification.** [Rule: Koray Lecture 1, lines 15-33] Before any topical map is drawn, the pipeline must: (1) extract the most frequent entity type from the Domain KG, (2) classify it broadly by proximity (geographic: continent→country→state→city; product: category→subcategory→brand; SaaS: industry→vertical→use-case), (3) build the broad-layer map borders first, THEN narrow to service attributes. This is a **missing data-artifact node** in the dependency DAG — it sits between Phase 4 (Entity-Semantic Bridge) and Phase 6 (Topical Authority Assembly) but is not modeled as a node. The 3-Vector engine currently models 12 framework nodes but zero data-artifact nodes. The fix is structural: extend `dependency_dag.py` to include data-artifact nodes (Query Network Classification, Contextual Vectors, Information Tree, URL Structure Derivation) so topological sort naturally enforces the broad→narrow descent. Without this, the engine produces correct framework order but the topical map skips the geographic/product-category layer entirely — a dentist in Phoenix would get `/root-canals` without the `Phoenix → Maricopa County → Scottsdale` geographic descent. See `references/query-network-classification.md` for the full specification.

## Corpus-Driven Vocabulary Extraction (Phase 1 Pipeline)

This is the operational detail behind Rules 3 and 4. When executing Phase 1 or Phase 4 of the framework, the vocabulary pipeline is:

1. **Auto-discover seed queries from the Domain KG.** Never hand-code. Use `get_anchor_entities()` from the Domain Knowledge Graph to extract high-signal entities (scored by frequency × attribute richness × connections), deconflict by entity type (brand, location, service, product), and combine with intent modifiers (guide, cost of, comparison, how to, near me) + compound patterns (location × service, product × location). Produces 10-12 seed queries.
2. **Scrape SERPs with Camofox + DuckDuckGo.** DuckDuckGo is primary; Google CAPTCHAs persist across sessions. Single-step only, 30s pause between queries. Extract organic results only (skip ads) — competitor domains, page titles, URL slugs, SERP snippets.
3. **Extract high-signal terms** from titles + snippets + slugs. Look for proper-noun capitalization, recurring noun phrases across multiple SERPs, terms in URL paths (intentional SEO targets), numeric thresholds (620+ credit score, 5% down payment).
4. **Domain expert filter** — mandatory. The engine cannot distinguish legal terms from illegal ones ("buyer rebate" vs. "TSAHC grant"). Expert approves/rejects/flags.
5. **Build three artifacts:** `vocabulary-bank.json` (engine), `copywriter-manual.md` (writer rulebook), `entity-glossary.md` (one-page definitions).

**Anti-patterns in the pipeline:**
- ❌ WordNet/NLTK for domain terms (returns "barony" for "estate", "trafficker" for "seller")
- ❌ Hand-coding seed queries (locks framework to one industry)
- ❌ Skipping expert filter
- ❌ Skipping the glossary (writers will misuse terms they don't understand)
- ❌ Manual blacklists like "remove 'Schema' from anchor list" — use structural regex
- ❌ Google for multi-step scraping — use DuckDuckGo

Full methodology + scoring formula + validation criteria: `references/corpus-driven-vocabulary-extraction.md`.

## Phase Reference

| Phase | Name | Layer | Status (quann.homes) |
|---|---|---|---|
| 0 | Prerequisites — Domain Grounding | -1 | ✅ Complete |
| 1 | Foundational Primitives — Linguistics & Data | 0 | ✅ Complete |
| 2 | Core SEO Concepts — KG & Conversion | 1 | ✅ Complete |
| 3 | Information Science — Retrieval & Indexing | 2 | ✅ Complete |
| 4 | Entity-Semantic Bridge | 3 | ✅ Complete |
| 5 | Execution Layer — Technical & International | 4 | 🔜 DEFERRED (business priority — content map > IT audit) |
| 6 | The Crown — Topical Authority Assembly | 5 | ✅ Complete (13-page topical map: root/seed/node, contextual vectors, content brief templates) |
| 7 | Meta-Reflection — Case Study Validation | 6 | ⏳ Pending |

## Related Skills

- `knowledge-synthesis-architecture` — LightRAG ingestion and query expansion for topical research
- _Corpus-driven vocabulary extraction was absorbed into this skill on 2026-06-01; see `references/corpus-driven-vocabulary-extraction.md` for the 5-step pipeline and seed-query generator methodology._

## Additional Resources

- `references/quann-homes-session-log.md` — Session-specific learnings from the quann.homes deployment: all 29 issues, 9 patterns, and key decisions that inform the rules above
