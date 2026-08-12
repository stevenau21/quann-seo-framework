# Web Entity — Quann.Homes (Grounded)

**Date:** 2026-05-04 | **Revised:** 2026-05-05 (alignment audit + cross-references)
**Status:** Revised — discovery mode, not audit mode. We don't know what exists.

> **Related:** [Proactive Entitization Strategy](../09-research/proactive-entitization-strategy.md) — step-by-step plan to create and verify external profiles. [Knowledge Graph API Audit](../09-research/knowledge-graph-api-audit.md) — verifying entity recognition.

---

## What We Know Exists

| Platform | Status | Evidence |
|---|---|---|
| quann.homes | ✅ Live | Verified May 4. Framer-built. 9 pages. |
| Instagram | ✅ Active | From previous context — Quanbot DM automation |
| Telegram | ✅ @QuannBot | Gateway for bot management |
| Phone | ✅ (832) 400-3152 | Confirmed in RAG |
| Email | ✅ quan@thequantumteam.net | Confirmed in footer |

**That's it.** Everything below is unconfirmed.

---

## What We DON'T Know

We have not verified ANY of these:

- Google Business Profile — may exist, may not. Haven't checked.
- Zillow agent profile — same.
- Realtor.com profile — same.
- HAR.com profile — same (Quan IS a HAR member if licensed in Houston, but profile may not be set up).
- LinkedIn — same.
- REAL BROKERAGE agent directory listing — same.
- Homes.com, Redfin, Facebook, Yelp, BBB, Nextdoor — all unconfirmed.
- Katy Chamber of Commerce — same.

---

## NAP Reference (What SHOULD Be Consistent)

When we DO find profiles, they should match:

```
Display Name:   Quan Nguyen
Full Legal:     Minh Quan T Nguyen (where required)
License:        #0774451
Brokerage:      REAL BROKERAGE
Team:           The Quantum Team
Phone:          (832) 400-3152
Email:          quan@thequantumteam.net
Website:        https://quann.homes
Location:       Katy, TX
Areas Served:   Houston, Austin, Dallas, Rio Grande Valley
```

---

## Discovery Process (To Do)

**Step 1: Search (1 hour, manual)**
For each platform below, search Quan's name. Record what you find.

```
Google Business Profile → Google "Quan Nguyen real estate Katy TX"
Zillow → Search zillow.com for "Quan Nguyen"
Realtor.com → Search realtor.com for "Quan Nguyen Katy TX"
HAR.com → HAR member directory
LinkedIn → linkedin.com search
Facebook → Business pages
Others: Homes.com, Redfin, Yelp, BBB, Nextdoor
```

**Step 2: For each profile found, record:**
- URL
- Name as displayed on platform
- Phone number shown
- Brokerage shown
- Does it link to quann.homes?
- Reviews: count + rating
- NAP matches reference? (yes/no)
- Action needed? (none / update / claim / create)

**Step 3: Prioritize**
- Fix first: Google Business Profile, Zillow, Realtor.com (local SEO signals)
- Fix second: HAR.com, LinkedIn (professional authority)
- Fix third: everything else

---

## Ideal End State (Not Current State)

When complete, Google should see:
1. **GBP claimed and verified** with correct category, NAP, 10+ reviews
2. **Zillow/Realtor.com profiles** with consistent NAP, linking to quann.homes
3. **Same NAP** on every profile — no variation
4. **sameAs** in quann.homes JSON-LD listing all profile URLs
5. **Reviews** distributed across platforms (not all on one)

**Current state:** Unknown. Probably none of this exists.

---

## What NOT to Do

- Don't assume profiles exist and just need tweaking
- Don't build automated audit scripts before confirming profiles exist
- Don't create profiles on 13 platforms in one sprint — start with the top 3
- Don't add sameAs URLs to schema until profiles are verified
