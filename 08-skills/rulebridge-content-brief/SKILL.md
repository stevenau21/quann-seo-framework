---
name: rulebridge-content-brief
description: Bifurcated RuleBridge for connecting extracted architect frameworks to real-site gap audits and content brief generation. Three-way join engine fuses deterministic gaps, directive cards (Injection Cap), and Domain KG entities with cross-page gap discovery. Canonical 4-section markdown output with priority scoring.
---

# RuleBridge + Content Brief Generator (Complete Pipeline)

## Purpose

Prove end-to-end ROI of the Architect Extraction Pipeline by turning 144 extracted Tier 1 flashcards into:
1. **Deterministic page audits** — 15 computable checks (regex, counts) that run locally with zero API cost, integrated into kernel_v2.py's `check_rules()` loop
2. **Three-way join content briefs** — fusing gap data, capped directives, and Domain KG entity context into canonical 4-section writer-ready briefs

## Architecture

```
Phase 5 flashcards (144 GROUNDED Tier 1)  ─→  build_bridge_schema.py
                                                      │
                                              bridge_schema.json
                                             (28 deterministic + 116 directive)
                                                      │
                                          ┌───────────┴───────────┐
                                          │                       │
                                   Deterministic Track     Directive Track
                                   (rule_bridge.py)        (rule_bridge.py)
                                   15 check methods         route_directives()
                                   run on every page        Injection Cap: 5-8
                                          │                       │
                                          ▼                       │
                                    kernel_v2.py                 │
                                    gap_report.json              │
                                          │                       │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          generate_content_brief.py
                                          ┌───────────────────────┐
                                          │  ThreeWayJoin Engine   │
                                          │  ┌─────────────────┐   │
                                          │  │ Stream 1: Gaps   │   │
                                          │  │ (Tier 1 fails)   │   │
                                          │  ├─────────────────┤   │
                                          │  │ Stream 2: Caps   │   │
                                          │  │ (Directive route)│   │
                                          │  ├─────────────────┤   │
                                          │  │ Stream 3: KG     │   │
                                          │  │ (Domain entities)│   │
                                          │  └─────────────────┘   │
                                          └───────────────────────┘
                                                      │
                                                      ▼
                                              Canonical Brief (.md)
                                              4 sections + Priority Score
```

## Files

| File | Role | Status |
|---|---|---|
| `build_bridge_schema.py` | Reads `phase5_frameworks.json`, classifies each card, writes `bridge_schema.json` | ✅ Complete |
| `bridge_schema.json` | Canonical schema: 144 cards with check_category, check_method, severity, applies_to | ✅ Complete |
| `rule_bridge.py` | `RuleBridge` class: `run_deterministic_checks()`, `route_directives()`, `build_directive_prompt_section()` | ✅ Complete |
| `kernel_v2.py` | Modified `check_rules()` accepts optional `bridge` param; appends bridge results to gap report | ✅ Complete |
| `generate_content_brief.py` | **New**: Three-way join engine + DomainKGQuery + Priority Score + canonical markdown renderer | ✅ Complete |
| `gap_report.json` | Kernel output (consumed as input by the generator) | ✅ Auto-generated |
| `knowledge-synthesis/briefs/` | Output directory for generated briefs | ✅ Auto-populated |

## Key Design Decisions

### 1. Bifurcated Execution (~20% deterministic, ~80% directive)
Deterministic checks run on EVERY page with zero API calls. Directive rules are NEVER evaluated at audit time — they bypass the page entirely and are only injected when content briefs are generated. This keeps the audit fast, stable, and cost-free.

### 2. Entity Anchoring Constraint
The Content Brief Generator does NOT just merge gaps + directives. It also pulls real entities from the Domain KG (LightRAG workspace). The `DomainKGQuery.get_gap_entities()` method discovers entities present on **sibling pages** (same page_type, real, non-template) that are **missing from the target page**. This prevents generic SEO essays — every content requirement is anchored to a real Katy/Texas real estate data point.

### 3. Injection Cap (max 5-8 directives)
`route_directives()` uses three-pass weighted selection:
- **Pass 1: Direct hits (~50%)** — directives from categories whose corresponding deterministic checks FAILED
- **Pass 2: Page matches (~30%)** — directives applicable to the page type but not yet triggered
- **Pass 3: Top-level fill (~20%)** — directives from the most-represented framework

Without the cap, 116 directives flood the LLM prompt → context collapse.

### 4. Non-Brittle Page Mapping
Legal/privacy pages receive Entity-Based SEO and Content Quality (E-A-T) directives. Categories with `applies_to` lists include `legal`, `policy` for `entity_requirements`, `content_strategy`, and `case_study_format`. No page type is left empty.

### 5. Priority Score (0-100)
Four-factor weighted score determines brief urgency:
| Factor | Weight | Description |
|---|---|---|
| Deterministic Gap Rate | 40% | `det_fails / total_det_checks` |
| Kernel Failures | 25% | `kernel_fails × 8` (capped at 100) |
| Directive Injections | 20% | `directive_count / cap × 100` |
| KG Anchor Entities | 15% | `anchor_count / 15 × 100` |

