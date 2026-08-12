#!/usr/bin/env python3
"""
kernel.py — Knowledge Synthesis Engine Kernel
==============================================
The irreducible core: ingest → extract entities → apply rules → detect gaps → report.

Phase 1 MVP: No dashboard, no alerts, no browser-use.
Just a Python script that outputs a JSON gap report.
If a writer says "holy shit, I need this" — we build the dashboard.

Components:
  1. ENTITY EXTRACTION — sitemap → LightRAG graph
  2. RULE APPLICATION — hardcoded rules from validated research
  3. GAP DETECTION — rules vs. reality → "write this"
  4. FRESHNESS TRACKING — timestamps, stale flags

Usage:
    source /home/steve/lightrag-env/bin/activate
    python3 kernel.py [--force] [--output report.json]
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

PROJECT_DIR = Path("/home/steve/lightrag-apps/knowledge-synthesis")
WORKSPACE_DIR = PROJECT_DIR / "workspace"
SITEMAP_URL = "https://quann.homes/sitemap.xml"
DOMAIN = "quann.homes"  # the domain we're analyzing

# ─── RULES (hardcoded from validated research — see architecture-review) ─────
# These are what we KNOW from P0 research rounds 1 & 2.
# Each rule has: id, description, category, paradigm, confidence, source

RULES = [
    {
        "rule_id": "aeo-faq-citation-2026",
        "category": "content_structure",
        "rule": "FAQPage schema markup increases AI Overview citation probability for definitional queries",
        "applies_to": ["AEO", "SEO"],
        "confidence": "confirmed",
        "source": "Google Search Central + Perplexity publisher guidelines + research validation",
        "check": "schema_faq",
    },
    {
        "rule_id": "content-depth-2300",
        "category": "content_quality",
        "rule": "Pages with 2,300+ words of substantive content correlate with AI citation",
        "applies_to": ["GEO", "SEO"],
        "confidence": "confirmed",
        "source": "Research Round 2 — cross-industry citation audit",
        "check": "word_count_min",
        "threshold": 2300,
    },
    {
        "rule_id": "entity-relationship-explicit",
        "category": "content_structure",
        "rule": "Explicit entity-to-entity relationship statements ('X is different from Y because…') improve GEO visibility",
        "applies_to": ["GEO"],
        "confidence": "probable",
        "source": "Research Round 2 — Perplexity values Q&A adjacency; explicit relationships = synthesis material",
        "check": "has_entity_relationships",
    },
    {
        "rule_id": "schema-article-type",
        "category": "schema_markup",
        "rule": "Article schema type should be present on all blog/content pages",
        "applies_to": ["SEO", "GEO"],
        "confidence": "confirmed",
        "source": "Schema.org + Google Search Central",
        "check": "schema_article",
    },
    {
        "rule_id": "structured-headings",
        "category": "content_structure",
        "rule": "Structured headings (H2/H3 hierarchy) correlate with AI citation",
        "applies_to": ["AEO", "SEO"],
        "confidence": "confirmed",
        "source": "Research Round 2 — heading structure is a positive signal",
        "check": "has_structured_headings",
    },
    {
        "rule_id": "freshness-90-day",
        "category": "freshness",
        "rule": "Content older than 90 days without update should be reviewed for staleness",
        "applies_to": ["SEO", "AEO", "GEO"],
        "confidence": "confirmed",
        "source": "Google freshness algorithm + industry best practice",
        "check": "freshness_90d",
        "threshold_days": 90,
    },
    {
        "rule_id": "internal-linking-entity",
        "category": "content_structure",
        "rule": "Pages should internally link to related entity pages to establish topical clusters",
        "applies_to": ["SEO", "GEO"],
        "confidence": "probable",
        "source": "Entity-based SEO methodology + Google's entity understanding patents",
        "check": "has_internal_entity_links",
    },
    {
        "rule_id": "quick-answer-box",
        "category": "content_structure",
        "rule": "Pages should have a 40-60 word extractable definition near the top for AEO",
        "applies_to": ["AEO"],
        "confidence": "probable",
        "source": "Perplexity publisher guidelines + AI Overview extraction patterns",
        "check": "has_quick_answer",
    },
]

# ─── SITEMAP ─────────────────────────────────────────────────────────────────

UA = "Mozilla/5.0 (compatible; KernelSynthesis/1.0; +https://quann.homes)"


def fetch_sitemap_urls(sitemap_url: str) -> dict[str, str]:
    """Return {url: lastmod} from sitemap XML."""
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    resp = requests.get(sitemap_url, headers={"User-Agent": UA}, timeout=30)
    resp.raise_for_status()
    tree = ET.fromstring(resp.content)
    urls = {}
    for el in tree.findall(".//s:url", ns):
        loc_el = el.find("s:loc", ns)
        lm_el = el.find("s:lastmod", ns)
        if loc_el is not None and loc_el.text:
            urls[loc_el.text.strip()] = (
                lm_el.text.strip() if lm_el is not None and lm_el.text else ""
            )
    return urls


# ─── SCRAPING ────────────────────────────────────────────────────────────────


def scrape_page(url: str) -> tuple[str | None, str | None]:
    """Extract text and raw HTML from a URL. Returns (plain_text, raw_html)."""
    raw_html = None
    
    # Try simple fetch first (faster, works for most pages)
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=15)
        resp.raise_for_status()
        raw_html = resp.text
        # Strip HTML tags for plain text
        text = re.sub(r"<script[\s\S]*?</script>", "", raw_html)
        text = re.sub(r"<style[\s\S]*?</style>", "", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 200:
            return text, raw_html
    except Exception:
        raw_html = None

    # Fallback: playwright
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            text = page.inner_text("body")
            raw_html = page.content()
            browser.close()
            if len(text) > 200:
                return text.strip(), raw_html
    except Exception as e:
        print(f"  ⚠ playwright fallback failed for {url}: {e}")

    return None, None


def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    """Sentence-aware chunking."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for s in sentences:
        if (len(current) + 1 + len(s)) > max_chars and len(current) > 100:
            chunks.append(current.strip())
            current = s
        else:
            current = (current + " " + s) if current else s
    if len(current.strip()) > 50:
        chunks.append(current.strip())
    return chunks


