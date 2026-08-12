# Momentum & Shock Publishing Strategy — Quann.Homes

**Date:** 2026-05-05
**Purpose:** Define the publishing velocity plan that shocks the search engine into a Broad Index Refresh — triggering re-ranking events and crawl quota increases.

---

## Core Principle

Drip-publishing one page per week signals: "This is a blog adding content slowly." Drop-publishing 12+ pages simultaneously signals: "This is a comprehensive resource that just materialized." The latter triggers a fundamentally different algorithmic response.

### Why Shock Publishing Works

1. **Crawl quota increase:** A sudden burst of new, interlinked URLs signals increased information supply. Google reallocates crawl budget to process the new content — often doubling or tripling daily crawl volume.
2. **Broad index refresh:** When Google discovers many semantically related pages at once, it re-crawls existing pages to update the internal link graph. This triggers re-ranking across the entire cluster.
3. **Information responsiveness:** A site that adds 12 interconnected pages on "Texas home buying" in one day looks fundamentally more authoritative than one that added them over 3 months.
4. **Entity graph expansion:** Google's entity-based ranking re-evaluates existing pages when the surrounding entity graph suddenly becomes richer. Old pages gain new relevance from fresh context.

---

## The Drop Batch Plan

### Batch 1: Entity Foundation + Outdoor Authority (Drop Day 1 — 6 pages)

**Quantity:** 6 pages
**Purpose:** Establish the entity + statewide authority before content goes live.

| Page | Section | Centroid Status |
|---|---|---|
| About Quan Nguyen (entity anchor page) | Core | ENTITY_ANCHOR |
| First-Time Home Buyer Process (Hub) | Core | PRIMARY_CENTROID |
| Katy Neighborhood Guide (Comparison Hub) | Core | PRIMARY_CENTROID |
| Texas Property Tax Structure | Outdoor | Authority Anchor |
| Texas Flood Zones & Insurance | Outdoor | Authority Anchor |
| Texas Residential Market Fundamentals | Outdoor | Authority Anchor |

**Architecture:** Outdoor Section is statewide (not Katy-only) because Quan serves Houston, Austin, Dallas, and Rio Grande Valley. The search engine must see the full Central Entity (Texas Residential Property) at launch. FTHB and Katy Hubs are hub pages linking down to satellites — not monolithic guides.

### Batch 2: Core Buyer Content (Drop Day 2-3)

**Quantity:** 4-5 pages
**Purpose:** The content that answers the most common buyer questions.

| Page | Query Intent |
|---|---|
| First-Time Home Buyer Process (Texas-specific) | Know |
| Builder Incentives — How to Get Paid to Buy | Know + Do |
| Down Payment Assistance Programs in Texas | Know + Do |
| FHA vs Conventional Loans (Texas loan limits) | Know + Do |
| Closing Costs in Texas — A Line-by-Line Breakdown | Know |

### Batch 3: Area Authority (Drop Day 4-5)

**Quantity:** 3-4 pages
**Purpose:** Show local knowledge and trigger Local Pack presence.

| Page | SERP Feature Target |
|---|---|
| Katy Neighborhood Guide (comparison table) | Local Pack |
| Katy ISD School Guide (ratings + feeder patterns) | Knowledge Panel |
| New Construction Communities in Katy | Local Pack |
| Katy Commute Guide | Featured Snippet |

### Summary

| Batch | Pages | Drop Window | Cumulative |
|---|---|---|---|
| Entity Foundation + Outdoor Authority | 6 | Day 1 | 6 |
| Core Buyer Content | 5 | Day 2-3 | 8 |
| Area Authority | 4 | Day 4-5 | 12 |

**Total: 12 pages across 5 days.**

---

## Why Not All at Once?

Dropping all 12 on the same day is ideal for the shock signal — but carries risk:

1. **Quality control:** If any page has errors, all 12 are live with issues.
2. **Internal linking:** Links between pages must be established before publish — cross-linking 12 pages simultaneously is error prone.
3. **Google's processing lag:** A 12-page surge might overwhelm crawl scheduling, causing some pages to sit unindexed for days.

**Recommended approach:** 3 batches across 5 days. This is still a shock signal (most agents add 0-2 pages per month), but gives breathing room for QC and internal linking.

---

## Crawl Quota Acceleration Tactics

| Tactic | Implementation |
|---|---|
| Sitemap update | Regenerate and resubmit sitemap.xml after each batch |
| Internal links from existing pages | Update homepage + existing blog posts to link to new pages |
| Google Search Console | Manually request indexing for each new URL after publish |
| Social signals | Post each new page to Quan's social profiles (LinkedIn, FB) to trigger discovery crawls |
| No orphan pages | Every new page must be reachable from nav or an existing page within 2 clicks |

---

## Momentum Maintenance (Post-Drop)

After the initial 5-day shock, switch to:

| Frequency | Activity |
|---|---|
| Weekly | 1 new blog post or area guide |
| Monthly | Update 1-2 existing pages with fresh data (prices, rates, school ratings) |
| Quarterly | HAR market data refresh — update statistics across all pages |

**The "update signal" is as important as the "publish signal."** A page that shows `dateModified: 2026-07-01` with updated 2026 Q2 data signals ongoing information responsiveness — the opposite of "stale incumbent" content.

---

## Competitor Context

Most Katy/Houston agents publish **0-2 pages per year** on their websites. Their content is:
- Stale (published once, never updated)
- Thin (300-500 word marketing fluff)
- Non-structured (no tables, no definitions, no comparison data)

**Dropping 12 data-rich, structured pages in 5 days makes quann.homes the most informationally responsive site in its competitive set.** When Google's freshness algorithms re-evaluate rankings for "Katy home buyer," a site that just added 12 comprehensive pages will outrank one that published a generic "Welcome to my website!" page in 2024.

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Pages unindexed after publish | Manual GSC index request + social signals |
| Low crawl budget (new domain) | Sitemap resubmission + existing page linking |
| Thin content penalties | Minimum 1,200+ words per page, rich HTML structure, unique data |
| Internal link errors | Pre-publish crawl to verify every link resolves |
| 404 on new pages | Verify all URLs in sitemap before submission |
