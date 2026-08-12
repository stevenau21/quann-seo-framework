---
name: lecture-gap-auditor
description: Cross-reference completed Phase 1-5 SEO framework outputs against uncompressed Koray lecture transcripts in LightRAG. Detects missing rules, constraints, methodology nuances, and schema properties. Produces incremental patches — never overwrites. Treats lectures as a semantic patch layer, NOT a rebuild source. Designed for the quann.homes SEO Topical Authority Framework.
triggers: ["audit against lectures", "gap audit", "check lectures for missing", "patch from lectures", "lecture-gap", "cross-reference lectures"]
---

# Lecture Gap Auditor

## Purpose

This skill audits completed SEO framework phases (1-5) against the uncompressed Koray Gubur lecture transcripts (~88 files, ~600 minutes) in LightRAG. It treats the lectures as a **Semantic Patch Layer** — identifying missing nuances, constraints, and structural rules that existing phase outputs do not capture.

**The rule:** never rebuild. Only patch. The phases are grounded in live Texas real estate corpus data and structurally sound. The lectures augment, not replace.

## When To Use

After ingesting Koray lecture transcripts into a dedicated LightRAG instance and BEFORE Phase 6 (Topical Authority). Run this audit to catch missing methodology details before Phase 6 synthesis begins.

## Architecture

```
┌──────────────────────────────────────────┐
│        Phase 1-5 Completed Outputs       │
│  (vocabulary, schemas, bridges, links)   │
└─────────────┬────────────────────────────┘
              │ extract core claims per phase
              ▼
┌──────────────────────────────────────────┐
│         Gap Audit Engine (Python)        │
│  ┌──────────────────────────────────┐    │
│  │ Per-phase:                        │    │
│  │  1. Extract phase claims/rules   │    │
│  │  2. Query lecture graph (8014)   │    │
│  │  3. LLM compares: new? missing?  │    │
│  │  4. Classify: PATCH / GAP / ✅   │    │
│  └──────────────────────────────────┘    │
└─────────────┬────────────────────────────┘
              │ audit report
              ▼
┌──────────────────────────────────────────┐
│         Incremental Patch Manifest       │
│  - Which file to patch                   │
│  - What to add (rule, constraint, etc.)  │
│  - Source citation (lecture, timestamp)  │
└──────────────────────────────────────────┘
```

## Audit Methodology

### Per-Phase Claim Extraction

For each completed phase, the auditor extracts a `claims` array — the key assertions, rules, and structural decisions that the phase output encodes.

**Phase 1** — Vocabulary + Data Infrastructure
- Claims: vocabulary terms, banned categories, predicate templates, entity glossary entries, seed query methodology

**Phase 2** — Knowledge Graph + Structured Data
- Claims: schema types, sameAs manifest, JSON-LD properties, entity descriptions, conversion architecture rules

**Phase 3** — Information Retrieval + Indexing
- Claims: PageRank methodology, Boolean matrix construction, RankBrain signal map, IR diagnostic rules

**Phase 4** — Entity Bridge + Relationship Graph
- Claims: entity relationship types, contextual bridge mappings, attribute coverage, disambiguation rules

**Phase 5** — Schema Normalization + Internal Linking
- Claims: EAV→schema.org mappings, linking matrix rules, centroid hierarchy, contextual bridge link patterns

### Lecture Query Construction

For each claim, construct a targeted query to the lecture LightRAG:

```
Query template: "What does Koray say about {claim_topic}? Are there specific rules, constraints, or methodology requirements?"

Query mode: "mix" (hybrid local+global retrieval)
Chunks: 5 (focused retrieval, not exhaustive)
```

### Gap Classification

| Class | Definition | Action |
|-------|-----------|--------|
| **MATCH** | Lecture says the same thing | No action — confirmed |
| **PATCH** | Lecture adds nuance/constraint not in phase output | Incrementally patch the relevant file with the new rule |
| **GAP** | Lecture describes a method/rule the phase entirely omits | Add new rule to the phase, flag for review |
| **NOT_FOUND** | Lecture doesn't address this topic | No action — phase may cover territory the lectures don't |

### PATCH Format

Every detected nuance is formatted as an incremental patch record:

```json
{
  "detection_id": "PHASE2-PATCH-001",
  "phase": 2,
  "file_to_patch": "06-topical-map/phase2-schemas.json",
  "claim_checked": "sameAs manifest should include Wikidata",
  "lecture_source": "Lecture 23 — Entity Resolution (42:15)",
  "nuance_found": "Koray emphasizes that sameAs should include schema:subjectOf pointing to the entity's Wikipedia page as well as Wikidata — not just Wikidata ID. This creates a bidirectional confirmation signal.",
  "classification": "PATCH",
  "suggested_patch": "Add schema:subjectOf property with Wikipedia URL to each entity's sameAs manifest entry"
}
```

## Implementation

### Script: `lecture_gap_auditor.py`

Located in: `/home/steve/SEO-quann.homes/06-topical-map/`

**Inputs:**
- `master-operating-blueprint.json` (phase definitions, outputs)
- Phase output files (vocabulary-bank.json, phase2-schemas.json, etc.)
- LightRAG endpoint: `http://localhost:8014` (koray-lectures)

**Outputs:**
- `lecture-audit-report.json` — full audit with per-phase findings
- `lecture-audit-summary.md` — human-readable summary
- Patch commands applied directly via `patch()` tool

**LLM for comparison:** Use `deepseek-v4-flash:cloud` for speed — comparing claims is a fast judgment task, not deep reasoning.

### Running

```bash
cd /home/steve/SEO-quann.homes/06-topical-map
python3 lecture_gap_auditor.py
```

Then apply patches with:
```python
patch(path=file, old_string=target, new_string=patched)
```

## Pitfalls

1. **Don't query the lecture graph for every single vocabulary term** — that's 94 queries, too slow. Group by phase and topic.
2. **Lecture transcripts may have OCR errors** — Koray speaks with an accent, transcripts may contain typos. Trust the LLM to infer meaning, don't require exact matches.
3. **Don't query the wrong LightRAG** — port 8014 ONLY. Port 8012 is the blog-post graph. Port 8011 is quann-chat.
4. **PATCH, not replace** — use `patch()` with targeted old_string, never `write_file()` for the whole file.
5. **Cite the lecture** — every patch must reference which lecture and approximate timestamp the nuance came from.

## Cross-Reference With

- `knowledge-synthesis-architecture` — the overall synthesis framework
- `corpus-driven-vocabulary-extraction` — Phase 1 methodology
- `architect-extraction-pipeline` — how Koray frameworks were originally extracted