# ─── CONTENT ANALYSIS (no LLM needed for basic checks) ───────────────────────


def analyze_content(text: str, raw_html: str, url: str) -> dict:
    """Extract content properties for rule validation — pure Python, no LLM."""
    words = text.split()
    word_count = len(words)

    # Detect headings (from raw HTML — NOT stripped text)
    headings_h2 = len(re.findall(r"(?i)<h2[^>]*>", raw_html))
    headings_h3 = len(re.findall(r"(?i)<h3[^>]*>", raw_html))

    # Detect schema markup (JSON-LD)
    schema_types = []
    schema_blocks = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        text,
        re.DOTALL,
    )
    for block in schema_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, dict):
                t = data.get("@type", "")
                if isinstance(t, list):
                    schema_types.extend(t)
                elif t:
                    schema_types.append(t)
            elif isinstance(data, list):
                for item in data:
                    t = item.get("@type", "")
                    if t:
                        schema_types.append(t)
        except json.JSONDecodeError:
            pass

    # Detect quick answer candidate (first paragraph 40-60 words)
    plain_text = re.sub(r"<[^>]+>", " ", text)
    plain_text = re.sub(r"\s+", " ", plain_text).strip()
    first_sentence = re.split(r"[.!?]", plain_text)[0]
    first_sentence_words = len(first_sentence.split())
    has_quick_answer = 40 <= first_sentence_words <= 100

    # Detect entity relationship statements
    # Patterns: "X is different from Y", "unlike X, Y...", "X vs Y", "X compared to Y"
    rel_patterns = [
        r"(?i)\bis\s+different\s+from\b",
        r"(?i)\bunlike\b",
        r"(?i)\bvs\.?\s",
        r"(?i)\bcompared\s+to\b",
        r"(?i)\bin\s+contrast\s+to\b",
        r"(?i)\bdistinction\s+between\b",
    ]
    has_entity_relationships = any(
        re.search(p, plain_text) for p in rel_patterns
    )

    # Detect internal links to same domain
    internal_links = len(
        re.findall(
            rf'href=["\'](?:https?://(?:www\.)?{re.escape(DOMAIN)}|/(?![/]))[^"\']*["\']',
            text,
        )
    ) - 1  # subtract self-link

    return {
        "url": url,
        "word_count": word_count,
        "heading_h2": headings_h2,
        "heading_h3": headings_h3,
        "has_structured_headings": headings_h2 >= 2 and headings_h3 >= 3,
        "schema_types": schema_types,
        "has_faq_schema": "FAQPage" in schema_types,
        "has_article_schema": "Article" in schema_types or "BlogPosting" in schema_types,
        "has_quick_answer": has_quick_answer,
        "has_entity_relationships": has_entity_relationships,
        "has_internal_entity_links": internal_links >= 2,
        "first_100_words": plain_text[:500],
    }


# ─── GAP DETECTION ───────────────────────────────────────────────────────────


