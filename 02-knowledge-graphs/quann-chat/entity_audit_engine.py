#!/usr/bin/env python3
"""
Entity Contamination Audit Engine v1.0
======================================
Audits a LightRAG knowledge graph for foreign entity contamination from
website templates (Framer, WordPress themes, etc.), generates a client-facing
report that doubles as a paid audit product.

AUDIT SCOPE:
  - Template-only entities: present ONLY in template pages → CRITICAL contamination
  - Mixed-source entities: appear in both template and real pages → requires LLM judgment
  - Domain entities: present only in real content → verified clean

OUTPUT:
  - Client-facing markdown report: quann.homes SEO/AEO/GEO Entity Audit
  - Structured JSON for downstream processing
  - Severity-graded findings with source attribution
"""

import json
import os
import re
import time
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

# ── Config ──
WORKSPACE = Path("/home/steve/lightrag-apps/quann-chat/workspace")
OUTPUT_DIR = Path("/home/steve/lightrag-apps/knowledge-synthesis")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.4.148:11434")
CLASSIFIER_MODEL = "gemma4:31b-cloud"  # Fast, capable for classification tasks
BATCH_SIZE = 15  # Entities per LLM call

# ── Sitemap knowledge ──
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

TEMPLATE_URLS = {u for u in SITEMAP_ORDER if "portfolio-dark-work/" in u}
TEMPLATE_URLS |= {"https://quann.homes/portfolio-dark-work", "https://quann.homes/portfolio-dark-home"}
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


def load_json_safe(path):
    """Load JSON with control char handling."""
    try:
        with open(path) as f:
            return json.loads(f.read(), strict=False)
    except Exception as e:
        print(f"  ⚠️  Failed to load {path}: {e}")
        return {}


