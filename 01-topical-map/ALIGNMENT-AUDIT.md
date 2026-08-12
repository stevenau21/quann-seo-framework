# Alignment Audit — What Quan Actually Covers vs What We Assumed

**Date:** 2026-05-05
**Purpose:** Go through every deliverable and separate what's grounded in Quan's actual content/business from what we added speculatively. No "should cover" — only "does cover."

---

## Ground Truth Sources

| Source | What It Confirms |
|---|---|
| Source Context (approved by Quan) | "helps Texas home buyers bridge the knowledge gap" — buyer-first, trust funnel, commission model |
| quann.homes homepage | "Buy a Home" CTA, "get paid to buy," builder incentives, testimonials from buyers + seller/investor |
| quann.homes /blog/steps-for-buying-your-first-home | FTHB content exists (depth unknown) |
| quann.homes /blog/out-of-state-buyer-guide | Massive 11-part guide on relocation economics, logistics, schools, costs |
| quann.homes /blog/texas-first-time-home-buyer-guide5 | Second FTHB post (depth unknown, possible redundancy) |
| Quann Chat RAG | "Client types: home buyers, home sellers, investors" — listing and investing are MENTIONED but no content exists for them |
| Footer of quann.homes | "MINH QUAN NGUYEN, REALTOR | LICENSE #0774451 | REAL BROKERAGE" |
| Navigation of quann.homes | Only 2 items: Home + Contact. Blog not in nav. |

---

## File-by-File Alignment Audit

### 01-source-context/source-context.md
**Status:** ✅ APPROVED
**Alignment:** 100%. Quan personally approved this statement.

### 02-central-entity/central-entity.md
**Status:** ✅ Grounded
**What's confirmed:** License #0774451 (from footer), REAL BROKERAGE (from footer), phone (832) 400-3152 (from RAG), email quan@thequantumteam.net (from footer/RAG), Katy TX (from RAG), service areas (from RAG), The Quantum Team (from homepage)
**What's speculative:** "Years of experience" — blank. "Languages spoken" — blank. "Certifications" — blank. "Awards" — blank. These are flagged as missing, which is correct.
**Verdict:** Good — properly flagged unknowns.

### 03-web-entity/web-entity.md
**Status:** ⚠️ Partially grounded
**What's confirmed:** quann.homes exists (checked), Instagram exists (from memory/context), Telegram @QuannBot (from memory)
**What's speculative:** Google Business Profile — NOT confirmed. Zillow profile — NOT confirmed. Realtor.com — NOT confirmed. HAR.com profile — NOT confirmed. LinkedIn — NOT confirmed. All 13 platform items are unchecked.
**Verdict:** Framework is useful, but it's presented as if these profiles definitely exist and just need auditing. Truth: we don't know if ANY of them exist. Rewrite needed.

### 04-eav-triples/eav-triples.md
**Status:** ✅ Grounded (methodology + Quan data)
**What's confirmed:** 14 universal attribute categories (from methodology), known triples about Quan (license, brokerage, phone, email, areas from RAG/footer)
**What's speculative:** Entity types defined for "Seller" and "Investor" — no content exists for either. "Property Tax," "MUD," "TREC" entities — methodology says these are relevant but we haven't confirmed Quan covers them.
**Verdict:** Mostly fine. The EAV framework is methodological. The triples we HAVE are grounded. The empty ones are properly flagged. Minor concern: seller/investor entities may be noise if Quan doesn't actually pursue those.

### 05-query-templates/query-templates.md
**Status:** ✅ Grounded (methodology application)
**What's confirmed:** 8 template patterns (from SEO RAG methodology). Instantiated examples use Quan's entities (Katy, Houston, FTHB, out-of-state).
**What's speculative:** The specific queries (e.g., "homes for sale Katy under 400k") — methodology says to generate these, but we haven't validated which ones Quan wants to target.
**Verdict:** Fine. Query templates are a tool, not content. They're derived from methodology × Quan's entities.

