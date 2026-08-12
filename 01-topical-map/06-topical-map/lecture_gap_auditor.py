#!/usr/bin/env python3
"""
Lecture Gap Auditor — Cross-references Phase 1-5 outputs against 88 Koray lecture transcripts.
Treats lectures as a Semantic Patch Layer. Produces incremental patches, never overwrites.

Requires: koray-lectures LightRAG on port 8014, all 88 transcripts processed.
Usage: python3 lecture_gap_auditor.py [--fast]
"""
import requests
import json
import time
import sys
from pathlib import Path

# === CONFIG ===
LECTURE_RAG = "http://localhost:8014"
REPO_ROOT = Path("/home/steve/SEO-quann.homes")
BLUEPRINT_PATH = REPO_ROOT / "master-operating-blueprint.json"
OUTPUT_DIR = REPO_ROOT / "06-topical-map"
OLLAMA_CHAT = "http://192.168.4.148:11434/v1/chat/completions"
COMPARISON_MODEL = "deepseek-r1:7b-qwen-distill-q4_K_M"  # fast, free, local — good for comparison judgments

def load_blueprint():
    with open(BLUEPRINT_PATH) as f:
        return json.load(f)

def query_lectures(query: str, mode: str = "mix", top_k: int = 5) -> str:
    """Query the lecture LightRAG graph."""
    try:
        resp = requests.post(f"{LECTURE_RAG}/query", json={
            "query": query,
            "mode": mode,
            "only_context": True
        }, timeout=60)
        data = resp.json()
        # LightRAG returns different shapes — handle both
        if "data" in data:
            return data["data"]
        elif "response" in data:
            return data["response"]
        else:
            return str(data)
    except Exception as e:
        return f"ERROR: {e}"

def llm_compare(claim: str, lecture_context: str) -> dict:
    """Use fast local LLM to compare a claim against lecture context."""
    prompt = f"""You are auditing an SEO framework against Koray Gubur's lecture transcripts.

CLAIM FROM OUR FRAMEWORK OUTPUT:
{claim}

RELEVANT LECTURE CONTEXT (from Koray's lectures):
{lecture_context[:4000]}

Compare the claim to the lecture context. Does the lecture add any nuance, constraint, or methodology detail that our claim is MISSING? Classify as:

- MATCH: Lecture says the same thing — no new nuance.
- PATCH: Lecture adds a specific detail, constraint, or nuance our claim doesn't capture. Describe the missing detail.
- GAP: Our claim covers a topic the lecture discusses but with a fundamentally different approach or additional step. Describe what's missing.
- NOT_FOUND: The lecture context doesn't address this claim's topic.

Respond ONLY with JSON:
{{"classification": "MATCH|PATCH|GAP|NOT_FOUND", "missing_detail": "concise description of what's missing (empty for MATCH/NOT_FOUND)", "confidence": "high|medium|low", "lecture_reference": "any lecture number or timestamp visible in context"}}"""

    try:
        resp = requests.post(OLLAMA_CHAT, json={
            "model": COMPARISON_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }, timeout=120)
        
        text = resp.json()["choices"][0]["message"]["content"]
        # Extract JSON from response
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"classification": "ERROR", "missing_detail": text[:200], "confidence": "low", "lecture_reference": ""}
    except Exception as e:
        return {"classification": "ERROR", "missing_detail": str(e)[:200], "confidence": "low", "lecture_reference": ""}

