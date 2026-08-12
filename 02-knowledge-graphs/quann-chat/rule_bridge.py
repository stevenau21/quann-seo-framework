#!/usr/bin/env python3
"""
Bifurcated RuleBridge — connects Tier 1 (GROUNDED) flashcards from Phase 5
into Kernel v2.1's gap audit and content brief generation.

ARCHITECTURE:
  ┌──────────────────────────────────────────────────────────────────┐
  │                     RuleBridge (this module)                     │
  ├──────────────────────────────────────────────────────────────────┤
  │  classify_and_route()                                           │
  │       ├─ Deterministic Track (28 cards → regex/count checks)    │
  │       │    • run_deterministic_checks(url, content, page_type)  │
  │       │    • Zero API calls, pure local computation             │
  │       └─ Directive Track (116 cards → prompt injection)         │
  │            • route_directives(page_type, failed_categories, cap)│
  │            • Capped at 5-8 directives (Injection Cap)           │
  └──────────────────────────────────────────────────────────────────┘
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Optional

SCHEMA_PATH = Path(__file__).parent / "bridge_schema.json"

# ── Compiled regex patterns for deterministic checks ──
# Using regular (non-raw) strings avoids the \"-inside-r-string trap.
RE_CANONICAL = re.compile(r'<link[^>]*rel=["\x27]canonical["\x27]', re.I)
RE_PRELOAD = re.compile(r'rel=["\x27]preload["\x27].*?as=["\x27](\w+)["\x27]', re.I)
RE_SCRIPT_DEFER = re.compile(r'<script[^>]*(?:defer|async)[^>]*>', re.I)
RE_SCRIPT_SRC = re.compile(r'<script[^>]*src=', re.I)
RE_SCRIPT_EXTERNAL = re.compile(r'<script[^>]*src=["\x27]https?://', re.I)
RE_CDN = re.compile(r'(cdn\.|cloudfront|fastly|bunnycdn|jsdelivr|unpkg)', re.I)
RE_SESSION_ID = re.compile(r'href=["\x27][^"\x27]*[?&](?:session_?id|sid|phpsessid)=[^"\x27]+["\x27]', re.I)
RE_CONTENT_VISIBILITY = re.compile(r'content-visibility:\s*auto', re.I)
RE_LEGACY_ANIM = re.compile(r'(?:top|left)\s*:\s*\d+(?:px|%|em|rem).*?(?:@keyframes|animation|transition)', re.I)
RE_INLINE_POSITION = re.compile(r'style=["\x27][^"\x27]*(?:top|left)\s*:\s*\d+', re.I)
RE_TRANSFORM = re.compile(r'transform\s*:', re.I)
RE_SPA_ROOT = re.compile(r'<div\s+id=["\x27]root["\x27]\s*>', re.I)
RE_EMPTY_ROOT = re.compile(r'<div\s+id=["\x27]root["\x27]\s*></div>', re.I)
RE_HEAD = re.compile(r'<head[^>]*>(.*?)</head>', re.I | re.S)
RE_BLOCKING_CSS = re.compile(r'<link[^>]*rel=["\x27]stylesheet["\x27]', re.I)
RE_BLOCKING_JS = re.compile(r'<script[^>]*src=', re.I)
RE_PRELOAD_HEAD = re.compile(r'rel=["\x27]preload["\x27]', re.I)
RE_REVIEW_SCHEMA = re.compile(r'(?:Review|AggregateRating|reviewRating)["\x27]', re.I)
RE_REVIEW_TEXT = re.compile(r'(?:rating|review|star|testimonial)', re.I)
RE_EMPTY_STYLE = re.compile(r'<style[^>]*>\s*</style>', re.I)
RE_JQUERY = re.compile(r'jquery', re.I)
RE_BOOTSTRAP = re.compile(r'bootstrap', re.I)
RE_VIEWPORT = re.compile(r'<meta[^>]*name=["\x27]viewport["\x27]', re.I)
RE_IMG_ALL = re.compile(r'<img[^>]+>', re.I)
RE_IMG_ALT = re.compile(r'<img[^>]*alt=["\x27][^"\x27]+["\x27]', re.I)
RE_IMG_ALT_EMPTY = re.compile(r'<img[^>]*alt=["\x27]\s*["\x27]', re.I)
RE_HREFLANG = re.compile(r'<link[^>]*rel=["\x27]alternate["\x27].*?hreflang=', re.I)
RE_LOCALBUSINESS = re.compile(r'(?:LocalBusiness|RealEstateAgent|Place|PostalAddress)["\x27]', re.I)
RE_FACETED = re.compile(r'href=["\x27][^"\x27]*\?(?:filter|sort|page|category|tag|color|size)=[^"\x27]+["\x27]', re.I)
RE_HTML_TAG = re.compile(r'<[^>]+>')


class RuleBridge:
    """Bifurcated bridge connecting Koray Gubur Tier 1 rules to Kernel v2.1."""

    def __init__(self, schema_path: Optional[Path] = None):
        path = schema_path or SCHEMA_PATH
        with open(path) as f:
            self.schema = json.load(f)

        self._check_registry = self.schema["deterministic_check_registry"]
        self._router = self.schema["directive_router"]
        self._directive_categories = self.schema["directive_injection_categories"]

        self._d_index = {}
        for rule in self.schema["rules"]:
            if rule["track"] == "deterministic":
                m = rule["check"]["method"]
                if m not in self._d_index:
                    self._d_index[m] = rule["check"]

        self._dir_index = {}
        for rule in self.schema["rules"]:
            if rule["track"] == "directive":
                self._dir_index[rule["card_id"]] = rule

        self._category_applies = {}
        for cat, defn in self._directive_categories.items():
            self._category_applies[cat] = set(defn["applies_to"])

        self._fw_directives = {}
        for fw, ids in self._router["by_framework"].items():
            self._fw_directives[fw] = ids

        self._det_cat_to_dir_cat = {
            "technical_seo": ["content_strategy", "methodology_depth"],
            "local_seo": ["entity_requirements", "conversion_optimization"],
            "content_depth": ["methodology_depth", "case_study_format", "content_strategy"],
            "multilingual_seo": ["multilingual_consistency", "content_strategy"],
        }

    # ── DETERMINISTIC TRACK ──────────────────────────────────────────

    def run_deterministic_checks(self, url: str, content: str, page_type: str) -> list[dict]:
        results = []
        for method, check_def in self._check_registry.items():
            if page_type not in check_def["applies_to"]:
                continue
            rule_entry = None
            for r in self.schema["rules"]:
                if r["track"] == "deterministic" and r["check"]["method"] == method:
                    rule_entry = r
                    break
            check_fn = getattr(self, f"_check_{method}", None)
            if check_fn is None:
                result = {"status": "unverified", "detail": f"No implementation for '{method}'"}
            else:
                result = check_fn(content)
            rule_id = rule_entry["card_id"] if rule_entry else f"bridge_{method}"
            rule_text = rule_entry["content"] if rule_entry else check_def.get("fix_directive", "")
            results.append({
                "rule_id": f"bridge_{rule_id}",
                "rule": rule_text,
                "status": result["status"],
                "detail": result.get("detail", ""),
                "fix_directive": check_def.get("fix_directive", ""),
                "priority": check_def.get("priority", "medium"),
                "bridge": True,
                "method": method,
                "category": check_def.get("category", ""),
            })
        return results

    # ── DIRECTIVE ROUTER (Injection Cap) ─────────────────────────────

    def route_directives(
        self, page_type: str,
        failed_deterministic_categories: Optional[list[str]] = None,
        cap: int = 8,
    ) -> list[dict]:
        failed_cats = failed_deterministic_categories or []
        related_cats = set()
        for dc in failed_cats:
            related = self._det_cat_to_dir_cat.get(dc, [])
            related_cats.update(related)

        direct_hits = []
        for cat in related_cats:
            if cat not in self._category_applies:
                continue
            if page_type not in self._category_applies[cat]:
                continue
            for cid in self._router["by_category"].get(cat, []):
                r = self._dir_index.get(cid)
                if r:
                    direct_hits.append({
                        "card_id": cid, "content": r["content"],
                        "framework": r["framework"], "category": cat,
                        "prompt_fragment": r["inject"]["prompt_fragment"],
                        "priority": "direct_hit",
                    })

        page_matches = []
        page_cats = self._router["by_page_type"].get(page_type, {})
        for cat, card_ids in page_cats.items():
            if cat in related_cats:
                continue
            for cid in card_ids:
                r = self._dir_index.get(cid)
                if r:
                    page_matches.append({
                        "card_id": cid, "content": r["content"],
                        "framework": r["framework"], "category": cat,
                        "prompt_fragment": r["inject"]["prompt_fragment"],
                        "priority": "page_match",
                    })

        framework_counts = Counter(d["framework"] for d in direct_hits)
        top_fw = framework_counts.most_common(1)[0][0] if framework_counts else None
        top_level = []
        if top_fw and top_fw in self._fw_directives:
            already = {d["card_id"] for d in direct_hits + page_matches}
            for cid in self._fw_directives[top_fw]:
                r = self._dir_index.get(cid)
                if r and cid not in already:
                    cat = r["inject"]["category"]
                    if page_type in self._category_applies.get(cat, set()):
                        top_level.append({
                            "card_id": cid, "content": r["content"],
                            "framework": r["framework"], "category": cat,
                            "prompt_fragment": r["inject"]["prompt_fragment"],
                            "priority": "top_level",
                        })

        n_direct = min(len(direct_hits), int(cap * 0.5))
        n_page = min(len(page_matches), int(cap * 0.3))
        n_top = min(len(top_level), cap - n_direct - n_page)
        selected = direct_hits[:n_direct] + page_matches[:n_page] + top_level[:n_top]

        for pool in [direct_hits, page_matches, top_level]:
            for d in pool:
                if d not in selected and len(selected) < cap:
                    selected.append(d)

        return selected[:cap]

    def build_directive_prompt_section(self, directives: list[dict]) -> str:
        if not directives:
            return ""
        by_cat = defaultdict(list)
        for d in directives:
            cat_label = self._directive_categories.get(d["category"], {}).get("label", d["category"])
            by_cat[cat_label].append(d)
        sections = [
            "## 🏗️ Architectural Directives (Koray Gubur — Phase 5 Tier 1)\n",
            f"_The following {len(directives)} directives are sourced from the Koray Gubur "
            "Architect Extraction Pipeline. They represent grounded, computable rules "
            "validated against source material. Adhere to these when writing this content._\n",
        ]
        for cat_label, dirs in by_cat.items():
            sections.append(f"### {cat_label}\n")
            for i, d in enumerate(dirs, 1):
                sections.append(f"{i}. {d['prompt_fragment']}\n")
            sections.append("")
        return "\n".join(sections)

    # ── DETERMINISTIC CHECK IMPLEMENTATIONS ─────────────────────────

    def _check_canonical_url_present(self, content: str) -> dict:
        found = RE_CANONICAL.search(content)
        return {"status": "pass" if found else "fail",
                "detail": f"Canonical URL tag {'found' if found else 'NOT found'}"}

    def _check_preload_key_requests(self, content: str) -> dict:
        matches = RE_PRELOAD.findall(content)
        return {"status": "pass" if matches else "fail",
                "detail": f"Preload hints: {len(matches)} ({', '.join(matches) if matches else 'none'})"}

    def _check_javascript_deferred(self, content: str) -> dict:
        deferred = len(RE_SCRIPT_DEFER.findall(content))
        all_scripts = len(RE_SCRIPT_SRC.findall(content))
        external = len(RE_SCRIPT_EXTERNAL.findall(content))
        return {"status": "pass" if deferred > 0 or all_scripts == 0 else "fail",
                "detail": f"Deferred scripts: {deferred}/{all_scripts} ({external} external)"}

    def _check_cdn_detected(self, content: str) -> dict:
        found = RE_CDN.findall(content)
        return {"status": "pass" if found else "fail",
                "detail": f"CDN indicators: {', '.join(set(found)) if found else 'none detected'}"}

    def _check_no_session_ids_in_urls(self, content: str) -> dict:
        matches = RE_SESSION_ID.findall(content)
        return {"status": "pass" if not matches else "fail",
                "detail": f"Session IDs in URLs: {len(matches)} {'found' if matches else 'none'}"}

    def _check_content_visibility_auto(self, content: str) -> dict:
        found = RE_CONTENT_VISIBILITY.search(content)
        return {"status": "pass" if found else "fail",
                "detail": f"content-visibility: auto {'found' if found else 'NOT found'}"}

    def _check_no_legacy_position_animations(self, content: str) -> dict:
        legacy = len(RE_LEGACY_ANIM.findall(content))
        inline = len(RE_INLINE_POSITION.findall(content))
        ok = legacy == 0 and inline < 5
        return {"status": "pass" if ok else "fail",
                "detail": f"Legacy position animations: {legacy} keyframes, {inline} inline — {'pass' if ok else 'consider transform'}"}

    def _check_transform_animations(self, content: str) -> dict:
        t_count = len(RE_TRANSFORM.findall(content))
        top_left = len(RE_LEGACY_ANIM.findall(content))
        if t_count == 0 and top_left == 0:
            return {"status": "unverified",
                    "detail": "No animations detected — transform check skipped"}
        return {"status": "pass" if t_count > 0 and top_left == 0 else "fail",
                "detail": f"Transform animations: {t_count} found, legacy top/left keyframes: {top_left}"}

    def _check_ssr_or_prerender(self, content: str) -> dict:
        empty = RE_EMPTY_ROOT.search(content)
        has_content = len(content) > 500
        return {"status": "pass" if not empty and has_content else "fail",
                "detail": f"SPA root empty: {'yes' if empty else 'no'}, content length: {len(content)} chars"}

    def _check_critical_request_chain_short(self, content: str) -> dict:
        head_m = RE_HEAD.search(content)
        head = head_m.group(1) if head_m else content[:3000]
        css = len(RE_BLOCKING_CSS.findall(head))
        js = len(RE_BLOCKING_JS.findall(head))
        pre = len(RE_PRELOAD_HEAD.findall(head))
        score = css + js - pre
        return {"status": "pass" if score <= 3 else "fail",
                "detail": f"Render-blocking chain depth: CSS={css} + JS={js} - preloads={pre} = {score} (target ≤3)"}

    def _check_review_schema_present(self, content: str) -> dict:
        found = RE_REVIEW_SCHEMA.search(content)
        has_text = RE_REVIEW_TEXT.search(content)
        return {"status": "pass" if found else "fail" if has_text else "unverified",
                "detail": f"Review schema: {'found' if found else 'NOT found'}. Ratings in text: {'yes' if has_text else 'no'}"}

    def _check_dead_code_indicators(self, content: str) -> dict:
        empty = len(RE_EMPTY_STYLE.findall(content))
        jq = len(RE_JQUERY.findall(content))
        bs = len(RE_BOOTSTRAP.findall(content))
        issues = []
        if empty > 0:
            issues.append(f"{empty} empty <style> blocks")
        if jq > 2:
            issues.append(f"{jq} jQuery references")
        if bs > 3:
            issues.append(f"{bs} Bootstrap references (possible duplication)")
        return {"status": "pass" if not issues else "fail",
                "detail": f"Dead code indicators: {', '.join(issues) if issues else 'none'}"}

    def _check_viewport_meta_present(self, content: str) -> dict:
        found = RE_VIEWPORT.search(content)
        return {"status": "pass" if found else "fail",
                "detail": f"Viewport meta tag: {'found' if found else 'MISSING'}"}

    def _check_image_alt_present(self, content: str) -> dict:
        all_imgs = len(RE_IMG_ALL.findall(content))
        with_alt = len(RE_IMG_ALT.findall(content))
        empty_alt = len(RE_IMG_ALT_EMPTY.findall(content))
        pct = round(100 * with_alt / max(all_imgs, 1), 1)
        return {"status": "pass" if pct >= 80 else "fail" if all_imgs > 0 else "unverified",
                "detail": f"Image alt text: {with_alt}/{all_imgs} ({pct}%), empty alt: {empty_alt}"}

    def _check_hreflang_present(self, content: str) -> dict:
        found = RE_HREFLANG.search(content)
        return {"status": "pass" if found else "unverified",
                "detail": f"Hreflang annotations: {'found' if found else 'NOT found (only relevant for multilingual sites)'}"}

    def _check_localbusiness_schema_present(self, content: str) -> dict:
        found = RE_LOCALBUSINESS.search(content)
        return {"status": "pass" if found else "fail",
                "detail": f"LocalBusiness schema: {'found' if found else 'NOT found'}"}

    def _check_faceted_nav_clean(self, content: str) -> dict:
        faceted = RE_FACETED.findall(content)
        return {"status": "pass" if len(faceted) == 0 else "fail",
                "detail": f"Faceted nav params in URLs: {len(faceted)} {'instances' if faceted else 'none'}"}

    def _check_thin_content(self, content: str) -> dict:
        text = RE_HTML_TAG.sub(" ", content)
        words = len(text.split())
        return {"status": "pass" if words >= 300 else "fail",
                "detail": f"Word count: {words} (thin threshold: 300)"}


def bridge_page_types(page_type: str) -> str:
    """Map kernel v2.1 page categories to bridge page types."""
    mapping = {
        "blog": "blog_post", "blog_index": "blog_post", "blog_post": "blog_post",
        "service": "service", "homepage": "homepage", "about": "about",
        "legal": "legal", "policy": "policy",
    }
    return mapping.get(page_type, page_type)


def build_bridge_gap_report(
    bridge_results: list[dict], failing_deterministic: list[dict],
    directives: list[dict], url: str, page_type: str,
) -> dict:
    fail_count = sum(1 for r in bridge_results if r["status"] == "fail")
    pass_count = sum(1 for r in bridge_results if r["status"] == "pass")
    total = len(bridge_results)
    return {
        "url": url, "page_type": page_type, "bridge_version": "1.0.0",
        "deterministic_checks_total": total,
        "deterministic_checks_passed": pass_count,
        "deterministic_checks_failed": fail_count,
        "compliance_pct": round(100 * pass_count / max(total, 1), 1),
        "failing_checks": [{
            "rule_id": r["rule_id"], "rule": r["rule"],
            "detail": r["detail"], "fix_directive": r["fix_directive"],
            "priority": r["priority"],
        } for r in failing_deterministic],
        "directives_injected": len(directives),
        "directives": [{
            "content": d["content"], "framework": d["framework"],
            "priority": d["priority"],
        } for d in directives],
        "directives_prompt_section": RuleBridge().build_directive_prompt_section(directives),
    }


# ── Smoke test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    rb = RuleBridge()
    print(f"✅ RuleBridge loaded: {len(rb._d_index)} deterministic checks, {len(rb._dir_index)} directives")

    mock = """<html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="canonical" href="https://quann.homes/blog/test">
    <link rel="preload" href="font.woff2" as="font">
    <script src="app.js" defer></script>
</head><body>
    <h1>First-Time Home Buyer Guide for Houston and Katy</h1>
    <p>""" + ("Content to reach word count. " * 100) + """</p>
    <img src="house.jpg" alt="Beautiful Katy home">
    <a href="https://quann.homes/contact">Contact Quan</a>
</body></html>"""

    print("\n📋 Deterministic checks (blog_post):")
    results = rb.run_deterministic_checks("https://quann.homes/blog/test", mock, "blog_post")
    for r in results:
        icon = "✅" if r["status"] == "pass" else "❌" if r["status"] == "fail" else "⚠️"
        print(f"  {icon} {r['method']}: {r['detail']}")

    p = sum(1 for r in results if r["status"] == "pass")
    print(f"  PASS: {p}/{len(results)}")

    failed_cats = [r["category"] for r in results if r["status"] == "fail"]
    print(f"\n🧠 Directive routing (failed_cats={failed_cats}):")
    dirs = rb.route_directives("blog_post", failed_cats, cap=8)
    for d in dirs:
        print(f"  [{d['priority']}] {d['content'][:90]}...")
    print(f"  Selected: {len(dirs)} directives")

    print(f"\n✅ Smoke test complete")
