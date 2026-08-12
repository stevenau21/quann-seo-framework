# Brokerage Decontamination Protocol

## Trigger
Any SEO framework file referencing a brokerage that does NOT match the user-confirmed canonical value.

## Canonical Brokerage (as of 2026-05-25)
**Walzel Properties**

## Decontamination Sweep

Run before ANY content work or topical map construction:

```bash
grep -rl "REAL BROKERAGE\|Forever Realty\|Elevatus\|Truss" SEO-quann.homes/ --include="*.md" --include="*.json"
```

### Files to Patch (prescriptive — these MUST be corrected)

| File | Old Value | Action |
|---|---|---|
| `02-central-entity/central-entity.md` | REAL BROKERAGE (NAP, Awards, H1, Footer) | ✅ Patched to Walzel Properties |
| `04-eav-triples/eav-triples.md` | REAL BROKERAGE (Brokerage, Awards) | ✅ Patched to Walzel Properties |
| `09-research/proactive-entitization-strategy.md` | REAL BROKERAGE (Purpose, Wikidata, GBP, Schema) | ✅ Patched to Walzel Properties |
| `09-research/entity-disambiguation-plan.md` | REAL BROKERAGE (throughout) | ✅ Patched to Walzel Properties |
| `09-research/distributional-semantics.md` | REAL BROKERAGE (boilerplate, n-grams) | ✅ Patched to Walzel Properties |
| `03-web-entity/web-entity.md` | REAL BROKERAGE (NAP reference) | ✅ Patched to Walzel Properties |
| `06-topical-map/topical-map.md` | REAL BROKERAGE (spoke pages) | ✅ Patched to Walzel Properties |
| `pages/about-quan-nguyen.md` | REAL BROKERAGE (H1, body, awards) | ✅ Patched to Walzel Properties |
| `ALIGNMENT-AUDIT.md` | REAL BROKERAGE (footer verification) | ✅ Patched to Walzel Properties |
| `08-backlink-strategy/backlink-strategy.md` | REAL BROKERAGE (license, directory) | ✅ Patched to Walzel Properties |

### Files to KEEP AS-IS (documentary — these record what happened)

- `EXECUTION-ISSUES-LOG.md` — Documents ISSUE-029 (brokerage misidentification). These references are historical record, not prescriptive instructions.
- `entity-discovery.md` — Already corrected to Walzel Properties with methodology note about Framer image-based detection.
- `framework-report.md` — Records the error and correction for the SEO expert.

## Framer Site Detection Rule

On Framer-built sites: **the footer text can be YEARS behind the visual layer.** Brokerage may only appear in image logos. Never trust text extraction alone — always:

1. Visually inspect the site (browser_vision or screenshot)
2. Cross-reference with the owner's direct confirmation
3. Check external profiles for the most recent brokerage, then verify against the site

This caused ISSUE-029: three wrong brokerages propagated (Forever Realty → REAL BROKERAGE → Walzel Properties) before visual inspection caught the truth.
