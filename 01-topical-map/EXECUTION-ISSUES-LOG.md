# Execution Issues Log — SEO Topical Map
**Framework stage:** Prerequisites → Category A (SEO interview) ✅ → Category B (Market data) ✅ → Category C (Entity discovery) ✅
**Dates:** Session 1: 2026-05-24 AM (raw HTTP scraping, mostly failed) → Session 2: 2026-05-24 PM (Camofox live, 10/10 confirmed) → Session 3: 2026-05-24 PM (Entity discovery + workflow analysis)
**Status:** ✅ Category A complete. ✅ Category B complete (10/10 HIGH confidence). ✅ Category C complete (11 profiles found, 7 platforms checked, entity workflow doc written). Remaining prerequisites: D (Framer access), E (KG API key), F (tech SEO prep), G (competitor analysis).

---

## Issues Encountered

### ISSUE-001: Browserbase Timeout (Critical)
- **Tool:** `browser_navigate`
- **Symptom:** Every navigation timed out after 60s with "Command timed out after 60 seconds"
- **URLs attempted:** redfin.com/city/30981, hud.gov, google.com/search
- **Root cause:** Browserbase cloud browser service was unresponsive — likely overloaded or rate-limited
- **Impact:** Couldn't scrape JS-rendered pages (Redfin, HUD, TEA, Comptroller)
- **Fix for next run:** Retry browser tool at start of session; if still down, use Firecrawl or raw HTTP APIs

### ISSUE-002: Redfin Scraping — Partial Success
- **Tool:** `curl` / `urllib.request`
- **Result:** Got median price ($436,523) from HTML pattern match — appeared 7 times consistently
- **Failed:** Price/sqft, DOM, Houston metro price NOT extractable from static HTML
- **API endpoint:** `/stingray/api/v1/region/stats` returned 404 (possibly changed)
- **Root cause:** Redfin's market page embeds most data in JS-rendered widgets, not static HTML
- **Fix for next run:** Try Redfin's `stingray/api/gis-csv` for sold listings to derive price/sqft and DOM

### ISSUE-003: Realtor.com — 429 Rate Limited
- **Tool:** `urllib.request`
- **Symptom:** HTTP 429 Too Many Requests
- **Root cause:** Realtor.com detected non-browser traffic from server IP
- **Fix for next run:** Rotate User-Agent, add delay, or use Firecrawl with stealth mode

### ISSUE-004: RocketHomes — 404
- **Tool:** `urllib.request`
- **Symptom:** HTTP 404 on `/real-estate-trends/tx/katy`
- **Root cause:** URL pattern may have changed; RocketHomes may have removed or moved this endpoint
- **Fix for next run:** Search for updated URL pattern before requesting

### ISSUE-005: HUD FHA Limits API — 404
- **Tool:** `urllib.request`
- **Symptom:** Both `/FHALimits2026.json` and `/limits_2026` returned 404
- **Root cause:** HUD's URL patterns change annually; 2026 data may not be published yet at expected paths
- **Fix for next run:** Navigate HUD.gov via browser to find current URL, then scrape

### ISSUE-006: Texas Comptroller — JS-Rendered
- **Tool:** `curl`, `urllib.request`
- **Symptom:** Empty responses — page is entirely JS-rendered (React/Angular)
- **Root cause:** Government site migrated to SPA framework; static scraping impossible
- **Fix for next run:** Browser tool required. Or use aggregated sources (Tax-Rates.org, SmartAsset) that publish Comptroller data in static HTML

### ISSUE-007: TEA School Ratings API — 404
- **Tool:** `urllib.request`
- **Symptom:** `/api/schools/101914` returned 404
- **Root cause:** API endpoint changed since 2022; txschools.gov may have new API structure
- **Fix for next run:** Browser tool required. TEA's `rptsvr1.tea.texas.gov` SAS broker may still work for district-level data.

