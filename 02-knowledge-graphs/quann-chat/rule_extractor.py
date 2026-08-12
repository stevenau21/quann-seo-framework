#!/usr/bin/env python3
"""
Rule Extractor Pipeline — Intelligence Layer Core

Fetches methodology content from SEO sources and extracts structured,
testable rules via LLM. Merges into the shared rules_inventory.json.

Usage:
    python3 rule_extractor.py --url https://backlinko.com/on-page-seo --source "Backlinko" --type practitioner_research
    python3 rule_extractor.py --batch                           # process all configured sources
    python3 rule_extractor.py --list                            # show configured sources

Architecture: This is the Intelligence Layer's primary input pipeline.
Every source → fetch → LLM extract → validate → merge into inventory.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# Config
RULES_FILE = Path("/home/steve/lightrag-apps/knowledge-synthesis/rules_inventory.json")
METHODOLOGY_DIR = Path("/home/steve/lightrag-apps/knowledge-synthesis/methodology/")
OLLAMA_URL = "http://192.168.4.148:11434"
MODEL = "gemma4:31b-cloud"

# Pre-configured sources (add more here as you discover them)
SOURCES = [
    {
        "name": "Google Search Central - SEO Starter Guide",
        "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide",
        "type": "official_documentation",
    },
    {
        "name": "Backlinko - On-Page SEO Guide",
        "url": "https://backlinko.com/on-page-seo",
        "type": "practitioner_research",
    },
    {
        "name": "Google Search Central - Article Schema",
        "url": "https://developers.google.com/search/docs/appearance/structured-data/article",
        "type": "official_documentation",
    },
    {
        "name": "Google Search Central - FAQ Schema",
        "url": "https://developers.google.com/search/docs/appearance/structured-data/faqpage",
        "type": "official_documentation",
    },
]

# ── Extraction prompt ──

EXTRACTION_PROMPT = """You are an SEO methodology analyst. Your job is to extract structured, TESTABLE content rules from SEO methodology documents.

Output ONLY a valid JSON array. Each rule must have these fields:

- rule_id: string (unique kebab-case, e.g. "seo-title-length")
- category: string (one of: metadata|schema|url_structure|linking|content_structure|content_depth|content_quality|entity_coverage|conversion|mobile|ux|technical|local_seo|positioning|images)
- rule: string (PRECISE, testable statement. NOT vague philosophy.)
- source_type: string (official_documentation|practitioner_research|academic|observed_behavior)
- source_name: string
- source_url: string
- confidence: string (confirmed|probable|speculative)
- applies_to: array of strings (blog_post|service|homepage|about|legal|all)
- check_method: string (specific verification method name)
- priority: string (high|medium|low)
- principle: string (WHY this rule matters — 1 sentence)

CRITICAL: Rules must be directly TESTABLE against a single webpage's HTML and content. For example:
- GOOD: "Page must have FAQPage schema markup with at least 3 Question/Answer pairs"
- GOOD: "Title tag must be between 50-60 characters in length"
- GOOD: "Primary keyword must appear within the first 100 words of body content"
- BAD: "Content should be high quality"
- BAD: "Optimize for user experience"

Extract 5-15 rules from the methodology below. Output ONLY the JSON array, no other text.

