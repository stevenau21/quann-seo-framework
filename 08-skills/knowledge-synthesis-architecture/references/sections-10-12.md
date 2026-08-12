## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AEO/GEO requirements change faster than we can track | Medium | High | Source rotation design. Rule confidence grading. Don't auto-apply speculative rules. |
| AI Overviews don't cite real estate content at all | Medium | High | Validate P0 research before Phase 1 build. If confirmed, pivot to industries with higher citation rates. |
| holisticseo.digital stops publishing | Low | Medium | Already designed for. Source rotation handles this. |
| LightRAG performance degrades at scale | Low | Medium | Proven at 33K documents. Monitor. Chunk size tuning available. |
| User adoption — too complex for content writers | Medium | Medium | Stub panels show roadmap without complexity. Gap view is the primary interface. Hide graph explorer behind advanced toggle. |
| Alert fatigue — freshness alerts accumulate, user ignores all | High | Medium | Confidence auto-decay circuit breaker. Gap dismissal with rationale. Degraded alerts auto-downgrade and stop nagging. |
| Cost overrun — LLM extraction costs accumulate unnoticed | Medium | Medium | Per-source cost tracking from day one. Signal-to-cost ratio gate (minimum 10:1). Monthly budget alert. |
| Confidence inflation — rules confirmed by own success, never falsified | Medium | High | Negative validation: zero citations after 6 months → confidence downgrade. Absence of evidence IS evidence when enough time passes. |
| Source contradiction explosion — quadratic growth at 10+ sources | Low | Medium | Contradiction clustering by consensus ratio. Strong consensus (4:1+) auto-resolves. Only weak consensus (2:2) hits human review. |
| Content refresh cascade — backlog grows faster than writer can clear | Medium | Medium | Refresh impact scoring: traffic × entity centrality, not count. High-impact pages first. |

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

## 12. Document Governance

- **Review cadence:** Revisit before any build decision. Update after any substantive architecture discussion.
- **Versioning:** Major version for scope changes. Minor version for refinements and clarifications.
- **Relationship to architecture skill:** The architecture skill defines the *how*. This PRD defines the *what and why*. They must stay consistent. Changes to one trigger review of the other.
- **Visual blueprint:** `references/blueprint.mermaid` — the system flow diagram. Update when architecture changes.
- **Decision log:** Significant product decisions appended to the ADR above. Cross-reference with Conversation Evolution Log in architecture skill.