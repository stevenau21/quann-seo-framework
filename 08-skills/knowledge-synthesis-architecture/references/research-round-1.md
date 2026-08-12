# Research Round 1 — P0 Gate Validation (2026-05-13)

> **UPDATED 2026-05-13:** P0-5 and P0-2 findings added in Round 2. See `references/research-round-2.md` for schema correlation deep-dive, entity density analysis, and remaining primary research gaps.

## P0-1: Do AI answer engines cite structured content across industries?

**Verdict: YES — but the ecosystem is shifting toward self-preferencing.**

### Key Data Points

| Data Point | Value | Source | Date |
|---|---|---|---|
| AI Overview presence in search queries | ~16% (up from 6.49% in Jan 2025) | Semrush (200K+ keywords) | Jan-Oct 2025 |
| AI Overviews top-12 citation rate | 75% (late 2024 baseline) | Search Engine Land | Late 2024 |
| AI Overviews top-10 citation overlap | 38% (declining) | Ahrefs | Early 2026 |
| Google.com self-citation rate in AI Mode | 17.42% (tripled from 5.7%) | SE Ranking (1.3M citations) | Jun 2025 → Mar 2026 |
| Google+YouTube total AI Mode control | ~20% of all sources | SE Ranking | Mar 2026 |
| Google dominates 19 of 20 niches as top-cited | #1 cited domain | SE Ranking | Mar 2026 |
| Perplexity always cites sources | 100% of responses include clickable citations (3-7 per answer) | Multiple studies | 2025-2026 |
| ChatGPT default attribution | Worst in class — rarely cites without prompting | Platform comparison | Apr 2026 |
| Claude unprompted citation rate | 16% | Platform comparison | Apr 2026 |
| Claude prompted citation rate | 97% | Platform comparison | Apr 2026 |
| Gemini unprompted citation rate | 6% | Platform comparison | Apr 2026 |
| Cross-platform citation overlap | Only 11% of sites cited by both ChatGPT AND Perplexity | AI Visibility Report | 2025 |

### Implications for Architecture

1. **Citation IS happening** — AEO/GEO optimization is not vibes-based. Content does get cited.
2. **But the ground is shifting** — Google's self-preferencing is accelerating. By 2027, 25%+ of AI Mode citations may be Google properties. This makes Perplexity and other independent engines more important for third-party content visibility.
3. **Ranking ≠ AI visibility** — the 38% overlap means traditional SEO rank is a weak predictor. Content STRUCTURE (length, headings, entity coverage, schema) matters more for AI citation than position.
4. **Perplexity is the measurement platform** — always cites, transparent attribution. Ideal for validating content strategies.

---

## P0-3: Cadence of search/AI guideline changes

**Verdict: Core updates ~quarterly. AI-related changes accelerating. Schema.org slowing.**

### Key Data Points

| Data Point | Value | Source |
|---|---|---|
| Google core updates in 2025 | 3 (March, August, November) | Google Search Status Dashboard |
| Google spam updates in 2025 | 2+ | Google Search Status Dashboard |
| Total confirmed Google updates 2025 | 7+ | Google Search Central |
| Schema.org releases 2025-2026 | ~3 minor releases (Product, Event, Organization refinements) | schema.org |
| Major schema.org structural changes | Slowing — most activity is refinement not expansion | schema.org |
| Google self-citation growth rate | 3x in <1 year (5.7% → 17.42%) | SE Ranking |
| AI Overviews query coverage growth | 2x in 3 months (6.49% → 13.14%) | Semrush |

### Implications for Architecture

1. **Minimum polling frequency: monthly** — Google core updates are quarterly, but AI-specific changes (AIO expansion, AI Mode adjustments) are more frequent. Monthly Intelligence Layer refresh is the floor.
2. **Schema.org is NOT a fast-moving target** — the schema landscape is stable enough that extraction rules built on schema types won't go stale monthly. Quarterly review is sufficient.
3. **Self-preferencing rate is the canary** — if Google's self-citation rate keeps growing at 3x/year, by late 2026 it will be ~25-30%. This fundamentally changes what "AEO optimization" means. Track this quarterly.
4. **Polling cost optimization** — monthly polling = 12 extractions/year/source. At the source onboarding gate (10:1 signal-to-cost), this bounds total annual Intelligence Layer cost.

---

## P0-4: Tried-and-true validation methods for SEO/GEO/AEO claims

**Verdict: Citation audits are the fastest reliable method. Controlled A/B is gold but slow.**

### Validation Method Hierarchy

| Method | Reliability | Cycle Time | Best For | Caveats |
|---|---|---|---|---|
| Citation audits | Medium-High | 7-30 days | AEO/GEO validation | Correlational, not causal |
| Controlled A/B tests | High | 30-90 days | SEO ranking claims | Requires traffic. Slow feedback. |
| Competitor schema audits | Medium | 1-7 days | Gap identification | Doesn't prove causality |
| Patent-to-product correlation | Medium | 12-24 months | Predictive intelligence | Long lead time. Not all patents ship. |
| Practitioner case studies | Low | Variable | Hypothesis generation | Confirmation bias rampant |

### Recommended Validation Stack for Our System

```
Primary: Citation audit
  → Publish entity-anchored content with full schema markup
  → Query Perplexity + Google AI Overviews at T+7, T+30, T+90
  → Track: cited? which entity? which schema type? position?

Secondary: Competitor schema audit  
  → Identify top-cited competitors in target verticals
  → Reverse-engineer their schema markup and content structure
  → Map: what do cited pages have that non-cited pages lack?

Tertiary: Patent monitoring
  → Track patent filings from Google, Microsoft/OpenAI, Meta
  → Flag speculative rules for re-check at T+12 months
  → Validate when product ships or patent expires

Quaternary: Controlled A/B (later, when traffic exists)
  → Publish structured vs. unstructured versions of similar content
  → Measure citation rate difference over 90 days
```

### Key Principle
The fastest validation loop that produces falsifiable results is a citation audit. You publish content, you query AI engines, you check if you're cited. This is the core feedback mechanism that the Intelligence Layer should automate. The system should be able to test its own rules by publishing test content and measuring citation outcomes.

---

## P0-5 & P0-2: Schema and Entity Density (Round 2)

See `references/research-round-2.md` for the full deep-dive on:
- FAQ/HowTo/Article schema citation correlation (P0-5)
- Entity density + citation correlation (P0-2)
- Remaining primary research gaps requiring direct experimentation
- Per-platform rule recommendation (schema rules must be platform-specific, not universal)

---

*Research conducted: 2026-05-13. Updated 2026-05-13 with cross-reference to Round 2. Sources: Semrush, SE Ranking, Ahrefs, AI Visibility Report, platform comparison studies, Google Search Central, schema.org.*
