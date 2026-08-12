# Product Requirements Document — Knowledge Synthesis Engine

**Version:** 0.2.0 (Exploit Engine Framing)
**Date:** 2026-05-14
**Status:** Draft — undergoing pressure testing and refinement
**Owner:** Quan Nguyen + Hermes (strategist/architect)

> This PRD is a living document. It evolves alongside the architecture skill. Nothing in here represents a commitment to build — it represents the current best understanding of what should be built and why. Every section is open to challenge.

---

## 1. Product Vision

A system that tells you what AI-powered search engines want from content *right now*, and whether your website delivers it.

Not a chatbot. Not a content calendar. Not an SEO tool. **An intelligence pipeline that monitors the evolving requirements of search engines and AI companies, structures your domain knowledge accordingly, and surfaces exactly what content you need to create to be the answer — everywhere.**

---

## 2. Problem Statement

### 2.1 The World Has Changed

Search is no longer one thing. A single query can hit:
- Traditional search (Google blue links)
- Answer engines (AI Overviews, featured snippets, Perplexity)
- Generative engines (ChatGPT Search, Gemini, Claude)

Each has different requirements. Each changes its requirements regularly. Most content creators are optimizing for one paradigm and invisible to the other two.

### 2.2 The Current Workflow Is Broken

Today, a content creator who wants to rank everywhere must:
1. Monitor Google Search Central for guideline changes
2. Monitor Schema.org for new/deprecated types
3. Read SEO practitioner blogs to stay current
4. Watch AI company announcements for new search features
5. Manually audit their own content against all of the above
6. Guess what to write next based on keyword tools that don't account for AI search

This doesn't scale. It's reactive. It depends on sources that may stop publishing.

### 2.3 The Gap

No tool exists that:
- Aggregates requirements from ALL signal sources (patents, docs, research, announcements, observed behavior)
- Structures them as machine-readable rules with confidence scores
- Applies them to a domain-specific knowledge graph
- Detects where your content falls short
- Alerts you when the rules change and your content needs refreshing
- Works for any industry

---

## 3. Target Users

### Primary: Content Strategist / Writer

**What they need:**
- "What should I write next and why?"
- "Does my existing content meet current AI search requirements?"
- "What changed this week that affects my content?"
- "What are actual humans asking about that we haven't covered?"
- "How do I structure this page so it works everywhere?"

**What they don't need:**
- Graph explorers
- Entity extraction debugging
- Raw patent dumps
- Technical infrastructure views

### Secondary: SEO Strategist / Agency Owner

**What they need:**
- "What rules are we tracking? What's the confidence level?"
- "Are we being cited? By which engines? For which queries?"
- "How does our entity coverage compare to competitors?"
- "What sources are we monitoring? Are any at risk?"

### Tertiary: System Administrator

**What they need:**
- Service health
- Ingestion status
- Error logs
- Configuration management

---

## 4. Core Product Principles

| # | Principle | What It Means |
|---|---|---|
| P1 | **Don't build. Surface.** | The system doesn't write content. It tells you what to write and why. |
| P2 | **Confidence over completeness.** | A rule with `confidence: speculative` is surfaced but not applied. Don't optimize for unproven signals. |
| P3 | **Source agnostic.** | holisticseo.digital is a source, not the source. When it stops publishing, the system survives. |
| P4 | **Freshness is a feature, not a chore.** | Every data point carries a timestamp. Staleness triggers alerts automatically. The system nags you. |
| P5 | **Domain agnostic.** | Real estate today. Any vertical tomorrow. The architecture doesn't know what industry it's serving. |
| P6 | **Contradictions are intelligence.** | When Google says X and Perplexity says Y, that's not a bug — it's the most valuable signal the system produces. |
| P7 | **No black boxes.** | Every rule links to its source. Every gap links to the rules that detected it. Every content suggestion has a traceable rationale. |

---

## 5. Scope — What We're Building

### 5.1 Phase 1 — Foundation (MVP)

| Capability | Description | Success Criterion |
|---|---|---|
| **Intelligence Layer MVP** | 2-3 sources configured. System pulls, processes, and stores structured rules with confidence scores. | Can add a source URL and see extracted rules within 5 minutes |
| **Rule Inventory** | View all rules. Filter by confidence, source, category, paradigm. See which are new/changed/contested. | Can answer: "what does Google currently require for FAQ content?" |
| **Domain KG** | Real estate entities ingested from quann.homes sitemap. Entity-relationship graph with timestamps. | Can answer: "what entities exist in our domain and when were they last updated?" |
| **Content Inventory** | Map of existing website pages to the entities they cover. | Can answer: "which pages cover the 'stamp duty' entity?" |
| **Gap Detection** | Cross-reference rules × content inventory. Surface: rule gaps, entity gaps, format gaps, temporal gaps. | Can answer: "what content are we missing that the rules say we need?" |
| **Freshness Alerts** | Entity/content not validated in 90 days → warning. Rule upgraded → notification. Source contradicted → alert. | System notifies user of staleness without manual checking |
| **Configuration** | UI for managing sources, rule thresholds, freshness deadlines, exclude patterns. | Non-technical user can add a source and adjust alert thresholds |
| **Stubbed Panels** | Patent monitoring, Client Signals, Content Writer View — visible as greyed-out cards with descriptions. | User understands the roadmap without reading documentation |

