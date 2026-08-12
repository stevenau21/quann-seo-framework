---
name: seo-market-data-collection
description: Pull live market data for SEO content (real estate focus). Data points, primary sources, and the battle-tested Camofox + search-engine-first scraping strategy. Covers pitfalls, Redfin city IDs for Katy/Houston, and refresh schedule.
version: 2.0.0
metadata:
  hermes:
    tags: [SEO, Market Data, Real Estate, Scraping, Data Collection, Camofox]
---

# SEO Market Data Collection

Pull 10 standard data points for real estate SEO content. This skill is a prerequisite step in the holistic SEO topical map pipeline (Category B in MASTER-GAP-LIST.md).

## Data Points & Proven Sources

| # | Data Point | Primary Source | Approach |
|---|---|---|---|
| 1 | Local median home price | Redfin (via Google search) | Search `Redfin Katy TX housing market`, extract from SERP snippet |
| 2 | Local price/sqft | Redfin (same search) | Same page — usually in headline or stats bar |
| 3 | Metro median price | Redfin Houston | Search `Redfin Houston TX housing market` |
| 4 | Avg closing costs % | Bankrate / Rocket Mortgage | Search `closing costs Texas 2026 Bankrate` |
| 5 | County property tax rate | Multiple aggregators | Search `Harris County property tax rate` + `Fort Bend County property tax rate` |
| 6 | FHA loan limits | HUD aggregator sites | Search `FHA loan limits Harris County 2026` — HUD.gov itself is an Oracle DB that 500-errors |
| 7 | Avg mortgage rate | Freddie Mac PMMS | `freddiemac.com/pmms` or FRED CSV |
| 8 | School district ratings | TEA accountability | Search `Katy ISD rating 2025 TEA` — txschools.gov 404'd (URL changed) |
| 9 | Local commute times | Google Maps / news | Search `Katy Houston commute time 2026` — news articles often have this |
| 10 | Days on Market (DOM) | Redfin (same search as #1) | Visible on Redfin market page stats section |

## Tool Strategy (Battle-Tested)

### PRIMARY: Camofox (self-hosted anti-detection browser)
Camofox is a self-hosted Firefox fork at `http://localhost:9377` with built-in fingerprint spoofing and humanization. It handles JS rendering and anti-bot detection out of the box — no extra cookies, headers, or setup needed. Use `browser_navigate` tool against Camofox URLs.

**Setup:** `skill_view("camofox-setup")` for deployment details.
**Key params:** `humanize: true` mimics human scroll/click behavior. No additional anti-detection config required.

### PATTERN 1: Search-Engine-First (MANDATORY)
**NEVER guess URLs.** Government and commercial sites restructure URLs constantly. Instead:

1. Search for the data point in Camofox: `browser_navigate` to `https://www.google.com/search?q={descriptive query}` or `https://duckduckgo.com/?q={query}`
2. Read SERP snippets — often contain the data directly (median price, FHA limit, tax rate)
3. Only click through if snippet is insufficient
4. Cross-reference 2+ sources to confirm

**Why:** In this session, directly navigating to Redfin city IDs (30818, 30970), HUD.gov, TEA/txschools.gov, and Bankrate ALL returned 404s or wrong redirects. Searching found correct URLs within 1-2 attempts.

### PATTERN 2: DuckDuckGo as Google Fallback
Google CAPTCHA-blocks after ~5 rapid searches from the same server IP (even with Camofox fingerprint spoofing). When blocked:
- Switch to DuckDuckGo: `https://duckduckgo.com/?q={query}`
- DDG has no CAPTCHA, returns clean SERP snippets, and typically shows the same top results as Google for factual queries
- For entity discovery specifically, DDG's site: search syntax works identically to Google's

### PATTERN 3: SERP Snippet Extraction
For factual data points (numbers, rates, prices), Google/DDG snippets often contain the answer directly. Read from the snapshot before clicking. This saves one full page load per data point and avoids anti-bot challenges on target sites.

### PATTERN 4: Government Tools Are Unreliable
HUD, TEA, Texas Comptroller — all use JS-rendered SPAs with frequently changing URL patterns. Their own search tools often Oracle/500 error. **Use aggregator sites** (Rocket Mortgage for FHA, bankrate.com for closing costs, news articles for commute times) that republish the same government data in stable HTML.

### PATTERN 5: Read Before You Click
When search results appear, read ALL snippets on the first page before clicking any link. Often 2-3 results will show the same number in their snippet — that's your confirmation. Cross-reference is built into the search results page.

### FALLBACK: Curl for Static JSON/CSV
Freddie Mac FRED data can be pulled via CSV: `curl "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US&cosd=2026-01-01&coed=2026-05-24"`. No browser needed for FRED.

### DO NOT USE (proven failures)
- **Firecrawl API** — requires paid key, not in our stack
- **Browserbase** — cloud browser times out, not needed when Camofox works
- **Raw curl on .gov sites** — returns empty HTML (JS-rendered SPAs)
- **Wikipedia for current metrics** — 2-4 years stale; acceptable only for structural facts (district boundaries, city names)

## Verified Redfin City IDs

| Area | Redfin URL | Median (May 2026) | $/sqft |
|---|---|---|---|
| Katy, TX | `redfin.com/city/9764/TX/Katy/housing-market` | $340,000 | $158 |
| Houston, TX | `redfin.com/city/8903/TX/Houston/housing-market` | $345,000 | $179 |

*IDs 30818 and 30970 both redirect to wrong pages. Only 9764 is correct for Katy.*

## Fallback Strategy

**If live scraping fails for >50% of data points after 3 attempts:**

1. **Use what you have** — ship with confirmed numbers and mark estimates clearly
2. **Acceptable estimates for architecture:** 2.1% property tax, 2-5% closing costs, 35-45 min commute
3. **Do NOT block the pipeline on data precision** — the architectural value (Information Gain, entity grounding, contextual bridges) works with approximate numbers
4. **Refresh during quarterly cycle** when tools are available

## Refresh Schedule

| Data Point | Cadence | Note |
|---|---|---|
| Mortgage rate | Every 2 months | Freddie Mac updates weekly |
| Home prices / DOM / $/sqft | Quarterly | Redfin monthly data |
| Tax rates | Annually | October (post-appraisal) |
| FHA limits | Annually | January (HUD December update) |
| School ratings | Annually | August (TEA release) |
| Closing costs | Semi-annually | Market-fluctuating |
| Commute times | Annually | Unless major highway changes |

## Session Logging

After every market data collection session, update `SEO-quann.homes/EXECUTION-ISSUES-LOG.md` with:
- Which tools were attempted and their results
- Which data points succeeded vs failed
- Root causes for failures
- Recovery plan for next session
- New patterns discovered

This prevents repeating the same failed approaches and builds institutional knowledge.

## Usage

Load this skill at start of Category B execution. After collection, save results to `SEO-quann.homes/market-data.md` with provenance (source, date, confidence level for each data point).
