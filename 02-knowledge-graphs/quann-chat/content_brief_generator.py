#!/usr/bin/env python3
"""
Content Brief Generator — The Ignition Point of the Flywheel

Loads gap report, rule inventory, and contamination audit. Filters
contaminated entities. For a given page URL, generates a structured
multi-paradigm (SEO/AEO/GEO) content brief that a writer can immediately
act on.

Usage:
    python3 content_brief_generator.py --url https://quann.homes/blog/out-of-state-buyer-guide
    python3 content_brief_generator.py --url ... --output /path/to/brief.md
"""

import argparse
import json
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── Config ──
GAP_REPORT = Path("/home/steve/lightrag-apps/knowledge-synthesis/gap_report.json")
RULES_FILE = Path("/home/steve/lightrag-apps/knowledge-synthesis/rules_inventory.json")
AUDIT_FILE = Path("/home/steve/lightrag-apps/knowledge-synthesis/entity_audit_report.json")
OUTPUT_DIR = Path("/home/steve/lightrag-apps/knowledge-synthesis/briefs/")
OLLAMA_URL = "http://192.168.4.148:11434"
MODEL = "gemma4:31b-cloud"


def load_all():
    gap = json.loads(GAP_REPORT.read_text())
    rules = json.loads(RULES_FILE.read_text())
    audit = json.loads(AUDIT_FILE.read_text()) if AUDIT_FILE.exists() else {"findings": []}
    return gap, rules, audit


def contaminated_set(audit):
    return {f["entity_name"] for f in audit.get("findings", [])
            if f.get("severity") == "critical"}


def get_page(gap, url):
    """Get rule results, gaps, and entity names for a specific page."""
    pr = next((r for r in gap.get("rule_results", []) if r["url"] == url), None)
    if not pr:
        print(f"❌ URL not in gap report: {url}")
        sys.exit(1)

    page_gaps = [g for g in gap.get("gaps", []) if g.get("url") == url]

    pi = gap.get("page_inventory", {})
    entities = pi.get(url, {}).get("entities", []) if isinstance(pi, dict) else []

    return pr, page_gaps, entities


def failed_rules_detail(page_rules, rules):
    """Return full rule objects for each failed check."""
    by_id = {r["rule_id"]: r for r in rules}
    out = []
    for c in page_rules.get("rule_checks", []):
        if c["status"] == "fail":
            r = by_id.get(c["rule_id"], {})
            out.append({
                "rule_id": c["rule_id"], "rule_text": c["rule"],
                "detail": c["detail"], "priority": r.get("priority", "medium"),
                "principle": r.get("principle", ""), "category": r.get("category", ""),
            })
    out.sort(key=lambda r: (r["priority"] != "high", r["rule_id"]))
    return out


def missing_entities(page_gaps, existing, contaminated):
    """Core entities missing from this page, minus contamination."""
    core = {
        "Closing Costs", "Down Payment Assistance", "Home Inspection",
        "Mortgage Pre-Approval", "Buyer's Agent", "Katy", "Katy ISD",
        "Texas Property Tax", "Homeowners Insurance", "School Districts",
        "Out-of-State Buyer", "Relocation",
    }
    missing = core - set(existing) - contaminated
    for g in page_gaps:
        if g.get("type") == "entity_coverage_gap":
            missing |= set(g.get("missing_entities", []))
    missing -= contaminated
    return sorted(missing)