### 5.2 Explicitly Out of Scope for Phase 1

| What | Why Not Yet |
|---|---|
| Automated content generation / writing | P1: "Don't build. Surface." The system identifies gaps. Humans write. |
| Chatbot interface | Secondary to gap detection. Chat is a query interface, not the product. |
| Client transcript ingestion | Requires n8n pipeline + extraction models. Phase 2. |
| Patent ingestion pipeline | Requires USPTO API integration + specialized extraction. Phase 2. |
| Competitive gap detection | Requires competitor content ingestion + entity comparison. Phase 3. |
| Automated source rotation | Requires source health monitoring + replacement discovery. Phase 3. |
| Citation monitoring (automated) | Requires query automation + result parsing across engines. Phase 2. |
| Multi-domain support | One domain first. Prove the model. Then generalize. |

### 5.3 Phase 2 — Signals & Citations (Planned, Not Committed)

- Patent ingestion pipeline
- Client transcript → Need Graph pipeline via n8n
- Citation monitoring dashboard
- Content gap scoring with client signal weight
- Client Voice panel (verbatim quotes)

### 5.4 Phase 3 — Autonomous Optimization (Planned, Not Committed)

- Automated rule contradiction detection + review queue
- Source rotation automation
- Content refresh pipeline (rule change → affected pages → rewrite queue)
- Competitive gap detection

---

## 6. Anti-Scope — What We Will NOT Build

| Anti-Feature | Rationale |
|---|---|
| Content generation / AI writing | Violates P1. The system surfaces opportunities. Humans create. |
| Keyword research tool | Solved problem. Integrate with existing tools if needed. |
| Rank tracking | Solved problem. Not our differentiator. |
| Backlink analysis | Solved problem. Not our differentiator. |
| Social media scheduling | Out of scope entirely. |
| Multi-tenant SaaS | Premature. Prove single-tenant first. |
| Mobile app | Web-first. Mobile responsive, not mobile native. |

---

## 7. Success Metrics

### 7.1 Phase 1 Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Source → Rule extraction time | < 5 minutes after source added | Timestamp delta |
| Gap detection accuracy | 0 false positives on rule gaps (rule exists + content exists = no gap reported) | Manual audit of 10 gap reports |
| Freshness alert precision | 0 alerts for entities validated within 90 days | Alert audit log |
| Configuration self-service | Non-technical user can add source + change thresholds without documentation | Usability test |
| System uptime | 99% during business hours | Health check monitoring |

### 7.2 Long-Term Success Indicators

- Pages created from gap detection rank in AI Overviews within 90 days
- Domain citation rate increases quarter-over-quarter
- Content refresh cycle time decreases (rule change → updated content published)
- Client question-to-content coverage ratio improves (fewer client questions without matching content)

---

## 8. Technical Constraints

| Constraint | Rationale |
|---|---|
| Open-source stack only | No Pinecone, no paid vector DBs, no proprietary APIs beyond what's already in use |
| WSL-hosted | Runs on existing WSL environment. No new cloud infrastructure. |
| LightRAG as graph engine | Already proven for sitemap ingestion. Don't swap vector DBs. |
| Ollama for embeddings + inference | On-premise, zero-cost. Cloud fallback for larger models. |
| FastAPI for API layer | Consistent with existing services. Lightweight. |
| Systemd for service management | Consistent with existing infrastructure. |

---

## 9. Open Questions

These must be resolved before Phase 1 build begins:

