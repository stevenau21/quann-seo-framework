#!/usr/bin/env python3
"""
Knowledge Synthesis Kernel v2 — quann.homes stress test

Reads LightRAG workspace directly, maps docs to URLs via ingest order,
detects template contamination entities, applies content rules, produces gap report.
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

WORKSPACE = Path("/home/steve/lightrag-apps/quann-chat/workspace")
STATE_FILE = Path("/home/steve/lightrag-apps/quann-chat/ingest_state.json")
OUTPUT = Path("/home/steve/lightrag-apps/knowledge-synthesis/gap_report.json")

# ── Known sitemap URLs in ingest order ──
SITEMAP_ORDER = [
    "https://quann.homes/",
    "https://quann.homes/portfolio-dark-work",
    "https://quann.homes/home-tours",
    "https://quann.homes/aboutme",
    "https://quann.homes/portfolio-dark-home",
    "https://quann.homes/texas-real-estate-commission-information-about-brokerage-services",
    "https://quann.homes/disclosure",
    "https://quann.homes/blog",
    "https://quann.homes/privacy-policy",
    "https://quann.homes/terms-of-service",
    "https://quann.homes/cookie-policy",
    "https://quann.homes/portfolio-dark-work/lightric-motors",
    "https://quann.homes/portfolio-dark-work/positive-energy",
    "https://quann.homes/portfolio-dark-work/xiong-wall",
    "https://quann.homes/portfolio-dark-work/hideaway",
    "https://quann.homes/portfolio-dark-work/louis-martin",
    "https://quann.homes/portfolio-dark-work/califfo",
    "https://quann.homes/portfolio-dark-work/froadmile",
    "https://quann.homes/portfolio-dark-work/westbury",
    "https://quann.homes/blog/texas-first-time-home-buyer-guide5",
    "https://quann.homes/blog/steps-for-buying-your-first-home",
    "https://quann.homes/blog/out-of-state-buyer-guide",
]

TEMPLATE_URLS = {url for url in SITEMAP_ORDER if "portfolio-dark-work/" in url}
TEMPLATE_URLS |= {
    "https://quann.homes/portfolio-dark-work",
    "https://quann.homes/portfolio-dark-home",
}

REAL_URLS = set(SITEMAP_ORDER) - TEMPLATE_URLS

PAGE_CATEGORIES = {
    "https://quann.homes/": "homepage",
    "https://quann.homes/aboutme": "about",
    "https://quann.homes/blog": "blog_index",
    "https://quann.homes/home-tours": "service",
    "https://quann.homes/blog/texas-first-time-home-buyer-guide5": "blog_post",
    "https://quann.homes/blog/steps-for-buying-your-first-home": "blog_post",
    "https://quann.homes/blog/out-of-state-buyer-guide": "blog_post",
    "https://quann.homes/texas-real-estate-commission-information-about-brokerage-services": "legal",
    "https://quann.homes/disclosure": "legal",
    "https://quann.homes/privacy-policy": "policy",
    "https://quann.homes/terms-of-service": "policy",
    "https://quann.homes/cookie-policy": "policy",
}

RULES_FILE = Path("/home/steve/lightrag-apps/knowledge-synthesis/rules_inventory.json")


def load_rules():
    """Load rules from the Intelligence Layer inventory. Falls back to hardcoded defaults."""
    if RULES_FILE.exists():
        with open(RULES_FILE) as f:
            rules = json.load(f)
        # Filter to confirmed/probable rules only (skip speculative/contested)
        active = [r for r in rules if r.get("confidence") in ("confirmed", "probable")]
        print(f"  Loaded {len(active)}/{len(rules)} active rules from {RULES_FILE}")
        return active
    else:
        print(f"  ⚠️  {RULES_FILE} not found — using kernel defaults")
        return DEFAULT_RULES


# ── Default fallback rules (used only if inventory is missing) ──
DEFAULT_RULES = [
    {"rule_id": "RE-FAQ-SCHEMA", "rule": "Pages answering buyer questions should have FAQPage schema markup",
     "category": "content_structure", "applies_to": ["service", "blog_post", "homepage"],
     "check": "schema_faq", "confidence": "confirmed"},
    {"rule_id": "RE-ARTICLE-SCHEMA", "rule": "Blog posts should have Article schema markup",
     "category": "schema", "applies_to": ["blog_post"],
     "check": "schema_article", "confidence": "confirmed"},
    {"rule_id": "RE-DEEP-CONTENT", "rule": "Content pages should exceed 1500 words for topical authority",
     "category": "content_depth", "applies_to": ["blog_post", "service"],
     "check": "word_count_gt_1500", "confidence": "probable"},
    {"rule_id": "RE-INTERNAL-LINKS", "rule": "Every page should internally link to at least 3 other quann.homes pages",
     "category": "seo", "applies_to": ["blog_post", "service", "about"],
     "check": "internal_links_ge_3", "confidence": "probable"},
    {"rule_id": "RE-ENTITY-CONTEXT", "rule": "Content mentioning 'Texas' should also mention relevant cities (Houston, Austin, Dallas, Katy)",
     "category": "entity_coverage", "applies_to": ["blog_post", "service", "homepage"],
     "check": "texas_city_coverage", "confidence": "confirmed"},
    {"rule_id": "RE-BUYER-CLARITY", "rule": "Content should clearly state Quan represents buyers when discussing buyer topics",
     "category": "positioning", "applies_to": ["blog_post", "homepage", "about"],
     "check": "buyer_positioning", "confidence": "confirmed"},
    {"rule_id": "RE-CONTACT-PATH", "rule": "Every page should have a clear path to contact/consultation",
     "category": "conversion", "applies_to": ["blog_post", "service", "about", "homepage"],
     "check": "contact_path", "confidence": "confirmed"},
    {"rule_id": "RE-KATY-LOCAL", "rule": "Katy-local pages should mention Katy-specific market context",
     "category": "local_seo", "applies_to": ["blog_post", "homepage"],
     "check": "katy_context", "confidence": "probable"},
]

# RULES is loaded at module level
RULES = load_rules()


def load_workspace():
    with open(WORKSPACE / "kv_store_full_entities.json") as f:
        entities = json.load(f)
    with open(WORKSPACE / "kv_store_full_relations.json") as f:
        relations = json.load(f)
    with open(WORKSPACE / "kv_store_doc_status.json") as f:
        doc_status = json.load(f)
    with open(WORKSPACE / "kv_store_full_docs.json") as f:
        full_docs = json.load(f)
    return entities, relations, doc_status, full_docs


def build_doc_map(doc_status):
    """Map doc_id → URL by matching ingest order against sitemap."""
    # Sort track_ids by timestamp (extracted from track_id)
    tracked = [(doc_id, v.get("track_id", ""), v.get("status", "?"))
               for doc_id, v in doc_status.items()]
    tracked.sort(key=lambda x: x[1].split("_")[2] if len(x[1].split("_")) > 2 else "0")

    doc_map = {}
    for i, (doc_id, track_id, status) in enumerate(tracked):
        if i < len(SITEMAP_ORDER):
            url = SITEMAP_ORDER[i]
            category = "template" if url in TEMPLATE_URLS else "real"
            doc_map[doc_id] = {
                "url": url,
                "category": category,
                "page_type": PAGE_CATEGORIES.get(url, "unknown"),
                "track_id": track_id,
                "status": status,
            }
        else:
            # Shouldn't happen, but handle gracefully
            doc_map[doc_id] = {
                "url": f"unknown_{i}",
                "category": "unknown",
                "page_type": "unknown",
                "track_id": track_id,
                "status": status,
            }
    return doc_map


def build_page_map(doc_map, entities, relations, full_docs):
    """Build page → {entities, relations, content, metadata}."""
    page_map = {}

    for doc_id, info in doc_map.items():
        url = info["url"]
        doc_status_info = doc_map[doc_id]
        doc_entities = entities.get(doc_id, {})
        doc_relations = relations.get(doc_id, {})
        doc_data = full_docs.get(doc_id, {})

        entity_names = doc_entities.get("entity_names", [])
        relation_pairs = doc_relations.get("relation_pairs", [])
        content = doc_data.get("content", "")

        word_count = len(content.split()) if content else 0
        created = doc_data.get("create_time")
        if created and isinstance(created, (int, float)):
            created = datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
        updated = doc_data.get("update_time")
        if updated and isinstance(updated, (int, float)):
            updated = datetime.fromtimestamp(updated, tz=timezone.utc).isoformat()

        page_map[url] = {
            "doc_id": doc_id,
            "category": info["category"],
            "page_type": info["page_type"],
            "status": info["status"],
            "entity_names": entity_names,
            "entity_count": len(entity_names),
            "relation_pairs": relation_pairs,
            "relation_count": len(relation_pairs),
            "word_count": word_count,
            "content_preview": content[:500].replace("\n", " "),
            "content_full": content,
            "created_at": created,
            "updated_at": updated,
        }

    return page_map


def detect_contamination(page_map):
    """Template-only entities vs. shared entities."""
    template_entities = set()
    real_entities = set()

    for url, page in page_map.items():
        es = set(page["entity_names"])
        if page["category"] == "template":
            template_entities |= es
        elif page["category"] == "real":
            real_entities |= es

    pure = sorted(template_entities - real_entities)
    merged = sorted(template_entities & real_entities)
    ratio = len(pure) / max(len(template_entities), 1)
    severity = ("CRITICAL" if len(pure) > 20
                else "HIGH" if len(pure) > 10
                else "MODERATE" if len(pure) > 5
                else "LOW")

    return {
        "template_page_count": sum(1 for p in page_map.values() if p["category"] == "template"),
        "real_page_count": sum(1 for p in page_map.values() if p["category"] == "real"),
        "total_template_entities": len(template_entities),
        "total_real_entities": len(real_entities),
        "pure_contamination": pure,
        "pure_contamination_count": len(pure),
        "merged_contamination": merged,
        "merged_contamination_count": len(merged),
        "contamination_ratio": round(ratio, 3),
        "severity": severity,
    }


def extract_typed_entities(page_map):
    """Query LightRAG API for typed entities, fall back to workspace."""
    import requests
    all_entities = defaultdict(lambda: {"pages": [], "types": set(), "descriptions": set()})

    # Try API
    try:
        resp = requests.post(
            "http://localhost:8011/query",
            json={"query": "list every single entity and its type from the knowledge graph as JSON",
                  "mode": "local", "only_need_context": True},
            timeout=120,
        )
        if resp.status_code == 200:
            data = resp.json()
            response_text = data.get("response", "")
            json_blocks = re.findall(r'\{[^{}]*"entity"[^{}]*\}', response_text)
            for block in json_blocks:
                try:
                    obj = json.loads(block)
                    if "entity" in obj:
                        name = obj["entity"]
                        etype = obj.get("type", "unknown")
                        desc = obj.get("description", "")
                        all_entities[name]["types"].add(etype)
                        all_entities[name]["descriptions"].add(desc)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"  ⚠️ API query failed: {e} — using workspace entities only")

    # Augment with workspace entity names
    for url, page in page_map.items():
        for entity_name in page["entity_names"]:
            all_entities[entity_name]["pages"].append(url)

    result = []
    for name, info in all_entities.items():
        pages_set = set(info["pages"])
        result.append({
            "entity_name": name,
            "types": sorted(info["types"]),
            "descriptions": sorted(info["descriptions"]),
            "pages": sorted(pages_set),
            "page_count": len(pages_set),
            "contamination": any(page_map.get(p, {}).get("category") == "template" for p in pages_set),
            "real_only": all(page_map.get(p, {}).get("category") == "real" for p in pages_set),
        })

    return sorted(result, key=lambda e: -e["page_count"])


def check_rules(page_map, bridge=None):
    """Apply rules to each real page. If bridge is provided, also runs
    Koray Gubur Tier 1 deterministic checks via the Bifurcated RuleBridge."""
    rule_results = []

    for url, page in page_map.items():
        if page["category"] != "real":
            continue

        content = page.get("content_full", "")
        entities = page["entity_names"]
        word_count = page["word_count"]

        page_rules = []
        for rule in RULES:
            if page["page_type"] not in rule.get("applies_to", []):
                continue

            result = {"rule_id": rule["rule_id"], "rule": rule["rule"], "status": None, "detail": ""}
            rtype = rule.get("check") or rule.get("check_method", "")

            if rtype == "schema_faq":
                has_faq = bool(re.search(r'FAQ|faq|Frequently Asked|Question.*\?', content))
                result["status"] = "pass" if has_faq else "fail"
                result["detail"] = f"FAQ structure {'found' if has_faq else 'NOT found'}"

            elif rtype == "schema_article":
                has_article = bool(re.search(r'Article|article|BlogPosting|articleBody', content))
                result["status"] = "pass" if has_article else "fail"
                result["detail"] = f"Article schema {'found' if has_article else 'NOT found'}"

            elif rtype == "word_count_gt_1500":
                result["status"] = "pass" if word_count > 1500 else "fail"
                result["detail"] = f"Word count: {word_count} (need 1500+)"

            elif rtype == "internal_links_ge_3":
                internal = len(re.findall(r'quann\.homes', content))
                result["status"] = "pass" if internal >= 3 else "fail"
                result["detail"] = f"Internal links: {internal} (need 3+)"

            elif rtype == "texas_city_coverage":
                cities = ["Houston", "Austin", "Dallas", "Katy", "San Antonio"]
                found = [c for c in cities if c.lower() in content.lower()]
                result["status"] = "pass" if len(found) >= 2 else "fail"
                result["detail"] = f"TX cities: {found} (need 2+)"

            elif rtype == "buyer_positioning":
                buyer_terms = ["buyer", "buying", "buy a home", "purchaser"]
                found = [t for t in buyer_terms if t.lower() in content.lower()]
                result["status"] = "pass" if found else "fail"
                result["detail"] = f"Buyer terms: {found}"

            elif rtype == "contact_path":
                contact_terms = ["contact", "call", "schedule", "consult", "phone", "email"]
                found = [t for t in contact_terms if t.lower() in content.lower()]
                result["status"] = "pass" if found else "fail"
                result["detail"] = f"Contact terms: {found}"

            elif rtype == "katy_context":
                has_katy = "katy" in content.lower()
                result["status"] = "pass" if has_katy else "fail"
                result["detail"] = f"Katy context: {'present' if has_katy else 'missing'}"

            # ── New Intelligence Layer check types ──
            elif rtype == "char_count_title":
                # Check title tag length (approximate from content)
                title_match = re.search(r'#+\s*(.+?)(?:\n|$)', content)
                title = title_match.group(1) if title_match else ""
                tc = len(title)
                result["status"] = "pass" if 40 <= tc <= 70 else "fail"
                result["detail"] = f"Title chars: {tc} (target 50-60)"

            elif rtype == "char_count_meta_desc":
                # Approximate meta desc from first paragraph
                para = re.split(r'\n\n+', content)
                pd = para[1] if len(para) > 1 else content[:200]
                mc = len(pd)
                result["status"] = "pass" if mc <= 200 else "fail"
                result["detail"] = f"Meta desc estimate: {mc} chars"

            elif rtype == "keyword_in_title_front":
                title_match = re.search(r'#+\s*(.+?)(?:\n|$)', content)
                title = title_match.group(1) if title_match else ""
                # Check if key entity names appear in first 60 chars of title
                has_keyword = any(e.lower() in title[:60].lower() for e in entities[:5])
                result["status"] = "pass" if has_keyword else "fail"
                result["detail"] = f"Keyword in title front: {'yes' if has_keyword else 'no'}"

            elif rtype == "schema_present":
                has_schema = bool(re.search(r'(application/ld\+json|itemscope|itemtype)', content))
                result["status"] = "pass" if has_schema else "fail"
                result["detail"] = f"Schema markup: {'found' if has_schema else 'NOT found'}"

            elif rtype == "header_hierarchy":
                has_h1 = bool(re.search(r'#\s+', content))
                has_h2 = bool(re.search(r'##\s+', content))
                has_h3 = bool(re.search(r'###\s+', content))
                result["status"] = "pass" if has_h1 and has_h2 else "fail"
                result["detail"] = f"Headers: H1={'✓' if has_h1 else '✗'} H2={'✓' if has_h2 else '✗'} H3={'✓' if has_h3 else '✗'}"

            elif rtype == "keyword_in_first_100":
                words = content.split()[:100]
                first100 = ' '.join(words).lower()
                has_keyword = any(e.lower() in first100 for e in entities[:5])
                result["status"] = "pass" if has_keyword else "fail"
                result["detail"] = f"Keyword in first 100w: {'yes' if has_keyword else 'no'}"

            elif rtype == "entity_coverage":
                required = ["Buyer's Agent", "Closing Costs", "Down Payment Assistance",
                           "Home Inspection", "Mortgage Pre-Approval"]
                found = [e for e in required if e.lower() in content.lower()]
                result["status"] = "pass" if len(found) >= 3 else "fail"
                result["detail"] = f"Core entities covered: {len(found)}/5 ({', '.join(found) if found else 'none'})"

            elif rtype in ("information_gain", "readability_natural_language",
                          "mobile_responsive", "no_intrusive_interstitials",
                          "image_alt_present", "sitemap_submitted",
                          "descriptive_url_slug", "anchor_text_quality"):
                # Manual/visual checks — mark as unverified rather than fail
                result["status"] = "unverified"
                result["detail"] = "Requires manual/visual inspection"

            page_rules.append(result)

        # ── RuleBridge: Koray Gubur Tier 1 deterministic checks ──
        bridge_results = []
        if bridge:
            try:
                from rule_bridge import bridge_page_types as bpt
                bpage_type = bpt(page["page_type"])
                bridge_results = bridge.run_deterministic_checks(url, content, bpage_type)
                page_rules.extend(bridge_results)
            except ImportError:
                pass  # rule_bridge.py not available — skip

        passed = sum(1 for r in page_rules if r["status"] == "pass")
        total = len(page_rules)
        rule_results.append({
            "url": url,
            "page_type": page["page_type"],
            "entity_count": page["entity_count"],
            "word_count": word_count,
            "rule_checks": page_rules,
            "pass_count": passed,
            "fail_count": total - passed,
            "total_rules": total,
            "compliance_pct": round(100 * passed / max(total, 1), 1),
            "bridge_checks": len(bridge_results),
        })

    return rule_results


def compute_gaps(rule_results, page_map):
    """Compute content gaps from rule failures and structural analysis."""
    gaps = []

    # Rule gaps
    for pr in rule_results:
        for check in pr["rule_checks"]:
            if check["status"] == "fail":
                # Use rule priority from inventory, fall back to hardcoded check
                rule_priority = "medium"
                for r in RULES:
                    if r["rule_id"] == check["rule_id"]:
                        rule_priority = r.get("priority", "medium")
                        break
                gaps.append({
                    "type": "rule_gap",
                    "url": pr["url"],
                    "rule_id": check["rule_id"],
                    "rule": check["rule"],
                    "detail": check["detail"],
                    "severity": rule_priority,
                })

    # Entity coverage gaps
    important_entities = {
        "Buyer's Agent", "First-Time Home Buyer", "Texas Real Estate",
        "Katy", "Houston", "Home Buying Process", "Mortgage Pre-Approval",
        "Closing Costs", "Home Inspection", "Down Payment Assistance",
    }
    for url, page in page_map.items():
        if page["category"] != "real" or page["page_type"] not in ("blog_post", "service"):
            continue
        page_entities = set(page["entity_names"])
        missing = important_entities - page_entities
        if missing:
            gaps.append({
                "type": "entity_coverage_gap",
                "url": url,
                "page_type": page["page_type"],
                "missing_entities": sorted(missing),
                "missing_count": len(missing),
                "severity": "high" if len(missing) > 5 else "medium" if len(missing) > 2 else "low",
            })

    # Format gap
    blog_posts = [(url, p) for url, p in page_map.items() if p["page_type"] == "blog_post" and p["category"] == "real"]
    if blog_posts and all(p["word_count"] < 1500 for _, p in blog_posts):
        gaps.append({
            "type": "format_gap",
            "description": "No blog posts exceed 1500 words — all shallow content",
            "affected_pages": [url for url, _ in blog_posts],
            "severity": "high",
        })

    # Freshness gaps (content older than 90 days)
    now = time.time()
    for url, page in page_map.items():
        if page["category"] != "real":
            continue
        created = page.get("created_at")
        if created:
            try:
                ts = datetime.fromisoformat(created).timestamp()
                if now - ts > 90 * 86400:
                    gaps.append({
                        "type": "freshness_gap",
                        "url": url,
                        "detail": f"Content not refreshed in >90 days",
                        "severity": "medium",
                    })
            except (ValueError, TypeError):
                pass

    return gaps


def build_report(page_map, contamination, typed_entities, rule_results, gaps):
    """Assemble the full report."""
    real_pages = {u: p for u, p in page_map.items() if p["category"] == "real"}
    template_pages = {u: p for u, p in page_map.items() if p["category"] == "template"}

    total_checks = sum(r["total_rules"] for r in rule_results)
    total_pass = sum(r["pass_count"] for r in rule_results)
    total_fail = total_checks - total_pass

    all_entities = set()
    for p in page_map.values():
        all_entities |= set(p["entity_names"])

    return {
        "report_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "kernel_version": "2.1",
            "workspace": str(WORKSPACE),
        },
        "summary": {
            "total_pages": len(page_map),
            "real_pages": len(real_pages),
            "template_pages": len(template_pages),
            "total_entities_extracted": len(all_entities),
            "real_entities": len(set().union(*[set(p["entity_names"]) for p in real_pages.values()])),
            "template_entities": len(set().union(*[set(p["entity_names"]) for p in template_pages.values()])),
            "contamination_severity": contamination["severity"],
            "pure_contamination_count": contamination["pure_contamination_count"],
            "rule_compliance": f"{total_pass}/{total_checks} ({round(100*total_pass/max(total_checks,1),1)}%)",
            "total_gaps": len(gaps),
            "high_gaps": sum(1 for g in gaps if g["severity"] == "high"),
            "medium_gaps": sum(1 for g in gaps if g["severity"] == "medium"),
            "low_gaps": sum(1 for g in gaps if g["severity"] == "low"),
        },
        "contamination_analysis": contamination,
        "entity_inventory": typed_entities,
        "page_inventory": {url: {
            "category": p["category"],
            "page_type": p["page_type"],
            "entity_count": p["entity_count"],
            "word_count": p["word_count"],
            "entities": p["entity_names"],
            "relations": p["relation_pairs"],
        } for url, p in page_map.items()},
        "rule_results": rule_results,
        "gaps": sorted(gaps, key=lambda g: (
            0 if g["severity"] == "high" else 1 if g["severity"] == "medium" else 2,
            g.get("url", ""),
        )),
    }


# ── Main ──

def main():
    print("🔬 Knowledge Synthesis Kernel v2.1")
    print("=" * 55)

    print("\n📂 Loading workspace...")
    entities, relations, doc_status, full_docs = load_workspace()
    print(f"   Entities: {len(entities)} docs, Relations: {len(relations)} docs")
    print(f"   Doc statuses: {len(doc_status)}, Full docs: {len(full_docs)}")

    print("\n🔗 Mapping docs → URLs (by ingest order)...")
    doc_map = build_doc_map(doc_status)
    for doc_id, info in doc_map.items():
        print(f"   {info['track_id'][:30]}... → {info['category']:8s} | {info['url'].split('/')[-1][:40]}")

    print("\n🗺️  Building page→entity map...")
    page_map = build_page_map(doc_map, entities, relations, full_docs)
    for url, page in page_map.items():
        print(f"   [{page['category']:8s}] {page['page_type']:12s} | {page['entity_count']:3d}e | {page['word_count']:5d}w | {url.split('/')[-1][:50]}")

    print("\n🦠 Detecting contamination...")
    contamination = detect_contamination(page_map)
    print(f"   Template pages: {contamination['template_page_count']}")
    print(f"   Real pages: {contamination['real_page_count']}")
    print(f"   Pure contamination entities: {contamination['pure_contamination_count']}")
    print(f"   Merged contamination: {contamination['merged_contamination_count']}")
    print(f"   Ratio: {contamination['contamination_ratio']}, Severity: {contamination['severity']}")

    if contamination["pure_contamination"]:
        print(f"\n   Pure contamination (template-only entities):")
        for e in contamination["pure_contamination"][:25]:
            print(f"     • {e}")
        if len(contamination["pure_contamination"]) > 25:
            print(f"     ... +{len(contamination['pure_contamination']) - 25} more")

    print("\n🏷️  Extracting typed entities from graph API...")
    typed_entities = extract_typed_entities(page_map)
    typed_count = sum(1 for e in typed_entities if e["types"])
    contaminated = [e for e in typed_entities if e["contamination"] and not e["real_only"]]
    print(f"   Total entities: {len(typed_entities)}, with types: {typed_count}")
    print(f"   Contaminated (template+real overlap): {len(contaminated)}")

    print("\n📏 Applying content rules to real pages...")
    # ── Load RuleBridge for Koray Gubur Tier 1 checks ──
    bridge = None
    try:
        from rule_bridge import RuleBridge
        bridge = RuleBridge()
        print(f"   🎯 RuleBridge loaded: {len(bridge._d_index)} deterministic + {len(bridge._dir_index)} directive checks")
    except (ImportError, FileNotFoundError) as e:
        print(f"   ⚠️  RuleBridge not available: {e}")

    rule_results = check_rules(page_map, bridge)
    for r in rule_results:
        print(f"   {r['url'].split('/')[-1][:45]:45s} | {r['compliance_pct']:5.1f}% | {r['pass_count']}/{r['total_rules']} ✅ | {r['fail_count']} ❌")

    print("\n🕳️  Computing gaps...")
    gaps = compute_gaps(rule_results, page_map)
    print(f"   Total gaps: {len(gaps)}")
    for g in gaps[:20]:
        print(f"   [{g['severity']:6s}] {g['type']:25s} | {g.get('url','').split('/')[-1][:45] if g.get('url') else ''}")

    report = build_report(page_map, contamination, typed_entities, rule_results, gaps)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✅ Report → {OUTPUT}")
    print(f"   {report['summary']['rule_compliance']} compliance")
    print(f"   {report['summary']['total_gaps']} gaps ({report['summary']['high_gaps']} high, {report['summary']['medium_gaps']} medium)")
    print(f"   Contamination: {contamination['severity']} ({contamination['pure_contamination_count']} entities)")

    # ── Run Entity Contamination Audit (client-facing product) ──
    print("\n🔬 Running Entity Contamination Audit Engine...")
    try:
        from entity_audit_engine import run_full_audit, generate_client_report
        audit_report = run_full_audit()
        generate_client_report(audit_report)
    except Exception as e:
        print(f"   ⚠️  Audit engine skipped: {e}")

    return report


if __name__ == "__main__":
    main()