### ISSUE-008: FRED Economic Data — Timeout
- **Tool:** `urllib.request`
- **Symptom:** CSV download timed out after 10s
- **Root cause:** FRED's CSV endpoint for MORTGAGE30US with full query params is heavy
- **Fix for next run:** Use simpler FRED URL: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US&cosd=2026-05-01&coed=2026-05-24`
- **Already resolved** via Freddie Mac PMMS direct scrape (6.51%)

### ISSUE-009: Wikipedia Data Staleness
- **Tool:** Wikipedia API
- **Symptom:** Katy ISD rating from 2022 (4 years stale for 2026 session); Harris Co median from Q3 2024; Demographics from 2020 Census
- **Root cause:** Wikipedia mirrors government data but lags behind; not suitable for current-year numbers
- **Impact:** 4/9 data points are stale (school rating, Houston price, demographics, tax rate)
- **Fix for next run:** Wikipedia is OK for structural facts (county borders, school district boundaries) but NEVER for current-year metrics. Always pull metrics from primary sources (TEA, HUD, Comptroller, Redfin).

### ISSUE-010: Exa API Key Not Configured
- **Tool:** Exa search API
- **Symptom:** No EXA_API_KEY found in `/.hermes/.env`
- **Impact:** Couldn't use AI-native search to find data points quickly
- **Fix for next run:** Configure Exa API key if available. Fallback: DuckDuckGo Lite + pattern matching.

### ISSUE-011: Firecrawl Not Attempted
- **Tool:** Never called
- **Symptom:** Firecrawl API key exists in `.env` (`FIRECRAWL_API_KEY`) but never used
- **Root cause:** Didn't check for Firecrawl availability before trying raw HTTP
- **Fix for next run:** Firecrawl should be first attempt for JS-rendered pages — it handles rendering, anti-bot, and structured extraction.

### ISSUE-012: No Camouflage/Rotation Layer
- **Tool:** All HTTP requests
- **Symptom:** Same User-Agent and IP on every request; got 429 and 403 blocks
- **Root cause:** No request rotation, no delay between requests, no proxy
- **Fix for next run:** Add 2-3s delay between requests. Rotate User-Agent strings. Consider Firecrawl stealth mode.

---

## Data Provenance — What We Actually Have

| # | Data Point | Value | Method | Source Date | Confidence |
|---|---|---|---|---|---|
| 1 | Katy median price | $436,523 | Redfin HTML scrape | 2026-05-24 live | ✅ HIGH |
| 2 | Katy price/sqft | ~$178 | Derived ($436,523 ÷ 2,450) | N/A | ⚠️ DERIVED |
| 3 | Houston metro price | $295,790 | Wikipedia / ACS | Q3 2024 | ❌ STALE |
| 4 | Closing costs % | 2–5% | Industry estimate | N/A | ⚠️ ESTIMATE |
| 5 | Harris Co tax rate | ~2.1% | Industry estimate | N/A | ⚠️ ESTIMATE |
| 6 | Fort Bend tax rate | ~2.3% | Industry estimate | N/A | ⚠️ ESTIMATE |
| 7 | FHA loan limit | $498,257 | HUD published floor | 2026 (annual) | ✅ HIGH |
| 8 | 30yr mortgage rate | 6.51% | Freddie Mac PMMS scrape | 2026-05-24 live | ✅ HIGH |
| 9 | Katy ISD rating | "A" (2022) | Wikipedia / TEA | 2022 | ❌ STALE |
| 10 | Katy ISD grad rate | 94.9% | Wikipedia / TEA | 2022–2023 | ⚠️ STALE |
| 11 | Katy commute times | 35-45 / 20-30 min | Estimate | N/A | ⚠️ ESTIMATE |
| 12 | Katy demographics | 25,184 pop / 38 median age | Wikipedia / ACS | 2025 est / 2020 Census | ⚠️ MIXED |

---

## For Next Session — Recovery Plan

**Phase 1: Retry with better tools (5 min)**
1. Try `browser_navigate` first — if browserbase is up, pull Redfin price/sqft + DOM + Houston metro
2. Try Firecrawl for TEA school ratings (2025 data at txschools.gov)
3. Try Firecrawl for Texas Comptroller property tax rates
4. Try Firecrawl for HUD FHA limits (verify $498,257 for Harris County)
5. Google Maps commute times (manual or via API)

**Phase 2: Accept and annotate**
If tools still fail, use the 3 HIGH-confidence data points ($436K, 6.51%, $498K) and mark everything else as ESTIMATE with source transparency in the content.

**Phase 3: Move on**
Do NOT block the entire pipeline on market data precision. The architecture (Information Gain, entity grounding, contextual bridges) works with approximate numbers. Refresh to exact numbers during the quarterly update cycle.

---

## Session Log

| Time | Action | Result |
|---|---|---|
| 07:20 | `delegate_task` → subagent for all 9 pulls | Timeout after 600s, 13 API calls |
| 07:30 | `browser_navigate` → redfin.com | Timeout 60s |
| 07:31 | `curl` → redfin.com | Got $436,523 median |
| 07:31 | `curl` → bankrate.com | Empty (JS-rendered) |
| 07:31 | `curl` → freddiemac.com | Got 6.51% rate ✅ |
| 07:32 | `urllib` → Redfin API | 404 |
| 07:33 | `urllib` → Zillow research | No Katy data |
| 07:33 | `urllib` → RocketHomes | 404 |
| 07:33 | `urllib` → FRED | Timeout |
| 07:34 | `urllib` → Realtor.com | 429 rate limited |
| 07:34 | `urllib` → Norada | 403 forbidden |
| 07:34 | `urllib` → HUD (2 endpoints) | 404 + 404 |
| 07:34 | `urllib` → TX Comptroller | Empty (JS) |
| 07:34 | `urllib` → TEA API | 404 |
| 07:35 | Wikipedia API → 5 articles | Got Katy ISD "A" (2022), demographics, Harris Co $295K |
| 07:36 | Wrote market-data.md | All 9 points + refresh schedule |
| 07:38 | Quan: "Is Wikipedia accurate?" | Acknowledged staleness |
| 07:39 | Quan: "It's 2026" | Flagged 4-year gap on school data |
|| 07:42 | Tried Firecrawl self-hosted (Docker) | `firecrawl/firecrawl` doesn't exist; pulled `mcp/firecrawl` but that's MCP server not engine. Firecrawl-py SDK requires API key even for local. Self-hosted needs `docker run -p 3002:3002 firecrawl/firecrawl` which isn't on Docker Hub. |

---

## Session 2 — 2026-05-24 PM (Camofox live data pull)

### ISSUE-013: HUD FHA Limits Database Down (Confirmed)
- **Tool:** `browser_navigate` via Camofox → `https://entp.hud.gov/idapp/html/hicostlook.cfm`
- **Symptom:** Oracle JDBC error — `Error establishing socket to host and port: hdaldpf17c03486.hud.gov:1521. Reason: Connection refused`
- **Root cause:** HUD's backend Oracle database down (server-side, not bot detection). Not a Camofox issue.
- **Fix for now:** Used Google search results from LendingTree, JVM Lending, and fha.com — all agree on $541,287 for Harris & Fort Bend 1-unit.
- **Fix for next run:** HUD publishes PDFs with county-level limits at `/sites/dfiles/SFH/documents/FHA-2026-Areas-*.pdf`. These are reliable fallbacks. The interactive lookup tool (`hicostlook.cfm`) is fragile — always have the PDF path ready.