def generate(target_url):
    """Main generation pipeline."""
    gap, rules, audit = load_all()
    contaminated = contaminated_set(audit)

    page_rules, page_gaps, entities = get_page(gap, target_url)
    failed = failed_rules_detail(page_rules, rules)
    missing = missing_entities(page_gaps, entities, contaminated)

    compliance = page_rules.get("compliance_pct", 0)
    wc = page_rules.get("word_count", 0)
    ptype = page_rules.get("page_type", "blog_post")
    passed = page_rules.get("pass_count", 0)
    total_checks = page_rules.get("total_rules", len(failed))

    # ── Build LLM prompt ──
    clean_entities = sorted(set(entities) - contaminated)[:25]
    slug = target_url.replace("https://quann.homes/", "")

    failed_lines = "\n".join(
        f"- [{r['priority'].upper()}] **{r['rule_id']}**: {r['rule_text']}\n  → {r['detail']}\n  → Why: {r['principle']}"
        for r in failed
    )

    prompt = f"""You are a senior content strategist and real estate copywriter.
Create a detailed, actionable, WRITER-READY content brief for the following page.

## TARGET PAGE
URL: {target_url}
Type: {ptype}
Current Compliance: {compliance}% ({passed}/{total_checks} rules)
Current Word Count: {wc}

## CONTAMINATED ENTITIES (DO NOT USE — they are Framer template artifacts)
{chr(10).join(f"- {e}" for e in sorted(contaminated)[:30])}

## CURRENT PAGE ENTITIES (legitimate, can reference)
{chr(10).join(f"- {e}" for e in clean_entities[:20])}

## FAILED RULES (what the page is missing per SEO methodology)
{failed_lines}

## MISSING ENTITIES (must be covered)
{chr(10).join(f"- {e}" for e in missing[:20])}

## WRITER INSTRUCTIONS
Create a single page that a buyer relocating to Katy/Houston would bookmark.
Write in a warm, knowledgeable voice. Avoid jargon. Every section should
anticipate what a relocating buyer is anxious about and answer it directly.
IMPORTANT: Do NOT mention any CONTAMINATED entities.

## REQUIRED SECTIONS

### 1. Page Metadata
- Target Title Tag: [50-60 chars, include "Katy" or "Houston", include "Out-of-State" or "Relocating"]
- Meta Description: [140-160 chars, include keyword + CTA]
- URL Slug: [descriptive]

### 2. Quick Answer Box (AEO — 40-60 words)
"What should an out-of-state buyer know about buying a home in Katy, Texas?"
Write this as if extracted for voice assistant or AI Overview.

### 3. FAQ Section (3 questions, 150-200 words each)
Use these exact questions. These become FAQPage schema.
- Q1: "How is buying a home in Texas different from other states?"
- Q2: "What are closing costs for an out-of-state buyer in Katy?"
- Q3: "Can I get down payment assistance as a relocating buyer?"

### 4. Guide Body (SEO — 2,000-3,000 words)
Cover: Texas market (Katy-specific), step-by-step process, property tax differences,
mortgage pre-approval for out-of-state, home inspection for remote buyers,
Katy ISD schools, HOA realities, relocation timeline.
Include internal links to: steps-for-buying-first-home, texas-first-time-home-buyer-guide5

### 5. Entity Definitions (GEO)
For each missing entity, 2-3 sentences defining it and connecting to out-of-state buying.

### 6. Katy Local Context (GEO)
Market snapshot, what makes Katy different from Houston, master-planned communities
(Cinco Ranch, Firethorne, Cross Creek Ranch), commute reality.

### 7. Schema Markup
Include ACTUAL JSON-LD blocks (not placeholders) for:
- Article schema (datePublished, author: Quan Nguyen, headline)
- FAQPage schema (3 pairs)
- WebPage schema

Write the COMPLETE content brief now. Real FAQ answers. Real Quick Answer Box text.
Real schema JSON-LD. No lorem ipsum. No placeholders. This goes straight to a writer."""

    print(f"\n🧠 Generating brief via {MODEL} (this may take 60-120s)...")
    result = subprocess.run(
        ['curl', '-s', '--max-time', '300', f'{OLLAMA_URL}/api/generate',
         '-d', json.dumps({"model": MODEL, "prompt": prompt, "stream": False})],
        capture_output=True, text=True, timeout=320
    )
    response = json.loads(result.stdout)
    body = response.get('response', '')
    if not body:
        print("❌ Empty LLM response")
        sys.exit(1)

    # ── Assemble final document ──
    now = datetime.now(timezone.utc).isoformat()
    high_cnt = sum(1 for r in failed if r['priority'] == 'high')
    med_cnt = sum(1 for r in failed if r['priority'] == 'medium')

    header = f"""# Content Brief: {slug}

> **Generated:** {now}
> **Target URL:** {target_url}
> **Page Type:** {ptype}
> **Current Compliance:** {compliance}% ({passed}/{total_checks} rules)
> **Current Word Count:** {wc}
> **Failed Rules:** {len(failed)} ({high_cnt} high, {med_cnt} medium)
> **Missing Entities:** {len(missing)}
> **Contaminated Entities Filtered:** {len(contaminated)}

---

## Gap Summary

### Failed Rules
{chr(10).join(f"- [{r['priority'].upper()}] **{r['rule_id']}**: {r['rule_text']} → {r['principle']}" for r in failed)}

### Missing Entities
{chr(10).join(f"- {e}" for e in missing[:20])}

---

{body}

---

*Brief generated by Knowledge Synthesis Engine. Source data: {GAP_REPORT}*
"""

    slug_safe = slug.replace("/", "-")
    out_path = OUTPUT_DIR / f"brief-{slug_safe}-{now[:10]}.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header)

    print(f"\n✅ Brief saved: {out_path}")
    print(f"   Total: {len(header)} chars")
    print(f"   Failed rules addressed: {len(failed)}")
    print(f"   Missing entities requested: {len(missing)}")
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Content Brief Generator")
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', help='Custom output path')
    args = parser.parse_args()
    generate(args.url)