METHODOLOGY CONTENT:
{content}"""

# ── Merging logic ──

def load_rules():
    if RULES_FILE.exists():
        with open(RULES_FILE) as f:
            return json.load(f)
    return []


def save_rules(rules):
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_FILE, 'w') as f:
        json.dump(rules, f, indent=2)


def merge_rules(existing, new_rules):
    """Merge new rules into inventory. Dedup by rule_id. Update if same ID but newer."""
    by_id = {r['rule_id']: r for r in existing}
    
    for rule in new_rules:
        rid = rule.get('rule_id', '')
        if not rid:
            # Generate an ID
            rid = f"rule-{len(by_id)+1:03d}"
            rule['rule_id'] = rid
        
        # Add timestamps
        now = datetime.now(timezone.utc).isoformat()
        if rid in by_id:
            rule['updated'] = now
            if 'added' not in rule:
                rule['added'] = by_id[rid].get('added', now)
        else:
            rule['added'] = now
            rule['updated'] = now
        
        by_id[rid] = rule
    
    return sorted(by_id.values(), key=lambda r: r['rule_id'])


# ── Fetching ──

def fetch_page(url):
    """Fetch a URL and extract readable text."""
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-sL', '--max-time', '60', url],
            capture_output=True, text=True, timeout=90
        )
        html = result.stdout
    except Exception as e:
        print(f"Fetch error: {e}")
        return ""

    # Strip scripts, styles, nav
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'&[a-z]+;', ' ', html)
    html = re.sub(r'\s+', ' ', html)
    
    # Truncate for LLM context window
    return html[:12000]


def extract_rules_via_llm(content, source_name, source_type, source_url):
    """Send methodology content to LLM and get structured rules back."""
    prompt = EXTRACTION_PROMPT.format(content=content)
    
    import subprocess
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    })
    
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '180', f'{OLLAMA_URL}/api/generate', '-d', payload],
            capture_output=True, text=True, timeout=200
        )
        response = json.loads(result.stdout)
        text = response.get('response', '')
    except Exception as e:
        print(f"LLM error: {e}")
        return []
    
    # Extract JSON array from response
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if not m:
        print(f"  No JSON array in LLM response. Raw: {text[:300]}")
        return []
    
    try:
        raw_rules = json.loads(m.group())
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return []
    
    # Ensure all required fields
    valid_rules = []
    for r in raw_rules:
        r.setdefault('source_type', source_type)
        r.setdefault('source_name', source_name)
        r.setdefault('source_url', source_url)
        r.setdefault('confidence', 'probable')
        r.setdefault('applies_to', ['all'])
        r.setdefault('check_method', 'manual')
        r.setdefault('priority', 'medium')
        r.setdefault('principle', r.get('rule', ''))
        valid_rules.append(r)
    
    return valid_rules


# ── Main commands ──

def process_source(source):
    """Fetch + extract rules from a single source."""
    print(f"\n{'='*60}")
    print(f"Processing: {source['name']}")
    print(f"URL: {source['url']}")
    
    print("  Fetching...")
    content = fetch_page(source['url'])
    
    if not content or len(content) < 500:
        print(f"  ⚠️  Content too short ({len(content)} chars). Skipping.")
        return []
    
    print(f"  Got {len(content)} chars. Extracting rules via {MODEL}...")
    rules = extract_rules_via_llm(
        content,
        source['name'],
        source['type'],
        source['url'],
    )
    
    print(f"  ✅ Extracted {len(rules)} rules")
    for r in rules:
        print(f"    - {r.get('rule_id')}: {r.get('rule')[:70]}...")
    
    return rules


def cmd_batch():
    """Process all configured sources."""
    existing = load_rules()
    print(f"Loaded {len(existing)} existing rules from inventory.")
    
    all_new = []
    for source in SOURCES:
        new_rules = process_source(source)
        all_new.extend(new_rules)
        time.sleep(1)  # Be gentle
    
    if all_new:
        updated = merge_rules(existing, all_new)
        save_rules(updated)
        added = len(updated) - len(existing)
        updated_count = len(all_new) - added
        print(f"\n{'='*60}")
        print(f"✅ MERGED: {len(updated)} total rules (added {added}, updated {updated_count})")
        print(f"Saved to {RULES_FILE}")
    else:
        print("\n⚠️  No new rules extracted.")


def cmd_single(url, name, source_type):
    """Process a single URL."""
    source = {"name": name, "url": url, "type": source_type}
    new_rules = process_source(source)
    
    if new_rules:
        existing = load_rules()
        updated = merge_rules(existing, new_rules)
        save_rules(updated)
        print(f"\n✅ Saved {len(updated)} rules to {RULES_FILE}")


def cmd_list():
    """Show configured sources."""
    existing = load_rules()
    print(f"Rules inventory: {len(existing)} rules in {RULES_FILE}\n")
    
    print("Configured sources:")
    for s in SOURCES:
        print(f"  • {s['name']} [{s['type']}]")
        print(f"    {s['url']}\n")


# ── CLI ──

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligence Layer Rule Extractor")
    parser.add_argument('--url', help='Single URL to extract rules from')
    parser.add_argument('--source', help='Source name (for --url)')
    parser.add_argument('--type', default='practitioner_research',
                       help='Source type: official_documentation|practitioner_research|academic')
    parser.add_argument('--batch', action='store_true', help='Process all configured sources')
    parser.add_argument('--list', action='store_true', help='List configured sources')
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list()
    elif args.batch:
        cmd_batch()
    elif args.url and args.source:
        cmd_single(args.url, args.source, args.type)
    else:
        parser.print_help()