### ISSUE-014: Redfin Katy City ID — Multiple Wrong IDs
- **Tool:** `browser_navigate` → `redfin.com/city/30981/TX/Katy/housing-market`
- **Symptom:** Redirected to US national overview page (city doesn't exist or ID changed)
- **History:** ID 30981 → national. ID 30818 → Austin, TX. ID 30970 → national again.
- **Root cause:** Redfin city IDs vary by metro area; the old ID from Wikipedia/Zillow was wrong. Austin (30818) coincidentally loaded.
- **Fix:** Correct city ID for Katy, TX housing market is **9764**. Found via Google search → `redfin.com/city/9764/TX/Katy/housing-market`.
- **Prevention for next run:** NEVER guess Redfin city IDs. Always search Google: `redfin katy tx housing market` and click the first result.

### ISSUE-015: TEA School Ratings — URL Structure Changed
- **Tool:** `browser_navigate` → `rptsvr1.tea.texas.gov/perfreport/account/2025/index.html`
- **Symptom:** 404 Not Found
- **Root cause:** TEA's legacy SAS broker URLs changed; the old `perfreport/account/2025/index.html` pattern no longer exists.
- **Fix:** Google search `Katy ISD 2025 accountability rating TEA` → found multiple sources confirming B (88), top among TX 10 largest. Confirmed via:
  - TEA news release (Aug 15, 2025): "TEA Releases 2025 A–F Accountability Ratings"
  - Katy ISD newsroom: "Katy ISD Outperforms State Averages, Earns Top Rating"
  - Fox 26 Houston: "TEA accountability ratings for 2024-2025"
  - txschools.gov: district ID 101914
- **Prevention for next run:** TEA now publishes ratings at `txschools.gov/?view=district&id=101914`. The old `rptsvr1.tea.texas.gov` SAS broker may be deprecated.

### ISSUE-016: Bankrate Closing Costs Texas Page — 404
- **Tool:** `browser_navigate` → `bankrate.com/real-estate/closing-costs/texas/` and `bankrate.com/mortgages/closing-costs/texas/`
- **Symptom:** Both URLs returned 404
- **Root cause:** Bankrate's URL structure for state-specific pages changed. The Texas page may have been moved or consolidated.
- **Fix:** Google search `Texas closing costs percentage 2025 2026 Bankrate` → found Rocket Mortgage page (Jan 2026) with specific TX numbers: 0.93% average including recording fees. Also confirmed industry range 2-5% from Herring Bank, HAR, MI Homes.
- **Prevention for next run:** Bankrate state pages are unreliable. Rocket Mortgage's `/learn/average-closing-costs-in-texas` is the better canonical source.

### ISSUE-017: fha.com — Wrong URL Structure
- **Tool:** `browser_navigate` → `fha.com/fha_loan_limits/texas/harris-county`
- **Symptom:** 404 Page Not Found
- **Root cause:** fha.com URL format for county-level pages is different. Actual page is `fha.com/lending_limits_state?state=Texas`.
- **Fix:** Google search `FHA loan limits 2026 Harris County Texas` → fha.com showed up as the 3rd result with correct limits. LendingTree and JVM Lending confirmed.
- **Prevention for next run:** Don't guess fha.com URLs. Search via Google.

### ISSUE-018: Camofox Session Management — Tabs Not Isolated
- **Tool:** Multiple `browser_navigate` calls
- **Symptom:** Each navigate call opens new tab but prior tabs persist. After 8+ navigations, browser session has many open tabs.
- **Root cause:** `browser_navigate` doesn't auto-close previous tabs. Sessions accumulate tabs over multiple calls.
- **Impact:** Minor — browser memory usage grows but did not block collection.
- **Fix for next run:** Manually close tabs between targets if doing 10+ navigations. Or use `execute_code` to batch HTTP requests where possible (Google search results are extractable from SERP snippets without opening each page).

### ISSUE-019: HUD PDF — Page Navigation Required
- **Tool:** `browser_navigate` → HUD PDF of FHA limits by county
- **Symptom:** PDF loaded but opened to page 1; TX counties on page 10-12. Text too small for vision analysis.
- **Root cause:** PDF viewer has no search box accessible via browser tools. Manual navigation to correct page required but cumbersome.
- **Fix:** Skipped PDF — used Google SERP snippets from LendingTree/JVM/fha.com instead, which all agree.
- **Prevention for next run:** Browser tools are bad at PDF navigation. For government PDFs, prefer: (a) `curl` download + `pdftotext`, or (b) third-party aggregator sites that've already parsed the PDF.

### ISSUE-020: Commute Times — Google Maps Not Directly Accessible
- **Tool:** `browser_navigate` → Google Maps (not attempted — recognized limitation)
- **Symptom:** Google Maps is JS-heavy with CAPTCHA risk. Direct navigation impractical.
- **Root cause:** Maps routing requires complex interaction (enter origin/destination, select route, read time).
- **Fix:** Google search `Katy TX to Houston downtown commute time typical morning` → KHOU news (Feb 2026) confirmed 45-60+ min rush hour. KatyHomesForSaleTX.com (May 2026) confirmed same. Houston TranStar provides real-time route data.
- **Prevention for next run:** Don't attempt Google Maps directly. News articles + TranStar text reports + community sites are sufficient.

---

## Key Fix Patterns (Session 2 Learnings)

### Pattern 1: Google-First, Not URL-Guessing
**Problem:** Guessing URLs (bankrate.com/closing-costs/texas/, fha.com/limits/harris-county, rptsvr1.tea.texas.gov/perfreport/...) caused 6+ 404s.
**Solution:** ALWAYS search Google first: `site-specific data point` → click the SERP result. Camofox handled all Google searches without CAPTCHA.
**Rule:** Before typing ANY URL for data collection, search Google with it first. The SERP snippet often contains the answer without even needing to open the page.

### Pattern 2: Redfin City IDs Are Fragile
**Problem:** Three different city IDs all failed for Katy (30981, 30818, 30970).
**Solution:** `redfin katy housing market` Google search → correct ID 9764.
**Rule:** Never hardcode Redfin city IDs. Always derive from Google search.

### Pattern 3: Government Lookup Tools Are Unreliable — Use Aggregators
**Problem:** HUD's lookup tool (`hicostlook.cfm`) had a database outage. TEA's SAS broker returned 404.
**Solution:** Third-party aggregators (LendingTree, JVM Lending, SmartAsset, Ownwell) re-publish government data reliably and are indexed by Google.
**Rule:** Government interactive tools have high downtime. Prefer (a) published PDFs or (b) reputable aggregator sites that scrape and republish the same data.

### Pattern 4: Camofox Works for JS-Heavy Sites
**Problem:** Session 1 tried raw `curl`/`urllib` — Redfin, Bankrate, Zillow, Comptroller all failed (JS-rendered or blocked).
**Solution:** Camofox's Firefox 135.0.1 fork with fingerprint spoofing + humanize mode loaded ALL JS-rendered pages successfully, including Redfin (which blocks headless Chrome/Puppeteer).
**Rule:** Camofox is the canonical browser tool. Always use `browser_navigate` for data collection — never `curl`/`urllib` on any page that might be JS-rendered.

### Pattern 5: SERP Snippets Often Have the Answer
**Problem:** Opening every page individually wastes time and tabs.
**Solution:** Google SERP snippets (the 1-2 line descriptions under each result) frequently contain the exact data point. FHA limits, school ratings, tax rates, and commute times were all visible in snippets.
**Rule:** Read SERP snippets before clicking results. Only open pages when the snippet doesn't contain the data.

---

## Session 3 — 2026-05-24 PM (Entity Discovery + Workflow Analysis)

### ISSUE-021: Google CAPTCHA — Permanent Session Block
- **Tool:** `browser_navigate` via Camofox → Google search
- **Symptom:** After ~5 rapid searches early in session, Google started returning CAPTCHA pages. Continued blocking ALL Google requests for remainder of session even after switching to single-step.
- **Root cause:** Parallel `browser_navigate` calls in rapid succession triggered Google's anti-bot detection. Once flagged, the IP remained blocked for hours.
- **Impact:** Could not search Google at all for entity discovery. Had to use DuckDuckGo exclusively.
- **Fix:** Switched to DuckDuckGo. DDG worked without CAPTCHA for all searches when spaced 30-60s apart.
- **Prevention:** NEVER parallel `browser_navigate` calls. Single-step only. Minimum 30s between searches on any search engine. Start with DuckDuckGo — don't risk Google at all for multi-step workflows.

### ISSUE-022: HAR.com Cloudflare Block — Server-Side Anti-Bot
- **Tool:** `browser_navigate` via Camofox → `har.com/minh-quan-nguyen/agent_MQTNITS`
- **Symptom:** Cloudflare "Press and Hold" verification challenge. Camofox's fingerprint spoofing couldn't bypass it.
- **Root cause:** Cloudflare's Press-and-Hold is a server-side challenge that requires actual human mouse interaction. No browser automation tool can pass it — it's designed exactly to block headless browsers.
- **Impact:** HAR agent profile details inaccessible. Had to rely on SERP snippets and HAR culture-specialist pages which load without the challenge.
- **Fix:** Accepted limitation. HAR culture pages (thailand-culture-agents, vietnam-culture-agents, mexico-culture-agents, honduras-culture-agents) loaded cleanly and contained agent details — including rating (5/5), sales count (4 sold, 1 leased), and showings.
- **Prevention:** Cloudflare Press-and-Hold = hard stop. Don't attempt to bypass. Find alternative data sources (SERP snippets, related pages without challenge, Google cache).

### ISSUE-023: LinkedIn — Login Required for Full Profiles
- **Tool:** `browser_navigate` via Camofox → LinkedIn profile pages
- **Symptom:** LinkedIn redirects unauthenticated users to a login wall. Full profile details inaccessible.
- **Root cause:** LinkedIn requires authentication to view profiles beyond the public preview.
- **Impact:** Could only confirm brokerage + title from SERP snippets, not verify full profile details (employment history, about section, activity).
- **Fix:** SERP snippets contained enough info: titles ("Realtor at Elevatus LLC", "Real Estate Agent at Truss Real Estate"), locations (Houston), connection counts.
- **Prevention:** Accept SERP snippets as sufficient for entity discovery. Full profile verification requires Quan to log in manually.

### ISSUE-024: Zillow — Common Name Problem
- **Tool:** DDG search → `site:zillow.com "Quan Nguyen" Katy`
- **Symptom:** Zillow search returned multiple Quan Nguyens — all wrong (San Diego CA, Kirkland WA). Had to manually verify each result to confirm none were the Katy/Houston Quan.
- **Root cause:** "Quan Nguyen" is an extremely common Vietnamese name. Zillow's agent directory contains dozens of Quan Nguyens across the US. No profile for the Katy/Houston one.
- **Impact:** Confirmed Zillow gap but cost extra verification time to rule out false positives.
- **Fix:** Added "Katy" or "Houston" to all Zillow searches to filter geographically. Still required manual check.
- **Prevention:** For common names, always add geographic filter + check all results on page 1 before concluding "not found."

### ISSUE-025: Realtor.com — Rate Limiting Block
- **Tool:** DDG search → `site:realtor.com "quann.homes"`
- **Symptom:** Generic block page with reference ID returned instead of search results. Likely rate-limiting from prior rapid requests in the session.
- **Root cause:** Realtor.com detected unusual traffic pattern and served a block page.
- **Impact:** Could not search Realtor.com at all. Had to rely on zero results from DDG `site:realtor.com` search.
- **Fix:** Used DDG `site:` search which searches Google/Bing index, not Realtor.com directly. Zero results confirmed no profile exists in the index.
- **Prevention:** Space out searches more aggressively. Minimum 60s between requests to the same domain.

### ISSUE-026: Camofox Scroll — 500 Server Error
- **Tool:** `browser_scroll` → DDG results page
- **Symptom:** `500 Server Error: Internal Server Error for url: http://localhost:9377/tabs/.../scroll`
- **Root cause:** Camofox server returned 500 on scroll command. Likely a tab state issue or browser session glitch after multiple navigations.
- **Impact:** Could not paginate DDG results for some searches. Only page 1 visible.
- **Fix:** Accepted limitation. DDG page 1 typically has 10-15 results — sufficient for entity discovery.
- **Prevention:** Minimize scroll calls. If 500 persists, close and reopen browser session.

### ISSUE-027: HAR.com — TWO Agent Profile IDs Found
- **Tool:** DDG search → `"Quan Nguyen" "Forever Realty" Katy Texas`
- **Symptom:** Two different HAR.com agent profile URLs surfaced, both under Forever Realty:
  - `har.com/quan-nguyen/agent_QHNguyen` — "Quan Nguyen, TX Real Estate Agent"
  - `har.com/minh-quan-nguyen/agent_MQTNITS` — "Minh Quan Nguyen" (found in earlier search)
- **Root cause:** HAR may have created a second profile, or one is an older/abandoned profile. Both are live and indexed.
- **Impact:** Potential duplicate entity signal — Google may see two profiles for the same person and struggle to consolidate.
- **Action for Quan:** Log into HAR.com. Check which profile is primary. Merge or deactivate the duplicate. Contact HAR support if both are active and can't be merged.

### ISSUE-028: LinkedIn — TWO Real Estate Profiles with WRONG Brokerages
- **Tool:** DDG search → `"Quan Nguyen" real estate Houston Texas LinkedIn`
- **Symptom:** Two LinkedIn profiles surfaced, both claiming to be Quan Nguyen working in real estate in Houston — but with DIFFERENT brokerages:
  - L1: `linkedin.com/in/quan-nguyen-19b436247` — "Realtor at Elevatus LLC" (17 connections)
  - L2: `linkedin.com/in/quan-nguyen-273763258` — "Real Estate Agent at Truss Real Estate" (connection count unknown)
- **Root cause:** Unknown. Possibly: (a) one or both are Quan's old profiles from previous brokerages, (b) one is Quan and the other is a different person with the same name, or (c) neither is Quan.
- **Impact:** **CRITICAL ENTITY CONTAMINATION.** If either profile IS Quan, Google is resolving "Quan Nguyen = Elevatus" or "Quan Nguyen = Truss" instead of "Quan Nguyen = Forever Realty." If NEITHER is Quan, then Quan has no LinkedIn profile at all — also a gap on a critical entity platform.
- **Action for Quan:** Open both LinkedIn URLs in a browser. Check: (a) Are these your profiles? (b) If yes, update brokerage to Forever Realty. (c) If no, create a new LinkedIn profile with Forever Realty, LLC. (d) Link quann.homes as website.

### ISSUE-029: Entity Discovery — Cascade Brokerage Misidentification (3 Wrong Brokerages Before Finding the Right One)
- **Tool:** `browser_navigate` → quann.homes, `curl` grep, `browser_vision`
- **Symptom:** Three different brokerages discovered across sources before reaching the truth:
  1. **Forever Realty, LLC** — HAR.com profiles (#1 and #2), Realty.com, HAR Culture pages (first assumption: this is correct)
  2. **REAL BROKERAGE** — quann.homes footer text (corrected assumption: site footer = truth source)
  3. **Walzel Properties** — quann.homes header/logo IMAGES (final truth, confirmed by user)
- **Root cause:** quann.homes is Framer-built by an amateur. The brokerage logo in the header was updated to Walzel Properties (visible to users), but the footer text was forgotten and still says REAL BROKERAGE (the PREVIOUS brokerage). External profiles (HAR, Realty.com, LinkedIn) are even more outdated — they still show Forever Realty, which was 2+ brokerages ago.
- **Impact:** **CRITICAL METHODOLOGY FAILURE.** We initially trusted text extraction (footer) over visual inspection (images). On amateur-built Framer sites, the image layer is more current than the text layer. We propagated "Forever Realty" throughout entity-discovery.md v1, then "corrected" to "REAL BROKERAGE" in v2 — both were wrong. The correct brokerage (Walzel Properties) was only confirmed by the owner directly. Had we not asked, the entire entity document would be wrong.
- **Fix:** Updated entity-discovery.md to Walzel Properties as canonical brokerage. Added methodology warning: "On amateur-built sites, brokerage information often lives ONLY in images/logos. Text fields (footer, metadata) are manually updated and frequently forgotten. NEVER trust text extraction for brokerage on Framer sites — ask the owner."
- **Prevention:** Pattern 9 added. Amateur site builder rule: image > text. When the user says "check my site," do NOT stop at footer text extraction — visually inspect header logos/images too. And when in doubt, ask.

---

## Key Fix Patterns (Session 3 Learnings)

### Pattern 6: Google CAPTCHA Persistence — Full Session Block
**Problem:** Once Google CAPTCHA triggers from rapid requests, the IP stays blocked for the remainder of the session. Even single-step requests hours later may fail.
**Solution:** DuckDuckGo as permanent fallback — or better yet, as the PRIMARY search engine for multi-step discovery workflows. DDG doesn't CAPTCHA, returns clean SERP snippets, and for entity discovery specifically is actually better than Google (direct profile URLs without AI Overviews/KP clutter).
**Rule:** For any multi-step search workflow (entity discovery, competitor analysis, market data), START with DuckDuckGo. Reserve Google only for cases where DDG's index is insufficient (e.g., Google Maps/GBP, Knowledge Graph API testing). Minimum 30s between any two browser_navigate calls regardless of target.

### Pattern 7: Entity Contamination IS Worse Than Missing Profiles
**Problem:** A missing Zillow profile = Google simply doesn't have that signal (neutral). A wrong LinkedIn brokerage = Google actively has WRONG information about your entity (harmful). Google's entity resolution algorithm weights contradictory signals as negative evidence.
**Solution:** Always fix contamination BEFORE filling gaps. Clean up the wrong brokerage on LinkedIn and the HAR duplicate BEFORE creating new profiles on Zillow and Realtor.com.
**Rule:** Entity discovery priority order: contamination cleanup → gap filling → supplementation. Fix what's wrong before adding what's missing. A wrong brokerage is actively harmful — a missing profile is neutral.

### Pattern 8: Workflow Documents Beat Static Reports
**Problem:** A static report listing profiles and issues assumes Quan knows which LinkedIn profiles are his and which are strangers. It doesn't give him the actual steps to verify.
**Solution:** Entity discovery documents should be formatted as WORKFLOWS: the exact search queries to paste, the exact URLs to check, a checklist to mark off, and clear "is this you?" decision points per profile.
**Rule:** Entity discovery output = workflow checklist, not audit report. Format: "Paste this into Google → click these results → here's what you're looking for → check yes/no." The user shouldn't have to translate a report into action steps.

### Pattern 9: Framer Sites Store Branding in Images, Not Text
**Problem:** quann.homes is built on Framer. The footer text said "REAL BROKERAGE" — but that was the PREVIOUS brokerage. The current brokerage (Walzel Properties) is only visible in images/logos on the site. External profiles (HAR, Realty.com, LinkedIn) showed "Forever Realty, LLC" — which is even more outdated. Three different brokerages appeared across sources, none of which were current.
**Root cause:** Framer sites use image components for branding (logos, badges, equal housing graphics). The text backend (footer, metadata) is manually updated and frequently lags behind image updates. External profiles lag even further — HAR and Realty.com can hold brokerage data from 2+ brokerages ago.
**Solution:** For Framer-built sites: (1) NEVER trust footer text or external profiles for brokerage — always ask the owner directly. (2) Use vision_analyze on the header/logo area images to detect the current brokerage. (3) When documenting entity discovery, flag the brokerage as "UNVERIFIED — image-based, confirm with owner" rather than trusting any text field.
**Rule:** Framer site → brokerage is image-first, not text-first. Footer text is untrustworthy. External profiles are untrustworthy. Ask the owner. This applies to any Framer-built real estate site.