### 6. Sibling-Page Gap Entity Discovery
`get_gap_entities(url, page_type)` compares the target page against all sibling pages:
1. Identifies sibling pages (same `page_type`, real, non-template)
2. Collects all clean entities from siblings
3. Subtracts entities already on the target page
4. Ranks remaining by domain relevance (keyword match + relation count + page count)
5. Returns top 10 highest-value missing entities

## Canonical Brief Structure (4 Sections)

1. **Meta-Information & Priority Score** — URL, page type, compliance, word count, 4-factor priority breakdown
2. **Deterministic Fixes (The Gaps)** — Bridge-detected gaps + Kernel-detected gaps, each with rule text, detail, fix directive
3. **Primary Domain Entities** — Anchor entities (on-page) + Missing entities (on siblings, absent here) + Contaminated entities (do not use)
4. **Architectural Directives** — Capped directives grouped by category, formatted as a markdown block ready for LLM injection

## LightRAG Data Format Quirks

### relation_pairs are lists, not dicts
```python
# Correct:
subj, obj = pair[0], pair[1]
# Wrong:
subj = pair.get("subject", "")
```

### Directive display in prompts
`route_directives()` returns dicts with BOTH `content` (short name) and `prompt_fragment` (full actionable text). Always use `d['prompt_fragment']` for prompt injection, NOT `d['content']`.

### Content may be extracted text, not raw HTML
Many HTML-specific regex checks (viewport meta, image alt) may return 0 matches because the content fed to the bridge is LightRAG's extracted text, not the raw HTML. This is a pipeline limitation.

## Usage

```bash
# Single page (markdown output)
python3 generate_content_brief.py --url https://quann.homes/blog/out-of-state-buyer-guide

# JSON output
python3 generate_content_brief.py --url ... --format json

# Batch all real pages
python3 generate_content_brief.py --all-urls

# Custom injection cap
python3 generate_content_brief.py --url ... --cap 5
```

Full pipeline run:
```bash
cd /home/steve/lightrag-apps/quann-chat
python3 kernel_v2.py                    # produces gap_report.json
python3 generate_content_brief.py --all-urls  # produces 12 briefs
```

## Integration Pattern

```python
from rule_bridge import RuleBridge
from generate_content_brief import ThreeWayJoin

# Audit stage
bridge = RuleBridge("bridge_schema.json")
results = bridge.run_deterministic_checks(content, "blog_post")

# Brief generation stage
engine = ThreeWayJoin()
brief = engine.build("https://quann.homes/blog/out-of-state-buyer-guide")
md = engine.format_markdown(brief)
# brief is a dict with meta, stream_1_gaps, stream_2_directives, stream_3_entities
```

## Testing Results

End-to-end against quann.homes (12 real pages):
- 117 bridge checks per full run
- 53 pass, 46 fail, 18 unverified
- 8 directives injected per brief (from 116 available)
- 15 anchor entities + 10 gap entities per blog post
- Priority scores: 60-62/100 for blog posts
- Legal pages receive entity directives (not left empty)

## Deterministic Check Registry (15 implemented)

| check_method | What it checks |
|---|---|
| `canonical_url_present` | `<link rel="canonical">` presence |
| `preload_key_requests` | `<link rel="preload">` for critical assets |
| `javascript_deferred` | `defer` or `async` on script tags |
| `cdn_detected` | CDN domains in src/href (cloudfront, fastly, etc.) |
| `no_session_ids_in_urls` | Session IDs in URL query params |
| `content_visibility_auto` | `content-visibility: auto` in CSS |
| `no_legacy_position_animations` | top/left/bottom/right animations |
| `transform_animations` | CSS transform usage vs legacy position animations |
| `ssr_or_prerender` | Empty `<div id="root">` (SPA detection) |
| `critical_request_chain_short` | Render-blocking chain depth (CSS + JS - preloads) |
| `review_schema_present` | Review/AggregateRating schema |
| `viewport_meta_present` | `<meta name="viewport">` |
| `image_alt_present` | `<img>` tags missing `alt` |
| `hreflang_present` | `<link rel="alternate" hreflang="...">` |
| `localbusiness_schema_present` | LocalBusiness/RealEstateAgent structured data |
| `faceted_nav_clean` | Faceted/filter URL params in links |
| `dead_code_indicators` | Empty style blocks, jQuery references, Bootstrap duplication |
| `thin_content` | Word count < 300 (thin threshold) |

## Pitfalls

- **Schema-implementation drift**: Adding a check to `bridge_schema.json` does NOT make it run. Must also add a matching method `_check_{method}` in `rule_bridge.py`.
- **Injection Cap is critical**: Without the 5-8 cap, 116 directives will cause LLM context collapse. Never skip the router.
- **Legal pages need cross-paradigm mapping**: Don't restrict `applies_to` too narrowly. Entity and Content Quality directives should reach all page types.
- **Bridge schema is source of truth**: If classification changes, regenerate with `build_bridge_schema.py`, never hand-edit `bridge_schema.json`.
- **Content is LightRAG text, not HTML**: HTML-specific checks (viewport, image alt) may return 0 matches because kernel feeds extracted text. This is a pipeline limitation, not a code bug.
- **Missing siblings = empty gap entities**: For page types with no sibling pages, `get_gap_entities()` returns empty. This is expected behavior.
- **relation_pairs are lists, not dicts**: Always use `pair[0]`, `pair[1]` for subject/object — `.get()` will AttributeError.