### 06-topical-map/topical-map.md
**Status:** 🔴 Mixed — over-built
**What's confirmed by Quan's content:**
- Pillar 1 "Buying in Texas" → Quan has FTHB + out-of-state content ✅
- Pillar 2 "Out-of-State Relocation" → Quan has a massive guide ✅
- Pillar 3 "Katy & Houston Area Guides" → Quan's Source Context says "accessible area guides" but NONE exist yet ⚠️

**What's speculative:**
- Pillar 4 "Selling Your Texas Home" → No seller content exists. Quan mentions "seller listing" as a service but has done NOTHING to attract sellers. This pillar may be irrelevant noise.
- Pillar 5 "Real Estate Investing" → Same — mentioned as service, zero content.
- Pillar 6 "Trust & Credibility" → About page doesn't exist as separate entity. "Why Work With The Quantum Team" is assumed.

**Individual spokes not grounded:**
- "How to Get Pre-Approved for a Mortgage in Texas" — does Quan cover this? Unknown.
- "FHA vs Conventional Loans" — does Quan cover this? Unknown.
- 7 more FTHB spokes — all assumed from methodology, not from Quan's existing content
- 8 relocation spokes — the out-of-state guide is one massive page covering these, but not as separate pages
- 8 Katy spokes — all assumed. None exist.
- 6 seller spokes — all assumed. Seller content not confirmed.
- 5 investment spokes — all assumed. Investment content not confirmed.
- 5 trust spokes — About page doesn't exist, client stories exist as snippets on homepage only.

**Verdict:** Over-specified. 2.5 pillars (buying, out-of-state, partial area guides) are grounded. The other 3.5 pillars (selling, investing, trust, full area guides) and ~40 spokes are speculative. This needs significant revision.

### 06-topical-map/topical-borders.md
**Status:** ⚠️ Mixed
**What's grounded:** Distance concept (from methodology). The border distinction between residential/homebuying (inside) vs commercial/finance/DIY (outside) is methodological, not Quan-specific.
**What's speculative:** "Home staging" listed as inside border — but Quan has no seller content. "Texas real estate investing" listed as inside — but zero investment content exists. The entire seller/investor inclusion assumes Quan wants these leads.
**Verdict:** Border methodology is sound. What's listed INSIDE the border needs revision to match what Quan actually does.

### 06-topical-map/information-gap.md
**Status:** ✅ Grounded (methodology-driven)
**What's confirmed:** These are zero-search-volume concepts that the methodology says an authority must cover. TREC notice, agency disclosure, MUD tax — these are real Texas-specific things buyers don't search for.
**What's speculative:** Whether Quan WANTS to build pages for all 15 concepts. Some (option period, agency disclosure) are core. Others (rate lock expiration, HOA estoppel letters) are edge cases.
**Verdict:** These are methodological recommendations, not requirements. Good as a resource, but Quan should prioritize, not execute all.

### 06-topical-map/contextual-bridges.md
**Status:** ⚠️ Mixed
**What's grounded:** Bridge concept (from methodology). Bridges for FTHB programs, Katy neighborhoods, out-of-state guide → all reference topics Quan has or clearly wants.
**What's speculative:** Bridge for "Home Staging Tips" → Quan has no staging content. Bridge for "Texas Property Tax Guide" → no such page exists. Bridge for "MUD Tax" → no such page exists.
**Verdict:** Good concept. Specific bridges reference assumed pages.

### 07-content-briefs/content-briefs.md
**Status:** ✅ Grounded
**What's confirmed:** Template structure (from methodology). Example brief for "First-Time Home Buyer Programs in Texas" — this maps to Quan's existing FTHB content.
**What's speculative:** None in the template. The one example is on-topic.
**Verdict:** Good. Template is solid. The ONE worked example matches Quan's content.

