# Web Entity Audit — What to Check

**Date:** 2026-05-04 (Revised 2026-05-05)
**Status:** Simplified — manual audit, not automated crawl
**Context:** Verify Quan's external profiles exist, are consistent, and link back to quann.homes. This is about entity consolidation, not scraping.

---

## NAP Reference (Must Be Identical Everywhere)

```
Display Name:   Quan Nguyen
Full Legal:     Minh Quan T Nguyen (only where legally required)
License:        #0774451
Brokerage:      REAL BROKERAGE
Team:           The Quantum Team
Phone:          (832) 400-3152
Email:          quan@thequantumteam.net
Website:        https://quann.homes
Location:       Katy, TX
Areas Served:   Houston, Austin, Dallas, Rio Grande Valley
```

The footer of quann.homes already says:
> "© 2025 MINH QUAN NGUYEN, REALTOR | LICENSE #0774451 | REAL BROKERAGE"

This is our anchor — external profiles must match.

---

## Manual Audit Checklist

### Tier 1 — Check These First (Local SEO signals)

| Platform | How to Check | Status |
|---|---|---|
| Google Business Profile | Google: "Quan Nguyen real estate Katy TX" → look for Knowledge Panel | ❓ |
| Zillow | Search zillow.com for "Quan Nguyen Katy TX" | ❓ |
| Realtor.com | Search realtor.com/realestateagents for Quan Nguyen in Katy | ❓ |
| HAR.com | HAR member directory search | ❓ |

### Tier 2 — Professional Profiles

| Platform | How to Check | Status |
|---|---|---|
| LinkedIn | linkedin.com search "Quan Nguyen real estate Houston" | ❓ |
| REAL BROKERAGE | realbrokerage.com agent directory | ❓ |
| Homes.com | Search agent directory | ❓ |
| Redfin | Redfin agent search | ❓ |

### Tier 3 — Social / Local

| Platform | How to Check | Status |
|---|---|---|
| Facebook | Business page for "The Quantum Team" or "Quan Nguyen Realtor" | ❓ |
| Instagram | Already known (@quann.homes or similar) → verify link to site | ✅ Known |
| Yelp | Search "Quan Nguyen real estate Katy" | ❓ |
| Nextdoor | Local business pages in Katy | ❓ |

### Tier 4 — Authority Signals

| Platform | Check |
|---|---|
| Katy Chamber of Commerce | Member directory — is Quan/Quantum Team listed? |
| BBB | Business profile exists? |
| Texas Real Estate Commission | License lookup confirms #0774451 is active |

---

## What to Record for Each Found Profile

```
Platform: [name]
URL: [full profile URL]
Name displayed: [exact text shown]
Phone: [number shown]
Brokerage: [name shown]
License #: [shown?]
Website linked: [URL shown]
Reviews: [count + rating]
NAP matches reference: [yes/no]
Action needed: [none / update phone / claim profile / merge duplicates]
```

---

## Common Issues (Based on Real Estate Agent Patterns)

1. **Old brokerage name** → If Quan moved to REAL BROKERAGE recently, old profiles may show previous brokerage
2. **Different phone** → Agent may have used personal cell before business line
3. **Name format** → Some platforms use "Minh Nguyen" not "Quan Nguyen" — inconsistency
4. **No website link** → Profile exists but doesn't link to quann.homes
5. **Zero reviews** → Profile claimed but empty → ask clients to leave reviews
6. **Duplicate Google profiles** → Common when agents move brokerages

---

## What to Do With Findings

1. **Consistency first:** Fix NAP mismatches everywhere
2. **Fill gaps:** Create profiles on missing platforms
3. **Add sameAs:** Compile all profile URLs → add to quann.homes JSON-LD
4. **Review generation:** Identify platforms with 0 reviews → strategy to collect

---

## Output

Single file: `09-research/web-entity-audit-findings.md`

```
# Web Entity Audit — Quan Nguyen

## Found Profiles
| Platform | URL | NAP Match? | Reviews | Action |
|---|---|---|---|---|
| GBP | ... | ✅/❌ | N/A | ... |

## Issues to Fix
1. ...
2. ...

## Missing Platforms
- [ ] Wikidata (create new item)
- [ ] ...

## sameAs URLs for Schema.org
- https://www.zillow.com/profile/...
- https://www.realtor.com/realestateagents/...
```

---

## Bottom Line

This is a **1-hour manual task**, not an automated crawl. The value is in verifying consistency and discovering gaps, not in scraping. If we find the profiles exist and are consistent → great, move on. If we find 3 different phone numbers across platforms → fix them.