def extract_phase_claims(blueprint: dict) -> dict:
    """Extract key claims/rules from each phase for auditing."""
    claims = {}
    
    phases = blueprint.get("phase_roadmap", {}).get("phases", [])
    
    for phase in phases:
        pid = phase["id"]
        if pid == 0 or pid >= 6:  # Skip prerequisites and pending phases
            continue
        
        phase_claims = []
        name = phase["name"]
        frameworks = phase.get("frameworks", [])
        outputs = phase.get("key_outputs", [])
        note = phase.get("methodology_note", "")
        
        # Phase-specific claim extraction
        if pid == 1:
            phase_claims = [
                "Vocabulary extraction should use live SERP corpus mining, not WordNet or lexical databases",
                "Domain vocabulary bank must include government program entities, tax districts, regional submarkets",
                "Seed queries must be auto-generated from Domain KG anchor entities, never hardcoded",
                "Copywriter manual should include predicate templates with Texas-specific examples",
                "Entity glossary should define every domain term for copywriters with zero domain knowledge",
                "Competitor corpus from live SERPs provides the frequency-weighted term extraction foundation",
                "Content quality rules include sentence structure, information gain, and first-100-words keyword placement"
            ]
        elif pid == 2:
            phase_claims = [
                "JSON-LD schema must include @id, @type, sameAs, and schema:subjectOf for entity disambiguation",
                "sameAs manifest should link all verified external profiles (Facebook, LinkedIn, HAR, Realty.com, Yelp)",
                "Entity contamination (wrong brokerage on external profiles) must be fixed before creating new profiles",
                "Knowledge Graph panel requires consistent NAP (Name, Address, Phone) across all profile URLs",
                "RealEstateAgent schema type should be used for individual agent entities, not just Organization",
                "Conversion architecture maps user journey from informational query → entity recognition → trust → contact"
            ]
        elif pid == 3:
            phase_claims = [
                "PageRank simulation on internal link graph identifies sink pages and ranking distribution",
                "Boolean retrieval model matrix is foundational for understanding term presence/absence in index",
                "RankBrain query embedding signals should be mapped for top buyer-agent queries",
                "Internal links should flow PageRank from high-authority pages to deep content pages",
                "Information retrieval diagnostics reveal which pages are invisible to crawlers"
            ]
        elif pid == 4:
            phase_claims = [
                "Entity relationship graph connects central entity (agent) to all attribute/context entities",
                "Contextual bridges are the semantic pathways connecting entities: Quan↔Katy, Quan↔Relocation, etc.",
                "Entity disambiguation matrix identifies contaminated, duplicate, and missing external profiles",
                "Attribute coverage analysis checks whether Domain KG entity attributes map to schema.org properties",
                "Entity salience ranking uses edge weight and centrality to identify the most important entities",
                "Information gaps detect where entities have no dedicated content coverage"
            ]
        elif pid == 5:
            phase_claims = [
                "EAV (Entity-Attribute-Value) triples should normalize to schema.org JSON-LD properties",
                "Internal linking matrix connects all 15 pages via 6 contextual bridges + centroid hierarchy",
                "Schema normalization maps domain-specific attributes to standard schema.org vocabulary",
                "Centroid-based topological traversal determines content creation order",
                "Multi-chunk verification uses BM25 + context embeddings for content gap detection",
                "Internal links should use descriptive anchor text matching the target page's primary entity"
            ]
        
        claims[pid] = {
            "name": name,
            "frameworks": frameworks,
            "key_outputs": outputs,
            "claims": phase_claims
        }
    
    return claims

def run_audit(blueprint: dict, fast_mode: bool = False):
    """Main audit: query lectures for each claim, compare, classify."""
    phase_claims = extract_phase_claims(blueprint)
    
    findings = {}
    total_claims = sum(len(pc["claims"]) for pc in phase_claims.values())
    patches_found = []
    gaps_found = []
    
    print(f"🔍 Auditing {total_claims} claims across {len(phase_claims)} phases against 88 lecture transcripts")
    print(f"   Fast mode: {fast_mode} | LLM: {COMPARISON_MODEL}\n")
    
    claim_num = 0
    for pid, phase_info in sorted(phase_claims.items()):
        print(f"--- PHASE {pid}: {phase_info['name']} ---")
        phase_findings = []
        
        for claim in phase_info["claims"]:
            claim_num += 1
            
            # Construct query for this claim
            # Extract key topic words for focused retrieval
            topic = claim[:120]  # First 120 chars captures the core concept
            
            # Query the lecture graph
            ctx = query_lectures(topic, mode="mix")
            ctx_preview = ctx[:200].replace("\n", " ")
            
            # Compare claim vs lecture context
            result = llm_compare(claim, ctx)
            classification = result.get("classification", "ERROR")
            detail = result.get("missing_detail", "")
            confidence = result.get("confidence", "low")
            lecture_ref = result.get("lecture_reference", "")
            
            finding = {
                "claim_num": claim_num,
                "claim": claim,
                "classification": classification,
                "missing_detail": detail,
                "confidence": confidence,
                "lecture_reference": lecture_ref,
                "context_preview": ctx_preview
            }
            phase_findings.append(finding)
            
            icon = {"MATCH": "✅", "PATCH": "🔧", "GAP": "🕳️", "NOT_FOUND": "➖", "ERROR": "❌"}.get(classification, "❓")
            print(f"  {icon} [{classification:9s}] C{claim_num:02d}: {claim[:80]}...")
            if classification in ("PATCH", "GAP"):
                print(f"         Detail: {detail[:150]}")
                if classification == "PATCH":
                    patches_found.append(finding)
                else:
                    gaps_found.append(finding)
            
            time.sleep(0.5)  # Rate limit
        
        findings[pid] = {
            "phase_name": phase_info["name"],
            "claims_total": len(phase_info["claims"]),
            "findings": phase_findings,
            "matches": sum(1 for f in phase_findings if f["classification"] == "MATCH"),
            "patches": sum(1 for f in phase_findings if f["classification"] == "PATCH"),
            "gaps": sum(1 for f in phase_findings if f["classification"] == "GAP"),
            "not_found": sum(1 for f in phase_findings if f["classification"] == "NOT_FOUND")
        }
        
        summary = findings[pid]
        print(f"  → {summary['matches']} matches, {summary['patches']} patches, {summary['gaps']} gaps, {summary['not_found']} not found\n")
    
    # Compute overall stats
    total_matches = sum(f["matches"] for f in findings.values())
    total_patches = sum(f["patches"] for f in findings.values())
    total_gaps = sum(f["gaps"] for f in findings.values())
    total_not_found = sum(f["not_found"] for f in findings.values())
    
    print(f"{'='*60}")
    print(f"AUDIT COMPLETE")
    print(f"  Phases audited: {len(findings)}")
    print(f"  Total claims: {total_claims}")
    print(f"  ✅ Matches (confirmed): {total_matches}")
    print(f"  🔧 Patches (missing nuance): {total_patches}")
    print(f"  🕳️  Gaps (fundamental differences): {total_gaps}")
    print(f"  ➖ Not found (lectures silent): {total_not_found}")
    print(f"{'='*60}")
    
    # Save full report
    report = {
        "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "88 Koray lecture transcripts via LightRAG port 8014",
        "comparison_model": COMPARISON_MODEL,
        "fast_mode": fast_mode,
        "total_claims": total_claims,
        "summary": {
            "matches": total_matches,
            "patches": total_patches,
            "gaps": total_gaps,
            "not_found": total_not_found
        },
        "phases": findings,
        "patch_manifest": patches_found,
        "gap_manifest": gaps_found
    }
    
    report_path = OUTPUT_DIR / "lecture-audit-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved: {report_path}")
    
    return report

