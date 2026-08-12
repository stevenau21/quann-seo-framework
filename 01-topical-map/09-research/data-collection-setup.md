# Data Collection Setup — What We Actually Need

**Date:** 2026-05-04 (Revised 2026-05-05)
**Status:** Realistic plan based on Quan's actual setup
**Key insight:** Quan already has content + RAG infrastructure. This is about filling gaps, not starting from zero.

---

## What We Already Have (No scraping needed)

Quan's existing infrastructure already handles discovery:

- **Quann Chat RAG** (port 8001) indexes quann.homes content (205 chunks from 9 pages). Queries to `/chat` return entity data, client types, services.
- **SEO RAG** (port 8002) has the full methodology loaded. Queries to `/ask` return frameworks.
- **quann.homes itself** — 9 live pages including comprehensive out-of-state guide and FTHB content.

Most "research" questions are answerable by querying these RAGs, not by scraping external sites. The only data we genuinely need from outside is real-time market stats.

---

## What Actually Requires Proxies

### Category 1: HAR.com Market Stats (one-time pull)

Quan is a HAR member. The cleanest way:

```
Option A (preferred): Ask Quan to pull a HAR market report PDF
  - HAR agent dashboard → Market Reports → Katy area
  - One export, no scraping needed
  - Contains: median price, DOM, inventory, sold count, new listings

Option B (fallback): Redfin Data Center (public, no login)
  - https://www.redfin.com/us-housing-market
  - Filter to Katy, TX
  - Public data, rate limited but accessible
  - Use basic proxy rotation (not residential needed for THIS)

Option C (if proxy available): HAR.com public market pages
  - Only if Options A/B insufficient
  - Needs residential proxy
```

**What we actually need (10 data points, not 17):**

| Data Point | Easiest Source | Proxy Needed? |
|---|---|---|
| Katy median home price | Redfin Data Center | No (public) |
| Katy price/sqft | Redfin | No |
| Katy DOM | Redfin / Ask Quan for HAR report | Maybe |
| Houston metro price | Redfin | No |
| Texas avg closing costs | Bankrate article (public) | No |
| County property tax rates | Texas Comptroller (public PDFs) | No |
| FHA loan limits | HUD website (public) | No |
| Avg TX mortgage rate | Freddie Mac PMMS (public) | No |
| School ratings | TEA website (public) | No |
| Commute times | Google Maps (manual lookup) | No |

**Net: ~80% of market data is public. The remaining ~20% (HAR member-only stats) can come from Quan directly.**

### Category 2: Competitor Discovery (manual, not automated)

```
Don't crawl competitor sites. Instead:
1. Manual Google search for "Katy TX buyer agent" / "Katy realtor"
2. Visit top 5 sites manually
3. Note: do they have a blog? Area guides? What topics?
4. Record in a simple spreadsheet

This is a 2-hour manual task, not an automated crawl.
Automated crawling of competitor sites is overkill — we just need
to know what they cover, not scrape their entire site.
```

### Category 3: Web Entity Audit (manual)

```
Same approach — manual, not automated:
1. Google "Quan Nguyen real estate Katy TX" → check GBP
2. Search Zillow, Realtor.com, HAR.com for Quan's name
3. Note what exists, screenshot if needed
4. Check NAP consistency by eye

This is a 1-hour manual task. No proxy infrastructure needed.
```

---

## What to Do Instead (Revised Flow)

### Step 1: Pull public data (no proxies, do now)
```bash
# Redfin Katy market data
curl "https://www.redfin.com/city/30818/TX/Katy/housing-market"

# Texas Comptroller tax rates
curl "https://comptroller.texas.gov/taxes/property-tax/rates/"

# HUD FHA limits
curl "https://entp.hud.gov/idapp/html/hicostlook.cfm"

# Freddie Mac rates
curl "https://www.freddiemac.com/pmms"
```

### Step 2: Ask Quan for HAR report (5 minutes)
- "Can you export a Katy area market report from your HAR dashboard?"
- Gets us: actual MLS data (more authoritative than Redfin)

### Step 3: Manual competitor review (2 hours)
- Search → visit 5 sites → note content coverage → fill matrix

### Step 4: Manual profile audit (1 hour)
- Check GBP, Zillow, Realtor.com, HAR.com, LinkedIn

### Step 5: Feed everything into RAG
- Take compiled market data, competitor notes, profile findings
- Add to Quann Chat RAG as new documents
- Now RAG can answer with real numbers

---

## Revised Timeline

| Task | Time | Blocked On |
|---|---|---|
| Pull public market data | 30 min | Nothing |
| Ask Quan for HAR report | 5 min | Quan responding |
| Manual competitor review | 2 hours | Nothing |
| Manual profile audit | 1 hour | Nothing |
| Compile into RAG | 30 min | Above complete |
| Update EAV triples with real data | 1 hour | Above complete |
| Generate content briefs | 2 hours | EAV complete |
| Write priority pages | 4 hours | Briefs complete |

**Total: ~11 hours of work. Zero proxy infrastructure needed for 90% of it.**

The only scenario that justifies proxy setup: if Quan wants automated ongoing market monitoring (weekly price updates) rather than one-time snapshots.

---

## Output: Where Data Lands

All collected data → `/home/steve/SEO-quann.homes/09-research/`

| File | Contents | Source |
|---|---|---|
| `market-data-public.md` | Compiled from Redfin, HUD, Freddie Mac, Texas Comptroller | Public |
| `market-data-har.md` | HAR report data (from Quan) | Quan |
| `competitor-notes.md` | Manual review of 5 competitor sites | Manual |
| `profile-audit.md` | Manual audit of Quan's external profiles | Manual |

---

## Bottom Line

**We don't need proxies for 90% of this project.** The original framework was overengineered. Most data is public or comes from Quan directly. The only proxy scenario is if we automate ongoing market monitoring — and even then, Redfin's public data center is sufficient for trending.
