# quann.homes Session Log — Key Learnings

**Part of:** seo-framework-execution skill  
**Session span:** 2026-05-24 through 2026-05-28 (5 sessions)  
**Repository:** /home/steve/SEO-quann.homes/

---

## Critical Discoveries

### The WordNet Disaster (Session 1 → Session 4 correction)

The Phase 1 vocabulary bank was initially built using WordNet 3.1 via NLTK. WordNet returned:
- "barony" and "feoff" as hyponyms of "estate"
- "trafficker" as a hypernym of "seller"
- "cliff dwelling" and "conjugal family" as hyponyms of "home"

These terms would have poisoned the copywriter's output and signaled spam to Google. The fix was rebuilding the vocabulary bank using DuckDuckGo SERP scraping of 26 competing domains — which revealed TSAHC, MUD, PID, Cinco Ranch, and other terms WordNet had zero knowledge of.

**Lesson:** WordNet is a 1985 lexical dictionary, not a search index. For SEO vocabulary extraction, Google's live index IS the only valid corpus.

### The Three Brokerages (Session 3-4)

Quan's brokerage was discovered in three stages:
1. **Forever Realty, LLC** — found on HAR.com, Realty.com, LinkedIn (first assumption: correct)
2. **REAL BROKERAGE** — found in quann.homes footer text (second assumption: site footer = truth)
3. **Walzel Properties** — seen in images/logos on quann.homes (truth, confirmed by owner)

The footer text was stale (previous brokerage), and external profiles were even more outdated. On Framer-built sites, the image layer is more current than the text layer because images are updated in the visual editor while footer text requires a separate manual edit.

**Lesson:** Never trust text extraction for brokerage on amateur-built sites. Always visually inspect logos/images. When in doubt, ask the owner.

### Google CAPTCHA Persistence (Session 1-3)

Once Google CAPTCHA triggers from rapid browser_navigate calls, the IP stays blocked for the remainder of the session. Even single-step requests hours later may fail.

**Lesson:** DuckDuckGo is PRIMARY for multi-step search workflows. Reserve Google only for Maps/GBP and KG API testing. Minimum 30s between any two browser_navigate calls.

### Table Header Contamination (Session 4)

EAV triples and topical map markdown files contain structural elements that get misparsed as entities:
- Column headers ("Entity", "Attribute", "Value", "Schema") appear as light-scoring nodes
- Row indices ("1", "2", "8") appear in salience rankings
- Section dividers ("Business Entity", "Service Entities") appear as isolated nodes

**Lesson:** Use structural/regex parsing (filter markdown headers, dividers, schema type names) — never manual keyword blacklists. Structural filters are domain-agnostic; manual blacklists break pluggability.

## 29 Issues Encountered

See EXECUTION-ISSUES-LOG.md in the repository for full details. Key issues:

- **ISSUE-001:** Browserbase timeout (switched to Camofox)
- **ISSUE-019:** Forever Realty in all external profiles (brokerage outdated)
- **ISSUE-022:** Camofox tab expiration — re-navigate to fix
- **ISSUE-027:** HAR.com duplicate agent profile IDs
- **ISSUE-028:** LinkedIn duplicate profiles with wrong brokerages (Elevatus, Truss)
- **ISSUE-029:** Cascade brokerage misidentification (3 wrong before finding Walzel Properties)

## 9 Proven Patterns

### Pattern 6: DuckDuckGo as Primary Search Engine
Google CAPTCHA persists across sessions. DDG is faster, cleaner, and more reliable for entity discovery.

### Pattern 7: Contamination Before Creation
Entity contamination (wrong brokerage on external profiles) IS worse than missing profiles. Fix wrong profiles BEFORE creating new ones (GBP, Wikidata, Zillow).

### Pattern 8: Workflow Documents Beat Static Reports
Entity discovery output = workflow checklist with exact steps, URLs, and yes/no decision points. Never deliver a static audit report that requires the user to translate into actions.

### Pattern 9: Framer Site Image-First Rule
Image layer is more current than text layer on Framer sites. Footer text is untrustworthy. External profiles are untrustworthy. Ask the owner.

## Key Architecture Decisions

1. **Corpus-driven vocabulary is mandatory** — WordNet is banned for domain vocabulary
2. **Seed queries are auto-generated** — never hand-coded (ensures industry portability)
3. **Review Gate on every phase** — prevents auto-advancing without human sign-off
4. **Agent decides engine/human split** — user never defines task allocation
5. **Structural filters only** — manual blacklists break pluggability
