#!/usr/bin/env python3
"""
Build the Bifurcated RuleBridge schema from Phase 5 Tier 1 cards.

Classifies each of 144 cards into:
  - DETERMINISTIC: page-content-regexable check (12 check types)
  - DIRECTIVE:   semantic/heuristic, injected at brief-generation time

Also computes the Directive Router — embeddings + metadata for
the Injection Cap (~5-8 directives per brief).
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PHASE5 = Path("/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur/phase5_frameworks.json")
OUTPUT = Path("/home/steve/lightrag-apps/quann-chat/bridge_schema.json")

# ── Deterministic Check Registry ──────────────────────────────────────────
# Each check maps to a regex or counting rule that runs on page HTML/content.
# check_method is the function name in rule_bridge.py.
DETERMINISTIC_CHECKS = {
    "canonical_url_present": {
        "method": "canonical_url_present",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
        "priority": "high",
        "gap_message": "Page is missing a canonical URL tag — search engines may index duplicate versions.",
        "fix_directive": "Add <link rel='canonical' href='...'> to <head>",
        "detection": "regex: <link[^>]*rel=[\"']canonical[\"']",
    },
    "preload_key_requests": {
        "method": "preload_key_requests",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage"],
        "priority": "medium",
        "gap_message": "No preload hints found — key requests (fonts, CSS) load late.",
        "fix_directive": "Add <link rel='preload' href='...' as='font|style|script'> for critical resources",
        "detection": "regex: rel=[\"']preload[\"'].*as=",
    },
    "javascript_deferred": {
        "method": "javascript_deferred",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage", "about"],
        "priority": "medium",
        "gap_message": "Scripts lack defer/async — render-blocking JavaScript detected.",
        "fix_directive": "Add defer or async attribute to <script> tags loading external JS",
        "detection": "regex: <script[^>]*(defer|async)[^>]*src=",
    },
    "cdn_detected": {
        "method": "cdn_detected",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage", "about"],
        "priority": "low",
        "gap_message": "No CDN detected for static assets — latency may increase cost-of-retrieval.",
        "fix_directive": "Serve fonts, images, and CSS from a CDN (Cloudflare, BunnyCDN, etc.)",
        "detection": "regex: (cdn\\.|cloudfront|fastly|bunnycdn|jsdelivr|unpkg)",
    },
    "no_session_ids_in_urls": {
        "method": "no_session_ids_in_urls",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
        "priority": "high",
        "gap_message": "Session IDs found in URLs — creates duplicate content for search engines.",
        "fix_directive": "Remove session_id/sid/phpsessid from all internal hrefs",
        "detection": "regex: [?&](session_?id|sid|phpsessid)=",
    },
    "content_visibility_auto": {
        "method": "content_visibility_auto",
        "category": "technical_seo",
        "applies_to": ["blog_post", "homepage"],
        "priority": "low",
        "gap_message": "content-visibility: auto not detected — off-screen rendering optimization missing.",
        "fix_directive": "Add content-visibility: auto to below-fold sections for rendering performance",
        "detection": "regex: content-visibility:\\s*auto",
    },
    "no_legacy_position_animations": {
        "method": "no_legacy_position_animations",
        "category": "technical_seo",
        "applies_to": ["blog_post", "homepage", "service"],
        "priority": "low",
        "gap_message": "Legacy top/left position animations detected — use transform for GPU-accelerated animations.",
        "fix_directive": "Replace top/left animation keyframes with transform: translate() for compositor-only rendering",
        "detection": "regex: (top\\s*:\\s*\\d|left\\s*:\\s*\\d).*(@keyframes|animation)",
    },
    "transform_animations": {
        "method": "transform_animations",
        "category": "technical_seo",
        "applies_to": ["blog_post", "homepage", "service"],
        "priority": "low",
        "gap_message": "CSS animations using top/left detected — use transform for GPU-accelerated rendering.",
        "fix_directive": "Replace top/left animation keyframes with transform: translate() for compositor-only rendering",
        "detection": "regex: (top\\s*:\\s*\\d|left\\s*:\\s*\\d).*(@keyframes|animation|transition)",
    },
    "ssr_or_prerender": {
        "method": "ssr_or_prerender",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage"],
        "priority": "high",
        "gap_message": "No SSR/prerender indicators — JavaScript-heavy pages may not be fully crawlable.",
        "fix_directive": "Use server-side rendering or pre-rendering to ensure search engines receive complete HTML",
        "detection": "negative: <div id='root'></div> with no fallback content (SPA indicator)",
    },
    "critical_request_chain_short": {
        "method": "critical_request_chain_short",
        "category": "technical_seo",
        "applies_to": ["blog_post", "homepage"],
        "priority": "medium",
        "gap_message": "Deep critical request chain detected — render-blocking resource waterfall.",
        "fix_directive": "Inline critical CSS, preload fonts, and reduce the depth of render-blocking request chains",
        "detection": "count: <script src=*> and <link rel=stylesheet> before first meaningful paint — heuristic",
    },
    "review_schema_present": {
        "method": "review_schema_present",
        "category": "local_seo",
        "applies_to": ["service", "homepage"],
        "priority": "medium",
        "gap_message": "No Review or AggregateRating schema — star ratings won't appear in SERP.",
        "fix_directive": "Add JSON-LD Review or AggregateRating schema for Google star ratings in search results",
        "detection": "regex: (Review|AggregateRating|reviewRating)[\"']",
    },
    "dead_code_indicators": {
        "method": "dead_code_indicators",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage"],
        "priority": "low",
        "gap_message": "Signs of unused/dead code — excessive CSS classes, empty style blocks, or orphaned scripts.",
        "fix_directive": "Remove unused CSS/JS, minify assets, and run Lighthouse coverage audit",
        "detection": "heuristic: empty <style> blocks, multiple copies of same library, excessive class count",
    },
    "viewport_meta_present": {
        "method": "viewport_meta_present",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
        "priority": "high",
        "gap_message": "Viewport meta tag missing — mobile rendering may be broken.",
        "fix_directive": "Add <meta name='viewport' content='width=device-width, initial-scale=1'> to <head>",
        "detection": "regex: <meta[^>]*name=[\"']viewport[\"']",
    },
    "image_alt_present": {
        "method": "image_alt_present",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage"],
        "priority": "medium",
        "gap_message": "Images missing alt text — accessibility and image search ranking impacted.",
        "fix_directive": "Add descriptive alt attributes to all <img> tags",
        "detection": "regex: <img[^>]*alt=[\"'][^\"']+[\"']",
    },
    "hreflang_present": {
        "method": "hreflang_present",
        "category": "multilingual_seo",
        "applies_to": ["blog_post", "homepage"],
        "priority": "low",
        "gap_message": "No hreflang annotations — search engines see this as single-language content.",
        "fix_directive": "Add <link rel='alternate' hreflang='...'> tags for language/region variants",
        "detection": "regex: <link[^>]*rel=[\"']alternate[\"'].*hreflang=",
    },
    "localbusiness_schema_present": {
        "method": "localbusiness_schema_present",
        "category": "local_seo",
        "applies_to": ["homepage", "service", "about"],
        "priority": "high",
        "gap_message": "No LocalBusiness schema — Google Maps and local pack visibility reduced.",
        "fix_directive": "Add JSON-LD LocalBusiness or RealEstateAgent schema with address, phone, geo coordinates",
        "detection": "regex: (LocalBusiness|RealEstateAgent|Place)[\"']",
    },
    "faceted_nav_clean": {
        "method": "faceted_nav_clean",
        "category": "technical_seo",
        "applies_to": ["blog_post", "service", "homepage"],
        "priority": "medium",
        "gap_message": "Faceted navigation query parameters found in internal links — crawl budget waste.",
        "fix_directive": "Canonicalize or noindex faceted URL variants; use rel=canonical on filter pages",
        "detection": "regex: (href=[\"'][^\"']*\\?(filter|sort|page|category|tag|color|size)=)",
    },
    "thin_content": {
        "method": "thin_content",
        "category": "content_depth",
        "applies_to": ["blog_post", "service"],
        "priority": "high",
        "gap_message": "Page word count below 300 — classified as thin content by quality raters.",
        "fix_directive": "Expand to 1500+ words covering entity, context, examples, and related subtopics",
        "detection": "count: words < 300",
    },
}

# ── Directive Injection Categories ────────────────────────────────────────
# When a brief is generated, directives are routed based on which
# categories are relevant to the failing page type.
DIRECTIVE_CATEGORIES = {
    "content_strategy": {
        "label": "Architectural Directives — Content Strategy",
        "description": "How to structure content semantically for topical authority",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
    },
    "entity_requirements": {
        "label": "Entity & Schema Requirements",
        "description": "Entity identity, relationships, and structured data patterns",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
    },
    "methodology_depth": {
        "label": "Methodology & Depth Requirements",
        "description": "Technical depth, NLP methods, and analytical rigor",
        "applies_to": ["blog_post", "service"],
    },
    "case_study_format": {
        "label": "Case Study & Evidence Standards",
        "description": "How to present evidence, cite sources, and build authority",
        "applies_to": ["blog_post", "about", "legal"],
    },
    "multilingual_consistency": {
        "label": "Multilingual & Cross-Language Consistency",
        "description": "Brand and topical consistency across language versions",
        "applies_to": ["blog_post", "homepage", "service"],
    },
    "conversion_optimization": {
        "label": "Conversion & Growth Architecture",
        "description": "User retention, A/B testing, ratings, and growth loops",
        "applies_to": ["service", "homepage", "about"],
    },
    "general_knowledge": {
        "label": "Foundational SEO Knowledge",
        "description": "Core search-engine principles every piece should respect",
        "applies_to": ["blog_post", "service", "homepage", "about", "legal", "policy"],
    },
}

# ── Card → Check Mapping ──────────────────────────────────────────────────
# Maps card content patterns to deterministic check methods.
# Multiple cards can map to the same check.
CARD_TO_CHECK = {
    # Technical SEO framework
    "canonical_url": "canonical_url_present",
    "Canonical URLs": "canonical_url_present",
    "preload key requests": "preload_key_requests",
    "Preload key requests": "preload_key_requests",
    "Preload": "preload_key_requests",
    "defer third-party": "javascript_deferred",
    "Defer third-party JavaScript": "javascript_deferred",
    "cdn": "cdn_detected",
    "CDN": "cdn_detected",
    "Use CDN": "cdn_detected",
    "session_id": "no_session_ids_in_urls",
    "Session IDs": "no_session_ids_in_urls",
    "content-visibility": "content_visibility_auto",
    "content-visibility: auto": "content_visibility_auto",
    "Use content-visibility": "content_visibility_auto",
    "Faceted Navigation": "faceted_nav_clean",
    "faceted nav": "faceted_nav_clean",
    "CLS": "content_visibility_auto",
    "Good CLS": "content_visibility_auto",
    # New: transform animations
    "transform instead of top/left": "transform_animations",
    "Use transform instead": "transform_animations",
    "Transform for animations": "transform_animations",
    "top/left for animations": "transform_animations",
    # New: SSR/prerender
    "server-side rendering": "ssr_or_prerender",
    "Server-side rendering": "ssr_or_prerender",
    "pre-rendering": "ssr_or_prerender",
    "Use pre-rendering": "ssr_or_prerender",
    # New: unused code
    "Clean unused code": "dead_code_indicators",
    "unused code": "dead_code_indicators",
    # New: critical request chain
    "Critical Request Chain": "critical_request_chain_short",
    "critical request": "critical_request_chain_short",
    # New: Lighthouse (heuristic — triggers SSR check)
    "Lighthouse": "critical_request_chain_short",
    # New: Google Search Console (heuristic — canonical check)
    "Google Search Console": "canonical_url_present",
    # New: A/B testing scripts
    "A/B testing": "canonical_url_present",  # presence of testing scripts/infrastructure
    "A/B Testing": "canonical_url_present",
    # New: ratings/reviews schema
    "ratings and reviews": "review_schema_present",
    "Ratings and reviews": "review_schema_present",
    "Manage ratings": "review_schema_present",
    # Multilingual
    "Inorganic Site Structure": "hreflang_present",
    "hreflang": "hreflang_present",
    # Holistic/Local SEO
    "local SEO": "localbusiness_schema_present",
    "Google My Business": "localbusiness_schema_present",
    # Content Quality
    "Thin Content": "thin_content",
    "thin content": "thin_content",
    # General Technical
    "viewport": "viewport_meta_present",
    "alt text": "image_alt_present",
    "image alt": "image_alt_present",
}


def classify_card(card: dict, framework_name: str) -> dict | None:
    """
    Classify a Tier 1 card into deterministic or directive track.
    Returns None if the card can't be mapped (shouldn't happen).
    """
    content = card.get("content", "").lower()
    target = card.get("target_entity", "").lower()
    card_id = card["card_id"]

    # Try to match a deterministic check
    for pattern, check_method in CARD_TO_CHECK.items():
        if pattern.lower() in content or pattern.lower() in target:
            check_def = DETERMINISTIC_CHECKS[check_method]
            # Only classify as deterministic if page_type makes sense
            # (applies_to filtering happens at runtime, but we mark it here)
            return {
                "card_id": card_id,
                "track": "deterministic",
                "content": card["content"],
                "target_entity": card.get("target_entity", ""),
                "action_directive": card.get("action_directive", ""),
                "type": card["type"],
                "framework": framework_name,
                "check": {
                    "method": check_def["method"],
                    "category": check_def["category"],
                    "priority": check_def["priority"],
                    "gap_message": check_def["gap_message"],
                    "fix_directive": check_def["fix_directive"],
                    "detection": check_def["detection"],
                },
            }

    # Not deterministic → directive. Determine injection category.
    category = _classify_directive_category(card, content, target)
    return {
        "card_id": card_id,
        "track": "directive",
        "content": card["content"],
        "target_entity": card.get("target_entity", ""),
        "action_directive": card.get("action_directive", ""),
        "type": card["type"],
        "framework": framework_name,
        "inject": {
            "category": category,
            "section": "architectural_directives",
            "sub_section": DIRECTIVE_CATEGORIES[category]["label"],
            "prompt_fragment": _build_prompt_fragment(card, framework_name, category),
        },
    }


def _classify_directive_category(card: dict, content: str, target: str) -> str:
    """Determine which injection category a directive card belongs to."""
    # Evidence/case studies → case_study_format
    if card["type"] == "evidence":
        return "case_study_format"
    if any(kw in content for kw in ["case study", "growth", "425%"]):
        return "case_study_format"

    # Entity-focused → entity_requirements
    if any(kw in content or kw in target
           for kw in ["entity", "knowledge panel", "knowledge graph",
                      "schema", "structured data", "brand serp",
                      "entity home", "entity description",
                      "fundamental facts", "entity identity"]):
        return "entity_requirements"

    # Methodological/technical depth → methodology_depth
    if any(kw in content or kw in target
           for kw in ["nltk", "wordnet", "lemmatization", "tokenization",
                      "stemming", "pagerank", "python", "advertools",
                      "knowledge graph api", "boolean model", "rankbrain",
                      "word cloud", "log file analysis", "data science"]):
        return "methodology_depth"

    # Conversion/growth → conversion_optimization
    if any(kw in content or kw in target
           for kw in ["conversion", "retention", "kpi", "a/b test",
                      "rating", "review", "aso", "app store",
                      "growth", "advocate", "referral"]):
        return "conversion_optimization"

    # Multilingual → multilingual_consistency
    if any(kw in content or kw in target
           for kw in ["language", "multilingual", "query expansion",
                      "inorganic", "cross-lingual"]):
        return "multilingual_consistency"

    # Content strategy (predicates, networks, topical maps, bridges, etc.)
    if any(kw in content or kw in target
           for kw in ["predicate", "verb", "semantic content network",
                      "topical map", "topical gap", "topical authority",
                      "contextual bridge", "source context", "frame semantic",
                      "brand identity", "topical consolidation",
                      "ranking signal", "historical data",
                      "cost of retrieval", "crawl budget",
                      "crawl efficiency", "crawl quota",
                      "semantic seo", "holistic seo",
                      "algorithmic trinity", "dwell time",
                      "e-a-t", "linguistic correctness",
                      "readability", "user engagement",
                      "understandability", "credibility",
                      "deliverability"]):
        return "content_strategy"

    # Default
    return "content_strategy"


def _build_prompt_fragment(card: dict, framework: str, category: str) -> str:
    """Build the injection prompt fragment for a directive card."""
    directive = card.get("action_directive", "understand")
    verb_map = {
        "implement": "MUST implement",
        "optimize": "MUST optimize for",
        "avoid": "MUST avoid",
        "monitor": "SHOULD monitor",
        "cite": "SHOULD cite or reference",
        "understand": "MUST demonstrate understanding of",
    }
    verb = verb_map.get(directive, "SHOULD address")

    return (
        f"CRITICAL ARCHITECTURAL DIRECTIVE (Koray Gubur — {framework}): "
        f"{verb}: {card['content']}"
    )


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    with open(PHASE5) as f:
        data = json.load(f)

    all_rules = []
    stats = defaultdict(int)

    for fw in data["frameworks"]:
        fw_name = fw["name"]
        for card in fw["tier_1_rules"]["cards"]:
            rule = classify_card(card, fw_name)
            if rule:
                all_rules.append(rule)
                stats[rule["track"]] += 1
                if rule["track"] == "deterministic":
                    stats[f"det_{rule['check']['method']}"] += 1
                else:
                    stats[f"dir_{rule['inject']['category']}"] += 1

    # Build the Directive Router index — for the Injection Cap
    directive_router = _build_directive_router(all_rules)

    bridge = {
        "bridge_version": "1.0.0",
        "source": "koray-gubur-phase5",
        "source_file": str(PHASE5),
        "tier": 1,
        "total_cards": len(all_rules),
        "classification": {
            "deterministic": stats["deterministic"],
            "directive": stats["directive"],
        },
        "rules": all_rules,
        "directive_router": directive_router,
        "deterministic_check_registry": {
            method: {
                "method": defn["method"],
                "category": defn["category"],
                "applies_to": defn["applies_to"],
                "priority": defn["priority"],
                "detection": defn["detection"],
            }
            for method, defn in DETERMINISTIC_CHECKS.items()
        },
        "directive_injection_categories": {
            cat: {
                "label": defn["label"],
                "description": defn["description"],
                "applies_to": defn["applies_to"],
            }
            for cat, defn in DIRECTIVE_CATEGORIES.items()
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(bridge, f, indent=2, ensure_ascii=False)

    # ── Summary ──
    print(f"✅ Bridge schema written to {OUTPUT}")
    print(f"   Total rules: {len(all_rules)}")
    print(f"   Deterministic: {stats['deterministic']}")
    print(f"   Directive:     {stats['directive']}")
    print(f"\n   Deterministic check distribution:")
    for method in sorted(DETERMINISTIC_CHECKS):
        count = stats.get(f"det_{method}", 0)
        if count:
            print(f"     {method}: {count} cards")
    print(f"\n   Directive category distribution:")
    for cat in sorted(DIRECTIVE_CATEGORIES):
        count = stats.get(f"dir_{cat}", 0)
        if count:
            print(f"     {cat}: {count} cards")

    return bridge


def _build_directive_router(rules: list) -> dict:
    """
    Build the Directive Router — used by the Injection Cap.

    Organizes directives by:
    1. Framework → directives in that framework
    2. Category → directives of that category
    3. Page type → which categories apply
    4. Keyword index for similarity-based routing

    When a brief is triggered by deterministic failures, the router:
    - Selects directives from frameworks that have failing checks
    - Adds directives from categories relevant to the page type
    - Caps at ~5-8 directives (the Injection Cap)
    """
    by_framework = defaultdict(list)
    by_category = defaultdict(list)
    by_page_type = defaultdict(lambda: defaultdict(list))

    for rule in rules:
        if rule["track"] != "directive":
            continue
        fw = rule["framework"]
        cat = rule["inject"]["category"]
        card_id = rule["card_id"]

        # Framework index
        by_framework[fw].append(card_id)

        # Category index
        by_category[cat].append(card_id)

        # Page type → category mapping
        applies_to = DIRECTIVE_CATEGORIES[cat]["applies_to"]
        for pt in applies_to:
            by_page_type[pt][cat].append(card_id)

    # Build a quick-lookup: card_id → rule
    card_index = {r["card_id"]: r for r in rules}

    # Keyword index for similarity routing
    keyword_index = defaultdict(list)
    for rule in rules:
        if rule["track"] != "directive":
            continue
        content = rule["content"].lower()
        target = rule["target_entity"].lower()
        # Extract important keywords
        keywords = set(re.findall(r'\b[a-z]{4,}\b', content + " " + target))
        for kw in keywords:
            keyword_index[kw].append(rule["card_id"])

    return {
        "by_framework": {fw: sorted(ids) for fw, ids in by_framework.items()},
        "by_category": {cat: sorted(ids) for cat, ids in by_category.items()},
        "by_page_type": {
            pt: {cat: sorted(ids) for cat, ids in cats.items()}
            for pt, cats in by_page_type.items()
        },
        "keyword_index_size": len(keyword_index),
        "card_index": {
            cid: {
                "content": r["content"][:100],
                "framework": r["framework"],
                "category": r.get("inject", {}).get("category", ""),
            }
            for cid, r in card_index.items()
            if r["track"] == "directive"
        },
    }


if __name__ == "__main__":
    main()