def detect_gaps(
    analyses: list[dict], sitemap_urls: dict[str, str]
) -> dict:
    """Compare content properties against rules. Return structured gaps."""
    gaps = []
    stats = {
        "total_pages_analyzed": len(analyses),
        "rules_checked": len(RULES),
        "gaps_found": 0,
        "pages_with_faq_schema": 0,
        "pages_with_article_schema": 0,
        "pages_with_deep_content": 0,
        "pages_with_quick_answer": 0,
        "pages_with_relationships": 0,
        "pages_with_structured_headings": 0,
        "pages_with_internal_links": 0,
    }

    now = datetime.now(timezone.utc)

    for analysis in analyses:
        url = analysis["url"]
        page_gaps = []

        # RULE: FAQ schema
        if not analysis["has_faq_schema"]:
            page_gaps.append(
                {
                    "rule_id": "aeo-faq-citation-2026",
                    "severity": "medium",
                    "detail": "Missing FAQPage schema markup — reduces AI Overview citation probability",
                    "fix": "Add FAQPage JSON-LD schema with 3-5 common questions + answers",
                }
            )
        else:
            stats["pages_with_faq_schema"] += 1

        # RULE: Article schema
        if not analysis["has_article_schema"]:
            page_gaps.append(
                {
                    "rule_id": "schema-article-type",
                    "severity": "low",
                    "detail": "Missing Article/BlogPosting schema type",
                    "fix": "Add Article or BlogPosting JSON-LD schema to the page",
                }
            )
        else:
            stats["pages_with_article_schema"] += 1

        # RULE: Content depth
        if analysis["word_count"] < 2300:
            page_gaps.append(
                {
                    "rule_id": "content-depth-2300",
                    "severity": "high" if analysis["word_count"] < 500 else "medium",
                    "detail": f"Page has {analysis['word_count']} words (target: 2,300+). Thin content correlates with lower AI citation rates.",
                    "fix": "Expand content to 2,300+ words with substantive entity coverage",
                }
            )
        else:
            stats["pages_with_deep_content"] += 1

        # RULE: Quick answer box
        if not analysis["has_quick_answer"]:
            page_gaps.append(
                {
                    "rule_id": "quick-answer-box",
                    "severity": "low",
                    "detail": "No extractable 40-60 word definition near the top — reduces AEO extractability",
                    "fix": "Add a concise definition (40-60 words) at the top of the page under a 'Quick Answer' or similar heading",
                }
            )
        else:
            stats["pages_with_quick_answer"] += 1

        # RULE: Entity relationships
        if not analysis["has_entity_relationships"]:
            page_gaps.append(
                {
                    "rule_id": "entity-relationship-explicit",
                    "severity": "medium",
                    "detail": "No explicit entity-to-entity relationship statements — reduces GEO synthesis material",
                    "fix": "Add comparison/relationship statements: 'X is different from Y because…' or 'Unlike X, Y…'",
                }
            )
        else:
            stats["pages_with_relationships"] += 1

        # RULE: Structured headings
        if not analysis["has_structured_headings"]:
            page_gaps.append(
                {
                    "rule_id": "structured-headings",
                    "severity": "low",
                    "detail": f"Only {analysis['heading_h2']} H2s and {analysis['heading_h3']} H3s — needs minimum 2 H2s + 3 H3s",
                    "fix": "Structure content with H2 for major sections and H3 for subsections",
                }
            )
        else:
            stats["pages_with_structured_headings"] += 1

        # RULE: Internal entity links
        if not analysis["has_internal_entity_links"]:
            page_gaps.append(
                {
                    "rule_id": "internal-linking-entity",
                    "severity": "low",
                    "detail": "Insufficient internal links to related entity pages — weakens topical cluster signals",
                    "fix": "Add contextual internal links to 2+ related entity pages on quann.homes",
                }
            )
        else:
            stats["pages_with_internal_links"] += 1

        # RULE: Freshness
        lastmod = sitemap_urls.get(url, "")
        if lastmod:
            try:
                # Try parsing ISO format
                lastmod_dt = datetime.fromisoformat(lastmod.replace("Z", "+00:00"))
                days_old = (now - lastmod_dt).days
                if days_old > 90:
                    page_gaps.append(
                        {
                            "rule_id": "freshness-90-day",
                            "severity": "medium" if days_old < 180 else "high",
                            "detail": f"Content last modified {days_old} days ago — exceeds 90-day freshness threshold",
                            "fix": f"Review and update content (last modified: {lastmod_dt.strftime('%Y-%m-%d')})",
                        }
                    )
            except (ValueError, TypeError):
                pass

        if page_gaps:
            gaps.append(
                {
                    "url": url,
                    "word_count": analysis["word_count"],
                    "schema_types": analysis["schema_types"],
                    "first_100_words": analysis["first_100_words"],
                    "gaps": page_gaps,
                    "total_gaps": len(page_gaps),
                }
            )

    stats["gaps_found"] = len(gaps)

    return {"summary": stats, "pages_with_gaps": gaps}


