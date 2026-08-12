# Research Round 2 — P0-5 and P0-2 Deep Dive (2026-05-13)

## P0-5: Do FAQ/HowTo/Article schema types correlate with AI citation?

**Verdict: MIXED SIGNALS — schema markup matters but differently per platform. No single study quantifies the effect.**

### Cross-Platform Schema Behavior

| Platform | Schema Correlation Signal | Evidence Strength |
|---|---|---|
| **Perplexity** | Q&A adjacency matters MORE than explicit schema markup. Inline citation format (question → answer → source) is the mechanism, not JSON-LD blocks. | Medium — platform design is built around Q&A format |
| **Google AI Overviews** | Schema markup historically correlated with featured snippets (pre-AI era). AI Overviews may use different ranking signals — the SE Ranking study found domain authority and content length predict AI visibility better than schema alone. | Medium-weak — no study isolates schema effect on AIO specifically |
| **ChatGPT Search** | Source attribution is inconsistent and rarely visible. Schema markup effect is essentially unmeasurable due to opaque citation behavior. | Weak — platform isn't designed for transparent citation |
| **Claude** | 16% unprompted citation rate, jumps to 97% when asked. Schema markup's role unclear — likely content comprehensiveness matters more. | Weak |
| **Gemini** | 6% unprompted citation rate. Even when content is relevant (81% of time), attribution fails. Schema markup is likely irrelevant given the platform's design. | Very weak |

### Key Finding: Schema is Necessary but Not Sufficient