### 07-content-briefs/lexical-richness.md
**Status:** ✅ Grounded (real estate domain knowledge)
**What's confirmed:** These are real estate terms. They're domain-specific, not Quan-specific. Any Texas real estate site benefits from using them.
**What's speculative:** Whether Quan's existing content already uses these terms. We didn't audit his pages.
**Verdict:** Fine as a reference catalog. Domain terms, not Quan assumptions.

### 07-content-briefs/cost-of-retrieval.md
**Status:** ✅ Grounded (methodology/tactical)
**What's confirmed:** Page segmentation strategy, semantic HTML rules — these are SEO best practices, not Quan-specific.
**What's speculative:** None. Pure technical methodology.
**Verdict:** Good — no entity assumptions.

### 08-backlink-strategy/backlink-strategy.md
**Status:** ⚠️ Partially grounded
**What's confirmed:** HAR.com is relevant (Quan is HAR member if he's in Houston). Chamber of Commerce is standard local SEO.
**What's speculative:** Does Quan have a GBP? A Zillow profile? Is he in the Katy Chamber? Has he ever been mentioned in local news? None of these are confirmed.
**Verdict:** Strategy framework is standard. None of the specific sources are verified.

### 09-research/consensus-baseline.md
**Status:** ✅ Grounded (factual research)
**What's confirmed:** TREC, Texas Comptroller, HUD, Fannie Mae — these are verifiable, authoritative sources for real estate data.
**Verdict:** Good — no entity assumptions.

---

## Summary: What We Got Wrong

| Pattern | Example | Problem |
|---|---|---|
| **Assumed content that doesn't exist** | "Home Staging Tips" bridge, "Katy Neighborhood Guide" table | Referenced pages that are purely hypothetical |
| **Assumed service areas** | Seller pillar (6 spokes), investor pillar (5 spokes) | Quan MENTIONS these services but has zero content for them |
| **Assumed external profiles** | "Check GBP, Zillow, Realtor.com" | We don't know if any exist — shouldn't build workflows around guesses |
| **Over-specified spokes** | 50+ spoke pages from 6 pillars | Only ~8-10 of these are grounded in Quan's actual content direction |
| **Over-engineered collection** | Proxy crawl scripts for competitor sites, auto NAP extraction | Quan's setup doesn't need this — RAG already handles knowledge |

---

## What's Actually Solid

| File | Status | Why |
|---|---|---|
| source-context.md | ✅ Approved | Quan signed off |
| central-entity.md | ✅ Known facts | License/brokerage/contact confirmed |
| eav-triples.md (known) | ✅ RAG-extracted | Values from quann.homes footer + RAG |
| query-templates.md | ✅ Methodology | Derived, not guessed |
| content-briefs.md | ✅ Template + 1 example | The example matches Quan's content |
| lexical-richness.md | ✅ Domain knowledge | Real estate terms, not Quan-specific |
| cost-of-retrieval.md | ✅ Technical | HTML/Schema best practices |
| consensus-baseline.md | ✅ Factual | Authoritative sources |

---

## What Needs Revision

| File | Issue | Fix |
|---|---|---|
| topical-map.md | 3.5 pillars assumed, not grounded | Reduce to what Quan actually covers or has clearly signaled he wants |
| topical-borders.md | Seller/investor listed as "inside" | Move to gray zone until Quan confirms |
| contextual-bridges.md | Bridges for non-existent pages | Remove bridges referencing assumed content |
| web-entity.md | 13-platform audit assumes profiles exist | Rewrite as "discover what exists" not "audit what should exist" |
| backlink-strategy.md | Sources not verified | Flag all as "to confirm" |
| data-collection-setup.md | Over-engineered proxy setup | ✓ Already fixed — realistic now |
| competitor-analysis-framework.md | Automated crawl framework | ✓ Already fixed — manual now |
| web-entity-audit-framework.md | 13-platform automated audit | ✓ Already fixed — manual now |