def generate_human_summary(report: dict):
    """Generate markdown summary for the Review Gate."""
    s = report["summary"]
    patches = report["patch_manifest"]
    gaps = report["gap_manifest"]
    
    md = f"""# Lecture Gap Audit — Review Gate Summary

**Audit completed:** {report['audit_timestamp']}  
**Source:** {report['source']}  
**Model:** {report['comparison_model']}  
**Claims audited:** {report['total_claims']} across 5 phases

## Results

| Classification | Count |
|---|---|
| ✅ Confirmed | {s['matches']} |
| 🔧 Needs Patch | {s['patches']} |
| 🕳️ Gap Detected | {s['gaps']} |
| ➖ Not Addressed | {s['not_found']} |

"""
    
    if patches:
        md += "## 🔧 Patches Needed (Missing Nuances)\n\n"
        md += "These are specific details or constraints from Koray's lectures that our Phase 1-5 outputs don't capture. They should be **patched incrementally** — no rebuild required.\n\n"
        for i, p in enumerate(patches, 1):
            md += f"### Patch {i}: {p['claim'][:80]}...\n"
            md += f"- **Missing:** {p['missing_detail']}\n"
            md += f"- **Source:** {p['lecture_reference']}\n"
            md += f"- **Confidence:** {p['confidence']}\n\n"
    
    if gaps:
        md += "## 🕳️ Structural Gaps (New Territory)\n\n"
        md += "These represent areas where the lectures describe an approach fundamentally different from what our phases encode. They may require new rules or methodology additions before Phase 6.\n\n"
        for i, g in enumerate(gaps, 1):
            md += f"### Gap {i}: {g['claim'][:80]}...\n"
            md += f"- **Missing:** {g['missing_detail']}\n"
            md += f"- **Source:** {g['lecture_reference']}\n"
            md += f"- **Confidence:** {g['confidence']}\n\n"
    
    if not patches and not gaps:
        md += "## ✅ No Changes Needed\n\nAll claims confirmed or lecture transcripts don't address them. Our Phase 1-5 outputs are complete for Phase 6 entry.\n"
    
    md += "---\n*Generated by lecture-gap-auditor v1.0*"
    
    summary_path = OUTPUT_DIR / "lecture-audit-summary.md"
    with open(summary_path, "w") as f:
        f.write(md)
    print(f"📄 Human summary saved: {summary_path}")
    
    return md

if __name__ == "__main__":
    fast_mode = "--fast" in sys.argv
    bp = load_blueprint()
    report = run_audit(bp, fast_mode=fast_mode)
    summary = generate_human_summary(report)
    print("\n" + summary)