Schema markup creates the CONDITIONS for citation (machines can parse your content's meaning), but it doesn't CAUSE citation. What causes citation is:

1. **Content format matching** — Perplexity wants Q&A format; Google AI Overviews wants comprehensive definitions
2. **Authority signals** — domain authority outranks schema for Google AI Mode
3. **Content length + depth** — 2,300+ words, structured headings
4. **Freshness** — recent publish dates (signal strength unquantified but likely significant)

### Implication for Architecture

Don't build a rule that says "add FAQ schema → get cited." Build rules that say:
- "For Perplexity: structure content as Q&A with explicit answer adjacency"
- "For Google AI: comprehensive entity coverage with structured headings"
- "Schema markup is the delivery mechanism, not the signal"

Schema extraction rules should detect whether pages HAVE the right schema FORMAT, not whether they have schema at all. The absence of schema is a gap. The presence of schema is table stakes.

---

## P0-2: Content properties that correlate with AI citation (cross-industry)

**Verdict: PARTIALLY VALIDATED — we know what correlates but haven't measured entity density directly.**

### Confirmed Correlates (from SE Ranking 1.3M citation study)

| Property | Correlation | Strength | Source |
|---|---|---|---|
| Content length (2,300+ words) | Strong positive | High | SE Ranking AI Mode study |
| Domain authority (high DA) | Strong positive | High | SE Ranking AI Mode study |
| Structured section headings (H2, H3) | Strong positive | High | SE Ranking AI Mode study |
| Organic top-10 ranking | Weak positive (only 38% overlap) | Medium | Ahrefs AI Overview study |

### Unvalidated (No Direct Studies Found)

| Property | Hypothesis | Why Unvalidated |
|---|---|---|
| Entity density (# of named entities per 1000 words) | Higher entity density → richer machine understanding → higher citation probability | No published study measures this. Requires parsing content with NER, counting entities, correlating with citation data. |
| Entity relationship explicitness ("X is different from Y because...") | Explicit entity relationships → easier for LLMs to synthesize → higher citation probability | Same as above. Not directly measured. |
| Schema type diversity (multiple schema layers on single page) | More schema types → more extraction points → higher citation probability | Not isolated as variable. Most cited pages have at least one schema type, but having 3 types vs. 1 — no study exists. |
| Content freshness delta (days since publish) | Fresh content gets cited more. But what's the half-life? | Freshness is assumed but not quantified per industry. |
| Answer adjacency (question → immediate answer <60 words) | This is Perplexity's core mechanism but no study quantifies the effect size. | Platform-specific design, not a published correlation study. |

### Cross-Platform Overlap Finding

From the AI Visibility Report:
- **Only 11% of sites get cited by BOTH ChatGPT AND Perplexity** — meaning different platforms use VASTLY different source selection criteria
- This implies entity-first strategy must be multi-platform, not single-platform
- Content properties that work for Perplexity (Q&A format) may not work for ChatGPT (comprehensive depth)

### Implication for Architecture

The Intelligence Layer's rule extraction should produce PER-PLATFORM rules, not universal rules. A rule like "FAQ format drives citation" is true for Perplexity but unproven for Google AI. Each rule should carry `applies_to_platforms: ["perplexity"]` not `applies_to: ["AEO"]`.

---

## Remaining Research Gaps — Require Primary Data, Not Web Search

These questions CANNOT be answered by searching the web. They require direct experimentation:

| Gap | Method | Timeline | Priority |
|---|---|---|---|
| Schema citation correlation (P0-5 final answer) | **Citation audit:** Publish 20 test pages — 10 with full schema markup, 10 without. Query Perplexity + Google at T+7, T+30, T+90. Compare citation rates. | 90 days | P0 — blocks rule confidence system |
| Entity density correlation (P0-2 final answer) | **Content audit:** Parse 100 cited pages + 100 non-cited pages with NER (spaCy). Count entities. Run logistic regression: does entity density predict citation? | 2-3 days (compute only) | P0 — validates core entity-first assumption |
| Entity relationship explicitness | **Same as above:** Use relationship extraction (RE model) on cited vs. non-cited pages. Does explicit relationship language predict citation? | 2-3 days (compute only) | P1 — nice to have, refines rules |
| Content freshness half-life per industry | **Longitudinal citation tracking:** Monitor 100 cited pages over 12 months. Track when citations drop. | 12 months | P2 |
| Multi-platform content format effectiveness | **A/B across platforms:** Same entity content, different formats (Q&A vs. essay vs. guide vs. comparison). Test on each platform. | 90 days | P2 |

---

## Consolidated P0 Gate Status (After Round 2)

| Gate | Status | Blocking Build? | Next Action |
|---|---|---|---|
| P0-1: Do AI engines cite? | ✅ YES | No | — |
| P0-3: Cadence of changes? | ✅ ~quarterly core, monthly AI | No | — |
| P0-4: Validation methods? | ✅ Citation audits fastest | No | — |
| P0-5: Schema correlation? | 🔶 Mixed signals — needs primary audit | **Partially** — can build schema rules as "necessary but not sufficient" but confidence stays at `probable` not `confirmed` until audit | Run citation audit with test pages (90-day timeline) |
| P0-2: Entity density correlation? | 🔶 Unvalidated — needs NER-based content audit | **Partially** — can build entity-extraction pipeline but core assumption ("entity density → citation") is theoretical until validated | Run NER audit on cited vs. non-cited pages (2-3 day compute window) |

### Recommended Action

P0-5 and P0-2 need PRIMARY research — not web search. Web search answered what's publicly known. The remaining gaps require collecting data directly:
1. **Build an entity density analyzer** — parse cited + non-cited pages, count entities, test correlation
2. **Run a schema citation audit** — publish test content, measure citation outcomes

MVP can still proceed with P0-5 and P0-2 at `probable` confidence. The architecture includes degradation mechanisms precisely for this scenario — rules that aren't `confirmed` don't drive automatic content changes, they drive monitoring.

---

*Research conducted: 2026-05-13. Sources: SE Ranking 1.3M citation study, AI Visibility Report, platform comparison study (Apr 2026), Semrush AIO study. Gaps identified: no published study directly measures entity density or schema citation correlation for AI Overviews specifically.*
