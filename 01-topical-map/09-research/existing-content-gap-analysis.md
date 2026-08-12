# Content Audit — What Exists on Quann.Homes vs What's Needed

**Date:** 2026-05-04
**Status:** Site audited via scrape. Gaps identified.

---

## Existing Content Inventory (9 pages, all live 200)

### Content Pages

| # | Page | Type | Quality Assessment |
|---|---|---|---|
| 1 | / (Homepage) | Landing | Strong brand copy, testimonials, CTA. Missing: JSON-LD schema, clear buyer journey path |
| 2 | /blog/steps-for-buying-your-first-home | Guide | Needs content review — likely covers steps but may miss programs/incentives |
| 3 | /blog/out-of-state-buyer-guide | Comprehensive guide | **Very thorough** — 11-part outline, appears to be the strongest asset |
| 4 | /blog/texas-first-time-home-buyer-guide5 | Guide | Possibly redundant with #2 — audit overlap |
| 5 | /disclosure | TREC required | Compliant, good |
| 6 | /privacy-policy | Legal | Compliant, good |
| 7 | /texas-real-estate-commission-information-about-brokerage-services | IABS | Compliant, good |
| 8 | /contact-us | Contact | Standard contact form |
| 9 | /contact-us-2 | Contact | Why two contact pages? Merge or differentiate |

---

## Site Structure Issues Found

### Navigation (from homepage scrape)
```
- / (Home)
- ./contact-us-2 (Contact)
```

**Only 2 nav items.** No blog link in main nav, no area guides, no about page as separate entity.

### Tech Stack
- Built on **Framer** (framer.com/edit/init.mjs)
- Not WordPress — harder to add blog sections dynamically
- No visible sitemap.xml (Framer may not auto-generate)

### Missing Pages (from topical map)

| Pillar | Missing Pages |
|---|---|
| Buying in Texas | 7/9 spokes missing (only FTHB steps exists) |
| Out-of-State Relocation | ⚠️ One comprehensive guide exists — but it's ONE page trying to cover everything |
| Katy & Houston Areas | **ALL missing** — neighborhood guides, school guides, commute analysis |
| Selling | **ALL missing** — nothing for sellers |
| Investing | **ALL missing** |
| Trust/Credibility | /about page missing (entity lives on homepage but no dedicated page) |

---

## Critical Gaps (What to Build First)

### Gap 1: No Entity Anchor Page
**Problem:** Quan's authority is spread across the homepage only. There's no dedicated `/about` page with full credentials, NAP, structured data, team info, and a clear "here's why you should trust me" narrative.
**Solution:** `/about` — full RealEstateAgent JSON-LD, years/certs/languages, team, client outcomes

### Gap 2: No Local Area Content
**Problem:** Google needs geographic entity recognition. Without neighborhood guides, school data, commute analysis, and market stats pages, there's no local relevance signal.
**Solution:** `/katy-neighborhood-guide`, `/katy-schools`, `/katy-vs-houston-suburbs`, `/katy-housing-market-trends`

### Gap 3: One-Page Giant for Out-of-State
**Problem:** The out-of-state guide is a massive single page trying to cover 11 topics. This violates the hub-and-spoke architecture — Google can't index subsections as separate entities.
**Solution:** Break into a hub page + 8-10 spoke pages (California→Texas cost comparison, Texas property taxes for relocators, buying sight unseen, etc.)

### Gap 4: Missing Buyer Journey Pages
**Problem:** No pages for specific decisions buyers face: rent vs buy, how much home can I afford, choosing a lender, understanding the TREC contract.
**Solution:** Fill Pillar 1 spokes — 7 pages needed

### Gap 5: Zero Seller Content
**Problem:** If Quan also does listings, there's zero content attracting sellers.
**Solution:** 6 seller-focused spoke pages

### Gap 6: No Structured Data
**Problem:** No JSON-LD on any page. Google can't extract entity relationships, NAP, sameAs, or service areas.
**Solution:** Add schema to: homepage (RealEstateAgent), about page, all area guides (Place/LocalBusiness context), all blog posts (Article+author)

---

## Content Priority Matrix (ROI-weighted)

| Priority | Page | Why | Effort |
|---|---|---|---|
| 🔴 1 | /about | Entity anchor, schema, trust signal | Low (1 page) |
| 🔴 2 | JSON-LD on ALL pages | Immediate SEO signal boost | Low (template) |
| 🔴 3 | /katy-neighborhood-guide | Highest buyer intent, local relevance | Medium |
| 🔴 4 | Break out-of-state guide into hub+spokes | Multiplies pages, captures subtopics | Medium |
| 🟡 5 | /texas-first-time-home-buyer-programs | Captures "how do I afford this?" intent | Medium |
| 🟡 6 | /katy-housing-market-trends | Data-driven, linkbaity | Medium |
| 🟡 7 | /rent-vs-buy-texas | Decision framework, evergreen | Low |
| 🟡 8 | FTHB spoke pages (6 remaining) | Fills pillar 1 | Medium each |
| 🟢 9 | Seller pages (6) | Opens second revenue stream | Medium each |
| 🟢 10 | Investor pages (5) | Niche, lower volume | Medium each |

---

## What EXISTS in RAG (Quann Chat)

The RAG has been indexing quann.homes content. The scrape ran successfully (205 chunks) before the embedding step crashed on a few pages. **Most content IS indexed** — the daily refresh just needs a fix for the precompute step.

### RAG Fix Required

The error: `No precomputed embedding for text: Ellie Sattler`

Root cause: `precompute_embeddings.py` runs before `index_quann_precomp.py`, but some extracted entities (like testimonial people) don't get embeddings. The fix is either:
1. Generate embeddings for ALL extracted text in the precompute step, OR
2. Filter out chunk entities that aren't precomputed before indexing

Location of fix: `/home/steve/lightrag-apps/quann-chat/index_quann_precomp.py`

---

## Summary: What We Know WITHOUT Proxy Data

| Category | Known | Unknown |
|---|---|---|
| Site structure | ✅ 9 pages on Framer, FTHB+relocation guides exist | ❌ Full content depth of blog posts (not crawled) |
| Entity attributes | ✅ License, brokerage, phone, email, areas served | ❌ Years, certs, languages, awards |
| Market data | ✅ Texas no income tax, homestead exemption exists | ❌ Actual prices, DOM, inventory, trends |
| Competitors | ✅ Framework built | ❌ Who they are, what they cover |
| External profiles | ✅ Framework built | ❌ Which exist, NAP consistency |
| SEO foundation | ✅ Source context, central entity, query templates | ❌ JSON-LD implementation, backlinks (none acquired) |
