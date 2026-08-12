# Competitor Analysis — What We Need to Know

**Date:** 2026-05-04 (Revised 2026-05-05)
**Status:** Simplified — manual review, not automated crawl
**Context:** Quan is a buyer's agent at REAL BROKERAGE, Katy TX. He already has content (FTHB guide, out-of-state guide). We need to know what competitors cover to find gaps — not scrape their entire site.

---

## Quan's Positioning

Before analyzing competitors, understand what Quan is:

- **Buyer-focused** (not listing-heavy)
- **Texas-wide** (Katy hub, serves Houston/Austin/Dallas/RGV)
- **Content already exists:** FTHB steps guide, comprehensive out-of-state relocation guide (11 sections), Texas FTHB guide
- **Differentiator:** "Get paid to buy" — builder credits, incentives, negotiation
- **Tech-enabled:** AI chatbots on site and Instagram, LightRAG knowledge base

Most competitors are listing agents first, buyers second. Quan's buyer-first angle IS the differentiator.

---

## Manual Review Process (NOT automated crawl)

### Step 1: Find 5 competitors (15 min)

Search Google (no proxy needed — manual):
```
"best buyer agent Katy TX"
"Katy TX realtor first time home buyer"
"Houston relocation real estate agent"
"Katy real estate agent blog"
"Katy TX real estate team"
```

Open top 3 organic results per query (not ads). Pick 5 agents/teams with:
- Active websites (not just Zillow profiles)
- Some content (blog, guides, or market pages)
- Based in Katy or West Houston

### Step 2: For each, answer these questions

```yaml
agent_name: ""
website: ""
brokerage: ""
buyer_focused: (yes/mixed/listing-first)
has_blog: (yes/no)
blog_topics: []     # Skim last 5-10 post titles
has_area_guides: (yes/no)
area_guide_topics: []
has_seller_content: (yes/no)
has_market_data: (yes/no)
contact_cta: ""     # "Call now" vs "Schedule consultation" vs "Home valuation"
tone: ""            # Aggressive sales vs educational vs luxury
```

### Step 3: Build simple coverage matrix

```
Topic                    | Quan | C1 | C2 | C3 | C4 | C5
--------------------------|------|----|----|----|----|----
First-time buyer guide    |  ✅  |    |    |    |    |
Out-of-state guide        |  ✅  |    |    |    |    |
Neighborhood guide        |  ❌  |    |    |    |    |
School ratings            |  ❌  |    |    |    |    |
Market stats/trends       |  ❌  |    |    |    |    |
Down payment help         |  ❌  |    |    |    |    |
Property tax guide        |  ❌  |    |    |    |    |
Rent vs buy               |  ❌  |    |    |    |    |
Seller guide              |  ❌  |    |    |    |    |
Home value estimator      |  ❌  |    |    |    |    |
```

Fill by checking each competitor's blog index and navigation.

### Step 4: Analyze findings

- **What does EVERYONE cover?** → Table stakes, we need it too (or acknowledge and link out)
- **What does NO ONE cover?** → Golden gaps — own these
- **What do 1-2 cover?** → Opportunity to do it better

---

## Expected Findings (based on Katy market)

Most Katy agents are listing-focused. Common patterns:

| Typical Competitor | Quan |
|---|---|
| "What's your home worth?" CTA | "Let's find your next home" CTA |
| Seller guides, staging tips | Buyer guides, incentives |
| Market reports for sellers | Market data contextualized for buyers |
| Luxury listing galleries | Builder/community spotlights |

**Quan's gap is also his differentiator:** he's one of few buyer-first agents with actual content. The competitors' gap (seller content) is irrelevant — Quan doesn't need to match them there unless he wants seller leads.

---

## What to Actually Look For

Skip the automated crawl. Spend 2 hours manually:

1. **Which agents have good content?** → If 1-2 do, study them closely
2. **What buyer questions do they answer that Quan doesn't?** → Steal the question, write a better answer
3. **Do any have neighborhood guides?** → If no, that's a massive gap to own
4. **Do any rank for "Katy neighborhood guide" or similar?** → Check manually
5. **How's their SEO?** → Quick check: meta titles, heading structure, page speed

---

## Output File

Single markdown file: `09-research/competitor-notes.md`

```
# Competitor Analysis — [Date]

## Competitor 1: [Name]
- Website: [url]
- Brokerage: [name]
- Summary: [2-3 sentences]
- Content coverage: [topics]
- Our advantage: [what we do better]

## Competitor 2: [Name]
...

## Gap Matrix
[filled table]

## Key Takeaways
- Golden gaps to own: []
- Table stakes to add: []
- Competitors to watch: []
```

---

## Bottom Line

This was framed as a complex proxy-backed crawling operation. It's actually a **2-hour manual Google session**. The value isn't in the scrape — it's in the synthesis of "what are 5 local agents writing about, and where are the obvious holes?"
