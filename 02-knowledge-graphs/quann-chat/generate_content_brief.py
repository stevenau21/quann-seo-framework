#!/usr/bin/env python3
"""
Three-Way Join Content Brief Generator ─ Ignition Point of the Flywheel

Fuses three data streams into a canonical, writer-ready content brief:

  Stream 1 (Tier 1): Failed deterministic audit gaps ─ from RuleBridge
  Stream 2 (Tier 2): Prioritized architectural directives (capped at 8) ─ from RuleBridge
  Stream 3 (Domain KG): Real-world entity context ─ from LightRAG workspace

ENTITY ANCHORING CONSTRAINT: Every directive in the brief must be grounded
in a real entity from the Domain KG. No abstract SEO theory without a
connection to a specific Katy/Texas real estate data point.

Output format ─ 4 canonical sections:
  1. Meta-Information & Priority Score
  2. Deterministic Fixes (The Gaps)
  3. Primary Domain Entities (from KG)
  4. Architectural Directives (capped Tier 2 rules)

Usage:
    python3 generate_content_brief.py --url https://quann.homes/blog/out-of-state-buyer-guide
    python3 generate_content_brief.py --url ... --output /path/to/brief.md
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from typing import Optional


# ── Paths ──
WORKSPACE = Path("/home/steve/lightrag-apps/quann-chat/workspace")
GAP_REPORT = Path("/home/steve/lightrag-apps/knowledge-synthesis/gap_report.json")
OUTPUT_DIR = Path("/home/steve/lightrag-apps/knowledge-synthesis/briefs/")

# Known sitemap URLs (for doc_id → URL mapping)
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


# ═══════════════════════════════════════════════════════════════════════
# DOMAIN KG QUERY ENGINE  (Stream 3)
# ═══════════════════════════════════════════════════════════════════════

class DomainKGQuery:
    """Queries the LightRAG workspace for entity context anchored to quann.homes pages."""

    def __init__(self, workspace_path: Optional[Path] = None):
        ws = workspace_path or WORKSPACE
        self._entities = json.loads((ws / "kv_store_full_entities.json").read_text())
        self._relations = json.loads((ws / "kv_store_full_relations.json").read_text())
        self._docs = json.loads((ws / "kv_store_full_docs.json").read_text())

        # Build entity → doc_ids index
        self._entity_docs: dict[str, set[str]] = defaultdict(set)
        for doc_id, edata in self._entities.items():
            for name in edata.get("entity_names", []):
                self._entity_docs[name].add(doc_id)

        # Build entity → relations index
        self._entity_rels: dict[str, list[dict]] = defaultdict(list)
        for doc_id, rdata in self._relations.items():
            for pair in rdata.get("relation_pairs", []):
                if len(pair) >= 2:
                    subj, obj = pair[0], pair[1]
                    self._entity_rels[subj].append({"target": obj, "doc_id": doc_id})
                    self._entity_rels[obj].append({"target": subj, "doc_id": doc_id})

        # Build doc_id → URL mapping (by ingest order)
        tracked = [(did, v.get("track_id", ""))
                   for did, v in json.loads(
                       (ws / "kv_store_doc_status.json").read_text()
                   ).items()]
        tracked.sort(key=lambda x: x[1].split("_")[2] if len(x[1].split("_")) > 2 else "0")
        self._doc_url: dict[str, str] = {}
        for i, (doc_id, _) in enumerate(tracked):
            if i < len(SITEMAP_ORDER):
                self._doc_url[doc_id] = SITEMAP_ORDER[i]

        # Load contamination set from gap report
        gap = json.loads(GAP_REPORT.read_text()) if GAP_REPORT.exists() else {}
        self._contaminated = set(
            gap.get("contamination_analysis", {}).get("pure_contamination", [])
        )

    def get_page_entities(self, url: str) -> list[dict]:
        """Return all entities found on a page, enriched with KG context."""
        # Find doc_id for this URL
        doc_id = None
        for did, mapped_url in self._doc_url.items():
            if mapped_url == url:
                doc_id = did
                break
        if not doc_id:
            return []

        edata = self._entities.get(doc_id, {})
        entity_names = edata.get("entity_names", [])

        results = []
        for name in entity_names:
            is_contaminated = name in self._contaminated
            rels = self._entity_rels.get(name, [])
            unique_targets = list({r["target"] for r in rels})
            doc_ids = self._entity_docs.get(name, set())
            page_urls = [self._doc_url.get(d, d) for d in doc_ids]

            # Get content snippet
            snippet = ""
            content = self._docs.get(doc_id, {}).get("content", "")
            if content and name.lower() in content.lower():
                idx = content.lower().find(name.lower())
                start = max(0, idx - 100)
                end = min(len(content), idx + len(name) + 200)
                snippet = content[start:end].replace("\n", " ").strip()[:300]

            results.append({
                "name": name,
                "contaminated": is_contaminated,
                "relations": unique_targets[:10],
                "relation_count": len(unique_targets),
                "page_count": len(page_urls),
                "pages": page_urls[:5],
                "snippet": snippet,
                "description": edata.get("description", ""),
            })

        # Sort: clean first, then by page_count desc
        results.sort(key=lambda e: (e["contaminated"], -e["page_count"]))
        return results

    def get_anchor_entities(self, url: str, max_entities: int = 15) -> list[dict]:
        """Return clean, high-signal entities for content anchoring."""
        all_ents = self.get_page_entities(url)
        clean = [e for e in all_ents if not e["contaminated"] and e["page_count"] >= 2]
        # Prioritize entities with relations and domain relevance
        domain_keywords = {
            "katy", "houston", "texas", "buyer", "home", "mortgage", "closing",
            "inspection", "property", "tax", "school", "real estate", "loan",
            "insurance", "down payment", "relocation", "first-time",
        }
        def relevance_score(e: dict) -> tuple:
            name_lower = e["name"].lower()
            kw_match = sum(1 for kw in domain_keywords if kw in name_lower)
            return (-kw_match, -e["relation_count"], -e["page_count"])
        clean.sort(key=relevance_score)
        return clean[:max_entities]

    def get_gap_entities(self, url: str, page_type: str, max_entities: int = 10) -> list[dict]:
        """Return entities that are ONTOLOGICALLY connected to the page's centroid
        but MISSING from the target page.

        CORRECTED: Uses graph traversal from the centroid entity rather than flat
        sibling-page Jaccard distance. An entity is only flagged as a 'gap' if it
        has a direct hierarchical relationship (Parent/Child/Attribute) to the
        target page's centroid entity within the Domain KG.

        This prevents keyword cannibalization — a page about 'Out of State Buyers'
        should not absorb 'first-time homebuyer' entities just because they share
        a /blog folder."""
        # Get all entities on the target page
        target_ents = self.get_page_entities(url)
        target_names = {e["name"] for e in target_ents if not e["contaminated"]}

        # Resolve the centroid entity
        centroid = self._resolve_centroid(target_ents)
        if not centroid:
            return []

        # 1-hop traversal from centroid through the entity→relations graph
        centroid_rels = self._entity_rels.get(centroid, [])
        one_hop_candidates = list({r["target"] for r in centroid_rels})

        # Build gap candidates: each must be graph-connected, on 2+ real pages,
        # and NOT already on the target page
        domain_keywords = {
            "katy", "houston", "texas", "buyer", "home", "mortgage", "closing",
            "inspection", "property", "tax", "school", "real estate", "loan",
            "insurance", "down payment", "relocation", "first-time", "agent",
            "broker", "commission", "hoa", "contract",
        }

        gap_entities: list[dict] = []
        for candidate in one_hop_candidates:
            if candidate in target_names:
                continue
            if candidate in self._contaminated:
                continue

            doc_ids = self._entity_docs.get(candidate, set())
            page_urls = [self._doc_url.get(d, d) for d in doc_ids]
            real_pages = [p for p in page_urls if p not in TEMPLATE_URLS]
            if len(real_pages) < 2:
                continue  # Not established enough as a domain entity

            rels = self._entity_rels.get(candidate, [])
            connections = list({r["target"] for r in rels})

            name_lower = candidate.lower()
            kw_match = sum(1 for kw in domain_keywords if kw in name_lower)

            gap_entities.append({
                "name": candidate,
                "centroid": centroid,
                "relation_count": len(connections),
                "page_count": len(real_pages),
                "pages": real_pages[:5],
                "connections": connections[:8],
                "_score": (kw_match, len(connections), len(real_pages)),
            })

        # Sort by ontological signal: keyword match → relation count → page count
        gap_entities.sort(key=lambda e: (-e["_score"][0], -e["_score"][1], -e["_score"][2]))
        for e in gap_entities:
            del e["_score"]

        return gap_entities[:max_entities]

    def _resolve_centroid(self, page_entities: list[dict]) -> str | None:
        """Identify the centroid entity of a page.

        The centroid is the clean entity with the highest combined score of:
        1. Domain keyword relevance (does it anchor a real estate concept?)
        2. Relation count in the KG (does it connect to other entities?)

        Contaminated entities (54 Framer template artifacts) are excluded.
        Generic entities with zero domain keywords (e.g., person names,
        boilerplate legal terms) are deprioritized.

        Returns the centroid entity name, or None if no suitable centroid exists."""
        domain_keywords = {
            "katy", "houston", "texas", "buyer", "home", "mortgage", "closing",
            "inspection", "property", "tax", "school", "real estate", "loan",
            "insurance", "down payment", "relocation", "first-time", "agent",
            "broker", "commission", "hoa", "contract", "out of state", "moving",
            "relocate",
        }

        candidates = []
        for e in page_entities:
            if e["contaminated"]:
                continue
            name_lower = e["name"].lower()
            kw_match = sum(1 for kw in domain_keywords if kw in name_lower)
            rel_count = e["relation_count"]
            candidates.append((e["name"], kw_match, rel_count))

        if not candidates:
            return None

        # Primary: keyword match. Tie-break: relation count.
        candidates.sort(key=lambda x: (-x[1], -x[2]))
        return candidates[0][0]

    @property
    def contaminated_set(self) -> set[str]:
        return self._contaminated


# ═══════════════════════════════════════════════════════════════════════
# THREE-WAY JOIN ENGINE
# ═══════════════════════════════════════════════════════════════════════

class ThreeWayJoin:
    """Fuses gap, directive, and entity streams into a Content Brief."""

    def __init__(self):
        self._gap = json.loads(GAP_REPORT.read_text()) if GAP_REPORT.exists() else {}
        self._kg = DomainKGQuery()

        # Lazy-load bridge
        self._bridge = None

    @property
    def bridge(self):
        if self._bridge is None:
            from rule_bridge import RuleBridge, bridge_page_types
            self._bridge = RuleBridge()
            self._bridge_page_types = bridge_page_types
        return self._bridge

    def build(self, url: str, cap: int = 8) -> dict:
        """Execute the three-way join and return a ContentBrief dict."""
        # ── Locate page in gap report ──
        rule_results = self._gap.get("rule_results", [])
        page_rules = next((r for r in rule_results if r["url"] == url), None)
        if not page_rules:
            raise ValueError(f"URL not found in gap report: {url}")

        page_type = page_rules.get("page_type", "blog_post")
        from rule_bridge import bridge_page_types
        bpage_type = bridge_page_types(page_type)

        # ─────────────────────────────────────────────────────────────
        # STREAM 1: Failed Deterministic Gaps
        # ─────────────────────────────────────────────────────────────
        all_checks = page_rules.get("rule_checks", [])
        bridge_fails = [
            c for c in all_checks
            if c.get("bridge") and c.get("status") == "fail"
        ]
        kernel_fails = [
            c for c in all_checks
            if not c.get("bridge") and c.get("status") == "fail"
        ]

        failed_categories = list({c.get("category", "") for c in bridge_fails if c.get("category")})

        # ─────────────────────────────────────────────────────────────
        # STREAM 2: Prioritized Directives (Injection Cap)
        # ─────────────────────────────────────────────────────────────
        directives = self.bridge.route_directives(
            bpage_type, failed_categories, cap=cap
        )
        directive_prompt = self.bridge.build_directive_prompt_section(directives)

        # ─────────────────────────────────────────────────────────────
        # STREAM 3: Domain KG Entity Context
        # ─────────────────────────────────────────────────────────────
        anchor_entities = self._kg.get_anchor_entities(url, max_entities=15)
        gap_entities = self._kg.get_gap_entities(url, page_type, max_entities=10)
        all_page_entities = self._kg.get_page_entities(url)
        contaminated_on_page = [e for e in all_page_entities if e["contaminated"]]

        # ── Compute priority score ──
        total_det = sum(1 for c in all_checks if c.get("bridge"))
        det_fails = len(bridge_fails)
        kernel_fail_count = len(kernel_fails)
        total_fails = det_fails + kernel_fail_count

        priority_score = _compute_priority_score(
            det_fails=det_fails,
            total_det=total_det,
            kernel_fails=kernel_fail_count,
            directive_count=len(directives),
            anchor_count=len(anchor_entities),
        )

        return {
            "meta": {
                "url": url,
                "slug": url.replace("https://quann.homes/", ""),
                "page_type": page_type,
                "bridge_page_type": bpage_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "priority_score": priority_score,
                "compliance_pct": page_rules.get("compliance_pct", 0),
                "word_count": page_rules.get("word_count", 0),
                "total_checks": page_rules.get("total_rules", 0),
                "bridge_checks": page_rules.get("bridge_checks", 0),
            },
            "stream_1_gaps": {
                "deterministic_fails": [
                    {
                        "rule_id": c["rule_id"],
                        "rule": c["rule"],
                        "detail": c["detail"],
                        "fix_directive": c.get("fix_directive", ""),
                        "priority": c.get("priority", "medium"),
                        "category": c.get("category", ""),
                    }
                    for c in bridge_fails
                ],
                "kernel_fails": [
                    {
                        "rule_id": c["rule_id"],
                        "rule": c["rule"],
                        "detail": c.get("detail", ""),
                    }
                    for c in kernel_fails
                ],
                "total_det_checks": total_det,
                "det_fail_count": det_fails,
                "kernel_fail_count": kernel_fail_count,
            },
            "stream_2_directives": {
                "injected": [
                    {
                        "card_id": d["card_id"],
                        "content": d["content"],
                        "framework": d["framework"],
                        "category": d["category"],
                        "priority": d["priority"],
                    }
                    for d in directives
                ],
                "injection_cap": cap,
                "total_available": len(self.bridge._dir_index),
                "prompt_section": directive_prompt,
            },
            "stream_3_entities": {
                "anchor_entities": anchor_entities,
                "gap_entities": gap_entities,
                "contaminated_on_page": [
                    {"name": e["name"], "page_count": e["page_count"]}
                    for e in contaminated_on_page
                ],
                "total_page_entities": len(all_page_entities),
                "clean_entities": len(all_page_entities) - len(contaminated_on_page),
            },
        }

    def format_markdown(self, brief: dict) -> str:
        """Render the ContentBrief as canonical markdown."""
        m = brief["meta"]
        s1 = brief["stream_1_gaps"]
        s2 = brief["stream_2_directives"]
        s3 = brief["stream_3_entities"]

        lines = []

        # ═══════════════════════════════════════════════════════════
        # SECTION 1: Meta-Information & Priority Score
        # ═══════════════════════════════════════════════════════════
        lines.append(f"# Content Brief: {m['slug']}\n")
        lines.append(f"> **Generated:** {m['generated_at']}")
        lines.append(f"> **Target URL:** {m['url']}")
        lines.append(f"> **Page Type:** {m['page_type']} (bridge: {m['bridge_page_type']})")
        lines.append(f"> **Current Compliance:** {m['compliance_pct']}%")
        lines.append(f"> **Word Count:** {m['word_count']}")
        lines.append(f"> **Total Checks:** {m['total_checks']} ({m['bridge_checks']} bridge)")
        lines.append("")
        lines.append(f"## Priority Score: **{m['priority_score']['score']:.0f}/100**")
        lines.append("")
        lines.append("| Factor | Value | Weight | Contribution |")
        lines.append("|--------|-------|--------|-------------|")
        for f in m["priority_score"]["factors"]:
            lines.append(
                f"| {f['label']} | {f['value']} | {f['weight']}% | {f['contribution']:.0f} |"
            )
        lines.append("")
        lines.append(f"**Interpretation:** {m['priority_score']['interpretation']}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # ═══════════════════════════════════════════════════════════
        # SECTION 2: Deterministic Fixes (The Gaps)
        # ═══════════════════════════════════════════════════════════
        lines.append("## 🔧 Section 2: Deterministic Fixes\n")
        lines.append(
            f"_These {s1['det_fail_count']} gaps were detected by the Bifurcated RuleBridge "
            f"using pure regex/computation. Zero API calls. Each must be addressed to pass audit._\n"
        )

        if s1["deterministic_fails"]:
            lines.append("### Bridge Detected Gaps (Koray Gubur — Tier 1)")
            lines.append("")
            for i, f in enumerate(s1["deterministic_fails"], 1):
                icon = "🔴" if f["priority"] == "high" else "🟡"
                lines.append(f"{i}. {icon} **{f['rule_id']}**")
                lines.append(f"   - Rule: {f['rule']}")
                lines.append(f"   - Detail: {f['detail']}")
                if f["fix_directive"]:
                    lines.append(f"   - Fix: {f['fix_directive']}")
                lines.append("")

        if s1["kernel_fails"]:
            lines.append("### Kernel v2.1 Gaps")
            lines.append("")
            for i, f in enumerate(s1["kernel_fails"], 1):
                lines.append(f"{i}. ❌ **{f['rule_id']}**: {f['rule']}")
                lines.append(f"   - Detail: {f['detail']}")
                lines.append("")

        lines.append("---")
        lines.append("")

        # ═══════════════════════════════════════════════════════════
        # SECTION 3: Primary Domain Entities
        # ═══════════════════════════════════════════════════════════
        lines.append("## 🏠 Section 3: Primary Domain Entities\n")
        lines.append(
            f"_The following {len(s3['anchor_entities'])} entities are extracted from the "
            f"quann.homes Knowledge Graph. They represent the real-world data points that "
            f"MUST be referenced in the content to establish topical authority._\n"
        )
        lines.append("")
        lines.append(
            f"**Entity Health:** {s3['clean_entities']}/{s3['total_page_entities']} clean "
            f"({s3['total_page_entities'] - s3['clean_entities']} contaminated filtered)"
        )
        lines.append("")

        lines.append("### Anchor Entities (must be mentioned)")
        lines.append("")
        for i, e in enumerate(s3["anchor_entities"], 1):
            lines.append(f"#### {i}. {e['name']}")
            lines.append(f"- **Pages:** {e['page_count']} on quann.homes")
            if e["relation_count"]:
                sample_rels = e["relations"][:5]
                lines.append(f"- **Relations:** {', '.join(sample_rels)}")
            if e["snippet"]:
                lines.append(f"- **Context:** \"...{e['snippet'][:200]}...\"")
            lines.append("")

        # ── Gap Entities: MISSING from this page but present on siblings ──
        gap_ents = s3.get("gap_entities", [])
        if gap_ents:
            lines.append("### 🕳️ Missing Entities (present on sibling pages — MUST BE ADDED)")
            lines.append("")
            lines.append(
                f"_These {len(gap_ents)} entities exist on other {m['page_type']} pages "
                f"but are ABSENT from this page. Adding them is the highest-leverage way "
                f"to improve entity coverage and topical authority._"
            )
            lines.append("")
            for i, e in enumerate(gap_ents, 1):
                lines.append(f"{i}. **{e['name']}**")
                lines.append(f"   - Found on: {', '.join(e['found_on'][:3])}")
                if e["relation_count"]:
                    lines.append(f"   - Relations: {', '.join(e['relations'][:5])}")
                lines.append("")

        if s3["contaminated_on_page"]:
            lines.append("### ⚠️ Contaminated Entities (DO NOT USE)")
            lines.append("")
            lines.append("These are Framer template artifacts. They must be excluded:")
            lines.append("")
            for e in s3["contaminated_on_page"]:
                lines.append(f"- ~~{e['name']}~~")

        lines.append("")
        lines.append("---")
        lines.append("")

        # ═══════════════════════════════════════════════════════════
        # SECTION 4: Architectural Directives
        # ═══════════════════════════════════════════════════════════
        lines.append("## 🏗️ Section 4: Architectural Directives\n")
        lines.append(
            f"_Injection Cap: {s2['injection_cap']} directives selected from "
            f"{s2['total_available']} available. These represent Koray Gubur's "
            f"Tier 1 grounded rules, injected into the content generation prompt._\n"
        )

        if s2["prompt_section"]:
            lines.append(s2["prompt_section"])
        else:
            lines.append("_No directives matched for this page type and gap profile._")

        lines.append("")
        lines.append("---")
        lines.append("")

        # ═══════════════════════════════════════════════════════════
        # WRITER INSTRUCTION BLOCK
        # ═══════════════════════════════════════════════════════════
        lines.append("## ✍️ Writer Instructions\n")
        lines.append(
            "Using the three sections above, produce content that:\n"
            "1. **Fixes every deterministic gap** — implement each fix_directive exactly\n"
            "2. **References every anchor entity** — each must appear naturally in the text\n"
            "3. **Follows every architectural directive** — treat them as non-negotiable requirements\n"
            "4. **Never mentions contaminated entities** — they are Framer template artifacts\n"
            "5. **Writes for a relocating buyer** — warm, knowledgeable, anticipates anxiety\n"
        )
        lines.append("")
        lines.append(
            "*Brief generated by Knowledge Synthesis Engine — Three-Way Join Generator.*\n"
            f"*Source: {GAP_REPORT}*"
        )

        return "\n".join(lines)


def _compute_priority_score(
    det_fails: int,
    total_det: int,
    kernel_fails: int,
    directive_count: int,
    anchor_count: int,
) -> dict:
    """Compute a 0-100 priority score for the brief."""
    factors = []

    # Factor 1: Deterministic failure rate (weight 40%)
    det_rate = det_fails / max(total_det, 1)
    det_score = min(det_rate * 100, 100)
    factors.append({
        "label": "Deterministic Gap Rate",
        "value": f"{det_fails}/{total_det} ({det_rate:.0%})",
        "weight": 40,
        "contribution": det_score * 0.4,
    })

    # Factor 2: Kernel failures (weight 25%)
    kernel_score = min(kernel_fails * 8, 100)
    factors.append({
        "label": "Kernel Failures",
        "value": str(kernel_fails),
        "weight": 25,
        "contribution": kernel_score * 0.25,
    })

    # Factor 3: Directive relevance (weight 20%)
    dir_score = min(directive_count / 8 * 100, 100)
    factors.append({
        "label": "Directive Injections",
        "value": f"{directive_count}/8",
        "weight": 20,
        "contribution": dir_score * 0.20,
    })

    # Factor 4: KG entity richness (weight 15%)
    kg_score = min(anchor_count / 15 * 100, 100)
    factors.append({
        "label": "KG Anchor Entities",
        "value": str(anchor_count),
        "weight": 15,
        "contribution": kg_score * 0.15,
    })

    total = sum(f["contribution"] for f in factors)

    if total >= 70:
        interp = "URGENT — High-impact brief. Multiple critical gaps + strong entity anchor points."
    elif total >= 40:
        interp = "IMPORTANT — Several gaps to address. Solid entity context available."
    elif total >= 20:
        interp = "ROUTINE — Minor fixes needed. Light entity anchoring."
    else:
        interp = "LOW PRIORITY — Page is in good shape."

    return {
        "score": round(total, 1),
        "factors": factors,
        "interpretation": interp,
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Three-Way Join Content Brief Generator"
    )
    parser.add_argument("--url", help="Target page URL (required unless --all-urls)")
    parser.add_argument("--output", help="Custom output path")
    parser.add_argument("--cap", type=int, default=8, help="Injection cap (default: 8)")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--all-urls", action="store_true",
        help="Generate briefs for all real pages in gap report"
    )
    args = parser.parse_args()

    if not args.url and not args.all_urls:
        parser.error("Either --url or --all-urls is required")

    engine = ThreeWayJoin()

    if args.all_urls:
        rule_results = engine._gap.get("rule_results", [])
        urls = [r["url"] for r in rule_results]
        print(f"📋 Generating briefs for {len(urls)} pages...")
        for url in urls:
            try:
                brief = engine.build(url, cap=args.cap)
                out_path = _save_brief(brief, args.format, args.output)
                print(f"  ✅ {url.split('/')[-1][:50]} → {out_path.name}")
            except Exception as e:
                print(f"  ❌ {url}: {e}")
        return

    brief = engine.build(args.url, cap=args.cap)
    out_path = _save_brief(brief, args.format, args.output)

    m = brief["meta"]
    s1 = brief["stream_1_gaps"]
    s2 = brief["stream_2_directives"]
    s3 = brief["stream_3_entities"]

    print(f"\n✅ Brief generated: {out_path}")
    print(f"   Priority Score: {m['priority_score']['score']:.0f}/100")
    print(f"   Deterministic gaps: {s1['det_fail_count']}/{s1['total_det_checks']}")
    print(f"   Kernel gaps: {s1['kernel_fail_count']}")
    print(f"   Directives injected: {len(s2['injected'])}/{s2['injection_cap']} cap")
    print(f"   Anchor entities: {len(s3['anchor_entities'])}")
    print(f"   Contaminated filtered: {len(s3['contaminated_on_page'])}")


def _save_brief(brief: dict, fmt: str, custom_path: Optional[str] = None) -> Path:
    """Save brief to disk."""
    slug = brief["meta"]["slug"].replace("/", "-")
    ts = brief["meta"]["generated_at"][:10]

    if custom_path:
        out_path = Path(custom_path)
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ext = "md" if fmt == "markdown" else "json"
        out_path = OUTPUT_DIR / f"brief-{slug}-{ts}.{ext}"

    if fmt == "json":
        out_path.write_text(json.dumps(brief, indent=2, default=str))
    else:
        engine = ThreeWayJoin()
        md = engine.format_markdown(brief)
        out_path.write_text(md)

    return out_path


if __name__ == "__main__":
    main()