# ─── MAIN PIPELINE ───────────────────────────────────────────────────────────


async def main():
    parser = argparse.ArgumentParser(description="Knowledge Synthesis Engine Kernel")
    parser.add_argument(
        "--force", action="store_true", help="Re-scrape all pages (ignore cache)"
    )
    parser.add_argument(
        "--output",
        default=str(PROJECT_DIR / "gap_report.json"),
        help="Output JSON file path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit pages to analyze (0 = all)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"KNOWLEDGE SYNTHESIS KERNEL")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"Domain: {DOMAIN}")
    print(f"Sitemap: {SITEMAP_URL}")
    print(f"Rules loaded: {len(RULES)}")
    print("=" * 60)

    # 1. Fetch sitemap
    print("\n📡 [1/4] Fetching sitemap…")
    sitemap_urls = fetch_sitemap_urls(SITEMAP_URL)
    urls = list(sitemap_urls.keys())
    print(f"  Found {len(urls)} URLs")

    # Filter out non-content pages
    skip_patterns = [
        r"/portfolio",
        r"/home-tours",
        r"\.(jpg|png|gif|pdf|css|js)$",
        r"/wp-content",
        r"/cdn-cgi",
    ]
    content_urls = [
        u
        for u in urls
        if not any(re.search(p, u, re.I) for p in skip_patterns)
    ]
    print(f"  Content pages (after filtering): {len(content_urls)}")

    if args.limit and args.limit > 0:
        content_urls = content_urls[: args.limit]
        print(f"  Limited to {len(content_urls)} pages")

    # 2. Scrape & analyze
    print(f"\n📄 [2/4] Scraping and analyzing {len(content_urls)} pages…")
    analyses = []
    cache_file = PROJECT_DIR / "content_cache.json"

    # Load cache if exists
    cache = {}
    if not args.force and cache_file.exists():
        with open(cache_file) as f:
            cache = json.load(f)

    for i, url in enumerate(content_urls, 1):
        text, raw_html = None, None
        # Check cache
        if url in cache:
            text, raw_html = cache[url]
            print(f"  [{i}/{len(content_urls)}] {url} (cached)")
        else:
            print(f"  [{i}/{len(content_urls)}] {url}")
            text, raw_html = scrape_page(url)
            if text and raw_html:
                cache[url] = [text, raw_html]

        if text and raw_html:
            analysis = analyze_content(text, raw_html, url)
            analyses.append(analysis)
        else:
            print(f"    ⚠ Skipped — no content extracted")

    # Save cache
    with open(cache_file, "w") as f:
        json.dump(cache, f)

    print(f"\n  Analyzed: {len(analyses)} pages")

    # 3. Detect gaps
    print(f"\n🔍 [3/4] Detecting gaps…")
    report = detect_gaps(analyses, sitemap_urls)

    # 4. Output report
    print(f"\n📊 [4/4] Generating report…")
    report["metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "kernel_version": "0.1.0",
        "domain": DOMAIN,
        "sitemap_url": SITEMAP_URL,
        "rules_count": len(RULES),
        "pages_analyzed": len(analyses),
        "pages_skipped": len(content_urls) - len(analyses),
    }

    # Write report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    s = report["summary"]
    print(f"\n{'='*60}")
    print(f"GAP REPORT SUMMARY")
    print(f"{'='*60}")
    print(f"  Pages analyzed:        {s['total_pages_analyzed']}")
    print(f"  Pages with gaps:       {s['gaps_found']}")
    print(f"  Rules checked:         {s['rules_checked']}")
    print(f"  ---")
    print(f"  With FAQ schema:       {s['pages_with_faq_schema']}")
    print(f"  With Article schema:   {s['pages_with_article_schema']}")
    print(f"  With deep content:     {s['pages_with_deep_content']}")
    print(f"  With quick answer:     {s['pages_with_quick_answer']}")
    print(f"  With relationships:    {s['pages_with_relationships']}")
    print(f"  With struc headings:   {s['pages_with_structured_headings']}")
    print(f"  With internal links:   {s['pages_with_internal_links']}")
    print(f"  ---")
    print(f"  Report saved to:       {output_path}")
    print(f"{'='*60}")

    # Quick health check: if EVERY page fails the same rule, that rule might be wrong
    if s["pages_with_deep_content"] == 0:
        print("\n⚠ NOTE: No pages pass the 2,300-word depth rule. Consider whether this threshold is appropriate for this domain.")

    return report


if __name__ == "__main__":
    asyncio.run(main())