| # | Question | Impact | Owner |
|---|---|---|---|
| Q1 | Are real estate sites actually cited by AI Overviews at all? | If no, AEO optimization may be premature for this vertical | Research backlog P0 |
| Q2 | Does FAQ schema empirically correlate with citation in real estate? | If no, rule "FAQ → citation" is invalid and should be removed | Research backlog P0 |
| Q3 | What do the initial 2-3 intelligence sources look like? Which ones? | Defines scope of Phase 1 rule inventory | Needs decision |
| Q4 | Is the Domain KG one LightRAG instance or two (quann-chat + methodology)? | Affects deployment architecture and dashboard design | Depends on Q1-Q2 resolution |
| Q5 | Should the dashboard replace all existing services (nexus_server, lightrag_unified_ui)? | Affects migration plan | Yes — per clean-slate decision |
| Q6 | What's the minimum viable UI — single page app with sidebar, or separate pages? | Affects frontend framework choice | SPA with sidebar per architecture doc |

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AEO/GEO requirements change faster than we can track | Medium | High | Source rotation design. Rule confidence grading. Don't auto-apply speculative rules. |
| AI Overviews don't cite real estate content at all | Medium | High | Validate P0 research before Phase 1 build. If confirmed, pivot to industries with higher citation rates. |
| holisticseo.digital stops publishing | Low | Medium | Already designed for. Source rotation handles this. |
| LightRAG performance degrades at scale | Low | Medium | Proven at 33K documents. Monitor. Chunk size tuning available. |
| User adoption — too complex for content writers | Medium | Medium | Stub panels show roadmap without complexity. Gap view is the primary interface. Hide graph explorer behind advanced toggle. |
| Alert fatigue — freshness alerts accumulate, user ignores all | High | Medium | Confidence auto-decay circuit breaker. Gap dismissal with rationale. Degraded alerts auto-downgrade and stop nagging. |
| Cost overrun — LLM extraction costs accumulate unnoticed | Medium | Medium | Per-source cost tracking from day one. Signal-to-cost ratio gate (min 10:1). Monthly budget alert. |
| Confidence inflation — rules confirmed by own success, never falsified | Medium | High | Negative validation: zero citations after 6 months → confidence downgrade. Absence of evidence IS evidence when enough time passes. |
| Source contradiction explosion — quadratic growth at 10+ sources | Low | Medium | Contradiction clustering by consensus ratio. Strong consensus (4:1+) auto-resolves. Only weak consensus (2:2) hits human review. |
| Content refresh cascade — backlog grows faster than writer can clear | Medium | Medium | Refresh impact scoring: traffic × entity centrality, not count. High-impact pages first. |

---

## 11. Architectural Decision Record (ADR)

Decisions that constrain future choices. Recorded so we know why we're locked in.

| ID | Decision | Rationale | Date | Reversible? |
|---|---|---|---|---|
| ADR-1 | Entity schema IS versioned from day one (v1, v2, v3) | Without versioning, every schema change is breaking. With versioning, old and new entities coexist, migrations are explicit. | 2026-05-13 | No — retrofitting versioning later is a migration nightmare |
| ADR-2 | Rules carry confidence levels that auto-decay | Prevents stale intelligence from masquerading as current. The system should telegraph its own uncertainty. | 2026-05-13 | Yes — decay thresholds are configurable |
| ADR-3 | No component failure takes down entire system | Graceful degradation modes defined for every component. Dashboard failing should not stop intelligence gathering. | 2026-05-13 | No — retrofitting degraded modes is harder than building them |
| ADR-4 | Gap dismissal feeds back into rule confidence | The human content writer IS the validation mechanism. System recommendations that get repeatedly dismissed should lose confidence. | 2026-05-13 | Yes — feedback weight is configurable |
| ADR-5 | Source onboarding requires signal-to-cost ratio > 10:1 | Prevents financially unsustainable source growth. Every new source increases token spend. Must justify itself. | 2026-05-13 | Yes — threshold is configurable |
| ADR-6 | Intelligence Layer is source-agnostic | Sources can be added, removed, or replaced without breaking the system. No source is permanent. | 2026-05-13 | No — this is the architectural foundation |
| ADR-7 | Domain KG is industry-agnostic | Real estate today, any vertical tomorrow. The architecture doesn't know what industry it's serving. | 2026-05-13 | No — this is the architectural foundation |

---

## 12. Document Governance

- **Review cadence:** Revisit before any build decision. Update after any substantive architecture discussion.
- **Versioning:** Major version for scope changes. Minor version for refinements and clarifications.
- **Relationship to architecture skill:** The architecture skill defines the *how*. This PRD defines the *what and why*. They must stay consistent. Changes to one trigger review of the other.
- **Visual blueprint:** `references/blueprint.mermaid` — the system flow diagram. Update when architecture changes.
- **Decision log:** Significant product decisions (scope changes, feature rejection, priority shifts) appended here as ADR entries. Cross-reference with Conversation Evolution Log in architecture skill.

---

## Appendix A: Terminology

| Term | Definition |
|---|---|
| **Intelligence Layer** | The source-agnostic monitoring system that extracts structured rules from patents, docs, research, announcements, and observed behavior |
| **Domain KG** | The industry-specific knowledge graph (real estate entities, relationships, content inventory) structured by current rules |
| **Rule** | A structured, sourced, confidence-graded requirement extracted from the Intelligence Layer |
| **Gap** | A detected mismatch between what rules require and what content delivers |
| **AEO** | Answer Engine Optimization — optimizing for AI Overviews, featured snippets, Perplexity |
| **GEO** | Generative Engine Optimization — optimizing for ChatGPT Search, Gemini, Claude |
| **Need Graph** | Client KG concept: anonymized patterns of questions, misconceptions, and emotional signals. Strip WHO, keep WHAT. |
| **Novel Emergence** | Insight that exists in no single source — only discoverable by cross-referencing intelligence signals + domain data + client patterns |
| **Source Rotation** | The ability to add, remove, and replace intelligence sources without breaking the rule extraction pipeline |

## Appendix B: Revision History

| Version | Date | Changes | Author |
|---|---|---|---|
| 0.1.0 | 2026-05-13 | Initial PRD drafted from architecture discussions | Hermes |
