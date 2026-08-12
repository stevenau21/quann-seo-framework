---
name: seo-entity-discovery
description: Discover and audit external web profiles for a person/brand entity — real estate agent SEO focused. Uses site-specific DuckDuckGo searches to find Zillow, Realtor.com, HAR, LinkedIn, Facebook, GBP profiles. Checks NAP consistency and sameAs readiness.
version: 1.0.0
metadata:
  hermes:
    tags: [SEO, Entity Discovery, Real Estate, NAP, sameAs]
---

# SEO Entity Discovery

Discover and audit external web profiles for a real estate agent or brand. This is Category C in the holistic SEO topical map pipeline (after market data). The goal is to find every platform where the agent appears, check NAP consistency, and identify gaps for entity consolidation.

## Platforms to Check (in priority order)

| # | Platform | Search Query | Why It Matters |
|---|---|---|---|
| 1 | Zillow | `"Full Name" site:zillow.com` | #1 real estate search platform; Google treats profiles as authoritative |
| 2 | Realtor.com | `"domain.com" site:realtor.com` | Official NAR site, strong entity signal |
| 3 | HAR.com (TX) | `"Full Name" site:har.com` | MLS-sourced profile, highly trusted by Google for Houston agents |
| 4 | LinkedIn | `"Full Name" brokerage site:linkedin.com` | Person-entity signal; wrong brokerage = entity contamination |
| 5 | Facebook | Search full name + "realtor" | Social entity signal; page likes = trust proxy |
| 6 | Google Business Profile | Manual check at maps.google.com | Most impactful local SEO profile; cannot be checked via search |
| 7 | Realty.com | `"Full Name" site:realty.com` | Aggregator that syndicates; often auto-created, may be unclaimed |
| 8 | Own domain | Navigate directly | Canonical entity home; should link to all other profiles |

## Method

### Step 1: General Discovery
Search `"[Full Name] real estate [City] [State]"` on DuckDuckGo (NOT Google — Google CAPTCHA-blocks after ~5 rapid searches from server IPs). DDG returns clean SERP snippets without anti-bot challenges.

Review ALL results on first page. Note: URLs, snippets, and any metrics visible in search results.

### Step 2: Platform-Specific Searches
For each platform, use `site:` operator:
```
"Quan Nguyen" site:zillow.com
"quann.homes" site:realtor.com
"Quan Nguyen" site:har.com
"Quan Nguyen" realtor Katy site:linkedin.com
```

Common name problem: If the name is common (Quan Nguyen, John Smith), site: searches will return wrong individuals. Filter by:
- Location (Katy, Houston, TX)
- Domain mention (quann.homes)

If no results after filtering, the profile does NOT exist — document as MISSING.

**CRITICAL — Brokerage Field is the Most Volatile Attribute:** External profiles (LinkedIn, HAR.com, Realty.com) frequently retain OLD brokerage affiliations long after the agent switches brokerages. LinkedIn profiles show Elevatus/Truss/Yong from past affiliations. HAR.com and Realty.com syndicate MLS data that may be months stale. **The canonical brokerage source is the agent's own site** (quann.homes), but even that requires visual inspection on Framer-built sites — brokerage often appears only in images/logos, NOT in crawlable text. Footer text may be outdated. Always cross-check: visual site inspection + user confirmation, never trust a single text source.

### Step 3: Profile Audit
For each profile found, extract:
- URL
- Display name (exact string)
- Brokerage/company
- Location/city
- Metrics (reviews, sales, likes)
- Whether claimed or auto-generated
- Whether it links back to the agent's own domain (sameAs)

### Step 4: NAP Consistency Check
Build a table comparing Name, Address/Area, and Phone/Contact across all platforms. Flag:
- ❌ Different name format (Minh Quan Nguyen vs Quan Nguyen) — minor, but note
- ❌ Wrong brokerage (Elevatus LLC on LinkedIn when agent is at Forever Realty) — **actively harmful**
- ❌ Different city (Sugar Land vs Katy vs Houston — all are Houston metro but not identical)

### Step 5: sameAs Audit
Check bidirectional linking:
- Does each profile link to the agent's own domain?
- Does the agent's domain link to each profile (via JSON-LD or footer links)?

Google consolidates person-entities by following these links. Without cross-links, each profile is a separate entity.

### Step 6: Gap Report
Document:
- Profiles confirmed present (with URLs and status)
- Profiles confirmed missing (Zillow and Realtor.com are highest-impact gaps)
- Profiles unverifiable (GBP requires manual check; HAR.com may be CAPTCHA-blocked)
- Priority actions ranked by SEO impact

## Known Pitfalls

### Pitfall 1: Google CAPTCHA
Google blocks rapid searches from server IPs (even with Camofox fingerprint spoofing). After ~5 searches, all queries return CAPTCHA or blank pages. **Fix:** Use DuckDuckGo for discovery. DDG has no CAPTCHA, supports site: operator, and returns equivalent results for entity discovery.

### Pitfall 2: Cloudflare Anti-Bot
HAR.com and some real estate platforms use Cloudflare's "Press & Hold" challenge. This is server-side — even Camofox's fingerprint spoofing cannot pass it. **Fix:** Document as "exists but blocked — manually verify." A human can clear the CAPTCHA once and extract the profile URL/content.

### Pitfall 3: Common Names
Agents with common names (Quan Nguyen, Maria Garcia, David Kim) will have many false positives in search. Filter by location + brokerage, not just name.

### Pitfall 4: Unclaimed Profiles
Realty.com and similar aggregators auto-create profiles from MLS data. These profiles EXIST but the agent has no control over NAP/bio/links. Flag as "unclaimed — needs claiming."

### Pitfall 5: LinkedIn Requires Login
LinkedIn blocks non-logged-in users from viewing full profiles. SERP snippets provide enough info to identify brokerage mismatch but not all details. For full audit, manual login needed.

## Output

Save results to `SEO-{domain}/entity-discovery.md` with:
1. Table of all platforms checked with status (✅/❌/⚠️)
2. NAP consistency matrix
3. sameAs audit findings
4. Priority-ranked action items (P0/P1/P2)

## Priority Ranking

| Priority | Criteria | Examples |
|---|---|---|
| P0 | Profile missing on high-impact platform | Zillow, GBP not found |
| P1 | Existing profile has wrong/conflicting data | LinkedIn showing wrong brokerage |
| P1 | Profile exists but unclaimed | Realty.com unclaimed |
| P2 | Profile exists but not cross-linked | Facebook doesn't link to own domain |
| P2 | Profile needs manual creation | Realtor.com, GBP |
| P3 | sameAs JSON-LD missing on own domain | Own site doesn't declare profiles |
| P3 | Bidirectional linking between all profiles | Cross-link all platforms |