def call_ollama(prompt, model=CLASSIFIER_MODEL, timeout=120):
    """Call Ollama API for text generation."""
    import urllib.request
    url = f"{OLLAMA_HOST}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 2000}
    })
    req = urllib.request.Request(url, data=payload.encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ❌ Ollama call failed: {e}")
        return {"response": "", "error": str(e)}


def extract_entities_from_workspace():
    """Extract all entities from VDB and map to source pages."""
    vdb = load_json_safe(WORKSPACE / "vdb_entities.json")
    doc_entities = load_json_safe(WORKSPACE / "kv_store_full_entities.json")
    doc_status = load_json_safe(WORKSPACE / "kv_store_doc_status.json")

    # Build entity registry
    entities = {}
    for item in vdb.get("data", []):
        name = item.get("entity_name", "")
        if name:
            entities[name] = {
                "entity_id": item.get("__id__", ""),
                "content": item.get("content", ""),
                "created_at": item.get("__created_at__", 0),
            }

    # Build entity → docs mapping
    entity_to_docs = defaultdict(set)
    for doc_id, data in doc_entities.items():
        for ename in data.get("entity_names", []):
            entity_to_docs[ename].add(doc_id)

    # Map docs to URLs (timestamp-order matching)
    sorted_docs = sorted(doc_status.items(), key=lambda x: re.search(r'insert_(\d{8})_(\d{6})', str(x[0])).group(1) + re.search(r'insert_(\d{8})_(\d{6})', str(x[0])).group(2) if re.search(r'insert_(\d{8})_(\d{6})', str(x[0])) else "00000000000000")
    doc_to_url = {}
    for i, (doc_id, info) in enumerate(sorted_docs):
        fp = info.get("file_path", "")
        if fp and fp.startswith("http"):
            doc_to_url[doc_id] = fp
        elif i < len(SITEMAP_ORDER):
            doc_to_url[doc_id] = SITEMAP_ORDER[i]
        else:
            doc_to_url[doc_id] = f"unknown:{doc_id[:8]}"

    # Classify by source
    results = []
    for ename, docs in entity_to_docs.items():
        if ename not in entities:
            continue
        doc_urls = [doc_to_url.get(d, "unknown") for d in docs]
        t_count = sum(1 for u in doc_urls if u in TEMPLATE_URLS)
        r_count = sum(1 for u in doc_urls if u in REAL_URLS)

        if t_count > 0 and r_count == 0:
            src_class = "template_only"
        elif r_count > 0 and t_count == 0:
            src_class = "domain_only"
        elif t_count > 0 and r_count > 0:
            src_class = "mixed"
        else:
            src_class = "unknown"

        results.append({
            "entity_name": ename,
            "description": entities[ename]["content"][:500],
            "source_class": src_class,
            "doc_count": len(docs),
            "template_doc_count": t_count,
            "real_doc_count": r_count,
            "source_urls": [u for u in doc_urls if u != "unknown"],
            "template_urls": [u for u in doc_urls if u in TEMPLATE_URLS],
            "real_urls": [u for u in doc_urls if u in REAL_URLS],
        })

    return results


def classify_batch_with_llm(entities_batch, batch_label):
    """Classify a batch of entities using LLM — confirms whether they belong to real estate domain."""
    if not entities_batch:
        return []

    # Build prompt
    entity_list = []
    for i, e in enumerate(entities_batch):
        entity_list.append(f"{i+1}. Entity: \"{e['entity_name']}\"\n   Description: \"{e['description'][:300]}\"\n   Current status: {e['source_class']}\n   Found on: {len(e['template_urls'])} template pages, {len(e['real_urls'])} real pages")

    prompt = f"""You are a real estate domain expert auditing a website's knowledge graph for entity contamination. 

A Framer website template was used to build a Katy, Texas real estate agent's website (quann.homes). The template shipped with demo content — fake portfolio projects, tech company names, design agency brands, etc. These foreign entities are now mixed into the real estate knowledge graph, poisoning search engine understanding.

For EACH entity below, classify it into ONE category and explain why in one sentence.

Categories:
- CONTAMINATION: Not related to real estate, home buying, Texas living, or the agent's business. These are template leftovers (design agencies, fake portfolio names, tech products, random brands).
- LEGITIMATE: Genuinely related to real estate, home buying, mortgages, Texas, relocation, or the agent's professional identity.
- AMBIGUOUS: Could be either — needs human review.

Respond in this EXACT JSON format (no markdown, no backticks):
{{
  "classifications": [
    {{"entity": "Entity Name", "category": "CONTAMINATION|LEGITIMATE|AMBIGUOUS", "reasoning": "one sentence explanation"}},
    ...
  ]
}}

Entities to classify:
{chr(10).join(entity_list)}

Respond with ONLY the JSON object, nothing else."""

    print(f"\n  🤖 Classifying {len(entities_batch)} {batch_label} entities with {CLASSIFIER_MODEL}...")
    result = call_ollama(prompt)

    try:
        text = result.get("response", "")
        # Extract JSON from response (may be wrapped in backticks)
        json_match = re.search(r'\{.*"classifications".*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(), strict=False)
            return data.get("classifications", [])
        else:
            print(f"  ⚠️  No JSON found in response. Raw: {text[:300]}")
            return []
    except json.JSONDecodeError as e:
        print(f"  ⚠️  JSON parse error: {e}")
        return []


def run_full_audit():
    """Run the complete audit pipeline."""
    print("=" * 70)
    print("  🔬 ENTITY CONTAMINATION AUDIT ENGINE v1.0")
    print("=" * 70)

    # 1. Extract and classify by source
    print("\n📊 Step 1: Extracting entities from workspace...")
    all_entities = extract_entities_from_workspace()

    template_only = [e for e in all_entities if e["source_class"] == "template_only"]
    mixed = [e for e in all_entities if e["source_class"] == "mixed"]
    domain_only = [e for e in all_entities if e["source_class"] == "domain_only"]

    print(f"   Total entities: {len(all_entities)}")
    print(f"   Template-only (no real page presence): {len(template_only)}")
    print(f"   Mixed (template + real pages): {len(mixed)}")
    print(f"   Domain-only (real pages only): {len(domain_only)}")

    # 2. LLM classification of suspected contamination
    print(f"\n🧠 Step 2: LLM classification of {len(template_only) + len(mixed)} suspect entities...")

    all_classifications = []

    # Classify template-only entities
    for i in range(0, len(template_only), BATCH_SIZE):
        batch = template_only[i:i + BATCH_SIZE]
        results = classify_batch_with_llm(batch, "template-only")
        all_classifications.extend(results)
        if i + BATCH_SIZE < len(template_only):
            time.sleep(1)  # Rate limit courtesy

    # Classify mixed entities
    for i in range(0, len(mixed), BATCH_SIZE):
        batch = mixed[i:i + BATCH_SIZE]
        results = classify_batch_with_llm(batch, "mixed")
        all_classifications.extend(results)
        if i + BATCH_SIZE < len(mixed):
            time.sleep(1)

    print(f"\n   LLM classified {len(all_classifications)} entities")

    # 3. Build final entity map with LLM verdicts
    classification_map = {c["entity"]: c for c in all_classifications if "entity" in c}

    findings = []
    for e in all_entities:
        name = e["entity_name"]
        llm = classification_map.get(name, {})
        llm_category = llm.get("category", "NOT_CLASSIFIED")
        llm_reasoning = llm.get("reasoning", "")

        # Determine final verdict
        if e["source_class"] == "domain_only":
            final = "CLEAN"
            severity = "none"
        elif llm_category == "CONTAMINATION":
            final = "CONFIRMED_CONTAMINATION"
            severity = "critical"
        elif llm_category == "LEGITIMATE":
            final = "FALSE_POSITIVE"  # Was flagged by source but LLM says it's real
            severity = "none"
        elif llm_category == "AMBIGUOUS":
            final = "NEEDS_REVIEW"
            severity = "medium"
        else:
            # LLM didn't classify — use source heuristic
            if e["source_class"] == "template_only":
                final = "LIKELY_CONTAMINATION"
                severity = "high"
            elif e["source_class"] == "mixed":
                final = "NEEDS_REVIEW"
                severity = "medium"
            else:
                final = "CLEAN"
                severity = "none"

        findings.append({
            "entity_name": name,
            "description": e["description"][:300],
            "source_class": e["source_class"],
            "llm_category": llm_category,
            "llm_reasoning": llm_reasoning,
            "final_verdict": final,
            "severity": severity,
            "source_urls": e["source_urls"],
            "template_urls": e["template_urls"],
            "real_urls": e["real_urls"],
            "template_doc_count": e["template_doc_count"],
            "real_doc_count": e["real_doc_count"],
        })

    # 4. Generate severity summary
    severity_counts = Counter(f["severity"] for f in findings)
    print(f"\n📋 Severity summary:")
    print(f"   CRITICAL (confirmed contamination): {severity_counts.get('critical', 0)}")
    print(f"   HIGH (likely contamination): {severity_counts.get('high', 0)}")
    print(f"   MEDIUM (needs review): {severity_counts.get('medium', 0)}")
    print(f"   CLEAN (false positives or domain-only): {severity_counts.get('none', 0)}")

    # 5. Save structured report
    report = {
        "audit_metadata": {
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "website": "quann.homes",
            "domain": "Katy, Texas Real Estate",
            "classifier_model": CLASSIFIER_MODEL,
            "total_entities_analyzed": len(findings),
            "total_contamination_sources": len(TEMPLATE_URLS),
        },
        "severity_summary": dict(severity_counts),
        "findings": sorted(findings, key=lambda x: {
            "critical": 0, "high": 1, "medium": 2, "none": 3
        }.get(x["severity"], 4))
    }

    report_path = OUTPUT_DIR / "entity_audit_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n✅ JSON report saved: {report_path}")

    return report


def generate_client_report(report):
    """Generate a client-facing markdown report that can be shown directly to a website owner."""
    now = datetime.now().strftime("%B %d, %Y")
    critical = [f for f in report["findings"] if f["severity"] == "critical"]
    high = [f for f in report["findings"] if f["severity"] == "high"]
    medium = [f for f in report["findings"] if f["severity"] == "medium"]
    false_positives = [f for f in report["findings"] if f["final_verdict"] == "FALSE_POSITIVE"]

    lines = []
    lines.append(f"# 🧹 Entity Contamination Audit — quann.homes")
    lines.append(f"")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Auditor:** Hermes AI — Knowledge Synthesis Engine")
    lines.append(f"**Website:** quann.homes | **Domain:** Katy, Texas Real Estate")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Executive summary
    total_flagged = len(critical) + len(high)
    lines.append(f"## ⚠️ Executive Summary")
    lines.append(f"")
    lines.append(f"Your quann.homes website was built using a **Framer template** that shipped with demo content — fake portfolio projects, sample company names, and design-agency branding. These entities are now embedded in your website's underlying knowledge graph, visible to search engines like Google, ChatGPT, and Perplexity.")
    lines.append(f"")
    lines.append(f"### Key Findings")
    lines.append(f"")
    lines.append(f"| Metric | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| Total entities extracted from your site | {report['audit_metadata']['total_entities_analyzed']} |")
    lines.append(f"| 🚨 **CRITICAL — confirmed foreign contamination** | **{len(critical)}** |")
    lines.append(f"| ⚠️ HIGH — likely contamination (heuristic) | {len(high)} |")
    lines.append(f"| 🔍 MEDIUM — needs manual review | {len(medium)} |")
    lines.append(f"| ✅ False positives (flagged but confirmed legitimate) | {len(false_positives)} |")
    lines.append(f"| Contamination source pages (template leftovers) | {len(TEMPLATE_URLS)} |")
    lines.append(f"")

    if total_flagged > 0:
        lines.append(f"### 🚨 Why This Matters")
        lines.append(f"")
        lines.append(f"Search engines (Google, ChatGPT, Perplexity, Gemini) build a **knowledge graph** of what your business is about by extracting entities from your website. When they see \"3D Rendering\" and \"App Design\" alongside \"Katy Texas Real Estate,\" your entity profile becomes confused. This directly impacts:")
        lines.append(f"")
        lines.append(f"- **SEO:** Diluted topical authority — Google may not rank you for real estate queries as highly as it should")
        lines.append(f"- **AEO (Answer Engine Optimization):** AI Overviews may not cite you for home-buying questions because your entity graph looks like a design agency")
        lines.append(f"- **GEO (Generative Engine Optimization):** ChatGPT/Gemini may not recommend you in real estate conversations because your site's entity fingerprint is mixed-signal")
        lines.append(f"- **Trust:** Home buyers researching you via AI search may see conflicting signals about what your business actually does")
        lines.append(f"")

    # CRITICAL findings
    if critical:
        lines.append(f"---")
        lines.append(f"## 🚨 CRITICAL — Confirmed Foreign Entities")
        lines.append(f"")
        lines.append(f"These entities were confirmed by AI analysis to have **no relationship** to real estate, home buying, Texas living, or your professional identity. They originate from Framer template demo content and are actively poisoning your knowledge graph.")
        lines.append(f"")
        lines.append(f"| # | Entity | What It Is | Source Page(s) |")
        lines.append(f"|---|---|---|---|")
        for i, f in enumerate(critical, 1):
            pages = ", ".join([url.replace("https://quann.homes/", "/") for url in f["template_urls"][:3]])
            lines.append(f"| {i} | **{f['entity_name']}** | {f['llm_reasoning'][:120]} | {pages} |")
        lines.append(f"")

    # HIGH findings
    if high:
        lines.append(f"---")
        lines.append(f"## ⚠️ HIGH — Likely Contamination (Auto-Detected)")
        lines.append(f"")
        lines.append(f"These entities appear only on template pages and never on your real content pages. High probability of being template leftovers.")
        lines.append(f"")
        template_entities = [f['entity_name'] for f in high]
        lines.append(f"**Entities:** " + ", ".join(f"`{e}`" for e in template_entities))
        lines.append(f"")

    # MEDIUM findings
    if medium:
        lines.append(f"---")
        lines.append(f"## 🔍 MEDIUM — Needs Review")
        lines.append(f"")
        lines.append(f"These entities appear on both template and real pages, or couldn't be definitively classified. They require human judgment.")
        lines.append(f"")
        for f in medium:
            lines.append(f"- **{f['entity_name']}** — {f['llm_reasoning'][:150] if f['llm_reasoning'] else 'Manual review required'}")
        lines.append(f"")

    # FALSE POSITIVES (good news)
    if false_positives:
        lines.append(f"---")
        lines.append(f"## ✅ Confirmed Legitimate (False Positives)")
        lines.append(f"")
        lines.append(f"These were initially flagged because they appear on template pages, but LLM analysis confirmed they are genuinely related to your real estate business:")
        lines.append(f"")
        for f in false_positives:
            lines.append(f"- **{f['entity_name']}** — {f['llm_reasoning'][:150]}")
        lines.append(f"")

    # Remediation guide
    lines.append(f"---")
    lines.append(f"## 🛠️ Remediation Guide")
    lines.append(f"")
    lines.append(f"### Immediate Actions (This Week)")
    lines.append(f"")
    lines.append(f"1. **Delete template portfolio pages.** If `/portfolio-dark-work/` pages are not needed, remove them from your site. This eliminates {len(TEMPLATE_URLS)} contamination sources at once.")
    lines.append(f"2. **Remove template demo content.** For any template pages you keep, remove all demo text, images, and project names. Replace with your own content or leave blank.")
    lines.append(f"3. **Re-submit sitemap** to Google Search Console after cleanup.")
    lines.append(f"")
    lines.append(f"### Short-Term (This Month)")
    lines.append(f"")
    lines.append(f"4. **Audit metadata.** Check page titles, meta descriptions, and Open Graph tags for template leftovers.")
    lines.append(f"5. **Review schema markup.** Template-generated schema may reference non-real-estate types. Verify with Google's Rich Results Test.")
    lines.append(f"6. **Request re-indexing** of affected pages in Google Search Console.")
    lines.append(f"")
    lines.append(f"### Ongoing")
    lines.append(f"")
    lines.append(f"7. **Schedule quarterly audits.** Run this audit engine after any site update or redesign to catch new contamination.")
    lines.append(f"8. **Monitor AI search results.** Periodically search for your brand in ChatGPT, Perplexity, and Google AI Overviews. Check what entities and descriptions they associate with you.")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*This audit was generated automatically by the Knowledge Synthesis Engine. It identifies entity-level contamination from website templates and provides actionable remediation steps. For questions, contact your SEO strategist.*")

    report_text = "\n".join(lines)
    report_path = OUTPUT_DIR / "entity_audit_client_report.md"
    with open(report_path, "w") as f:
        f.write(report_text)
    print(f"✅ Client report saved: {report_path}")

    return report_text


if __name__ == "__main__":
    report = run_full_audit()
    client_report = generate_client_report(report)
    print(f"\n{'=' * 70}")
    print(f"  ✅ AUDIT COMPLETE")
    print(f"{'=' * 70}")
    print(f"\nReports saved to: {OUTPUT_DIR}")
    print(f"  entity_audit_report.json — Structured data for downstream processing")
    print(f"  entity_audit_client_report.md — Client-facing deliverable")
