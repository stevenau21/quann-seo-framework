# Truth Range & Consensus Mapping — Quann.Homes

**Date:** 2026-05-05
**Status:** Pre-execution baseline — must be established before writing pages
**Methodology:** Per holistic SEO, content must fall within the consensus band of authoritative sources or be flagged for low accuracy

---

## What This Is

Google does not index "the truth" — it indexes **consensus**. A truth range is the band of acceptable factual claims that authoritative sources agree on. Your content can vary within this band, but claims outside it — without extraordinary proof — trigger accuracy flags.

---

## Ground Truth Sources for Texas Residential Real Estate

These are the sources Google already treats as authoritative for this niche:

### Tier 1 — Legal / Regulatory (Highest Trust)

| Source | Domain | What Google Uses It For |
|---|---|---|
| **Texas Real Estate Commission (TREC)** | trec.texas.gov | Licensing, forms, consumer protection, contract law |
| **Texas Department of Housing & Community Affairs (TDHCA)** | tdhca.state.tx.us | Down payment assistance, first-time buyer programs |
| **Texas Comptroller of Public Accounts** | comptroller.texas.gov | Property tax rates, homestead exemptions, tax code |
| **Texas Property Code / Tax Code** | statutes.capitol.texas.gov | Legal definitions, seller disclosures, title requirements |
| **HUD (Federal)** | hud.gov | FHA loan limits, fair housing, RESPA |
| **FHFA (Federal)** | fhfa.gov | Conventional loan limits |
| **USDA** | usda.gov | Rural development loans, eligible areas |

### Tier 2 — Data / Statistics (High Trust)

| Source | Domain | What Google Uses It For |
|---|---|---|
| **Federal Reserve Economic Data (FRED)** | fred.stlouisfed.org | Mortgage rates, housing starts, economic indicators |
| **Texas Real Estate Research Center (TRERC)** | recenter.tamu.edu | Market statistics, Texas housing reports |
| **U.S. Census Bureau** | census.gov | Population, household income, housing characteristics |
| **Texas Education Agency (TEA)** | tea.texas.gov | School district ratings, accountability |
| **Fannie Mae / Freddie Mac** | fanniemae.com, freddiemac.com | Conforming loan limits, mortgage market surveys |

### Tier 3 — Industry / Association (Moderate Trust)

| Source | Domain | What Google Uses It For |
|---|---|---|
| **National Association of Realtors (NAR)** | nar.realtor | Market forecasts, existing home sales, industry standards |
| **Texas Association of Realtors (TAR)** | texasrealestate.com | Texas-specific market reports, legal updates |
| **Houston Association of Realtors (HAR)** | har.com | Local market data, MLS statistics |
| **Austin / DFW / RGV Boards of Realtors** | various | Regional market data |

---

## Truth Ranges for Quan's Core Claims

For each factual claim Quan will make, here's the consensus band established by authoritative sources:

### Claim Cluster 1: Texas Home Prices

| Claim | Consensus Sources | Truth Range | Outside Range = Flagged |
|---|---|---|---|
| "Katy median home price" | HAR.com + Redfin + TRERC | Range: HAR report value ± 5% from Redfin | Claiming a number 15%+ different from both without citing a specific methodology |
| "Houston metro median price" | HAR.com + Redfin + NAR | HAR value ± 3% from NAR quarterly report | Same |
| "Texas median home price" | TRERC + NAR + Redfin | Tends to be within 2-4% across sources | Claiming outside this band without attribution |

**Rule for Quan:** Cite the specific source ("According to HAR's April 2026 market report..."). Don't say "Katy homes cost $385K" — say "HAR data shows the Katy median is $X." This aligns with consensus by attributing to the ground truth source.

### Claim Cluster 2: Property Taxes

| Claim | Consensus Sources | Truth Range | Outside Range = Flagged |
|---|---|---|---|
| "Texas property tax rate is X%" | Texas Comptroller (county-by-county) | Varies by county. Harris ~2.X%, Fort Bend ~2.X%. Must show county-specific. | Averaging across counties without distinction |
| "Homestead exemption saves $X/year" | Texas Comptroller + county CAD | School tax: $100K exemption × local school rate. County/city optional. | Claiming savings without showing the calculation |
| "Texas has no state income tax" | Texas Constitution | Absolute truth — consensus is universal | N/A — this claim is uncontested |

### Claim Cluster 3: Mortgage / Financing

| Claim | Consensus Sources | Truth Range | Outside Range = Flagged |
|---|---|---|---|
| "FHA requires 3.5% down payment" | HUD guidelines | 3.5% for 580+ credit score. 10% for 500-579. | Saying "3.5% for everyone" without the credit score caveat |
| "Conventional loans require X% down" | Fannie Mae + Freddie Mac | 3% (HomeReady/HomePossible) to 20% (no PMI) | Claiming a single number as universal |
| "Average interest rate in Texas is X%" | Freddie Mac PMMS | National rate ± 0.1-0.3% | Claiming a rate more than 0.5% different from PMMS without citing a specific lender survey |
| "Closing costs average X% in Texas" | Bankrate + ClosingCorp | 2-5% of purchase price | Claiming outside this band or a single number without the range |

### Claim Cluster 4: Buyer Programs

| Claim | Consensus Sources | Truth Range | Outside Range = Flagged |
|---|---|---|---|
| "TDHCA offers up to X% in down payment assistance" | TDHCA program guidelines | "My First Texas Home" — up to 5%. "My Choice Texas Home" — up to 5%. | Claiming a percentage not listed in current TDHCA materials |
| "USDA loans cover 100% in eligible areas" | USDA Rural Development | True for eligible areas. Eligibility map determines coverage. | Claiming "all of Katy" is eligible without checking the USDA map |
| "VA loans require $0 down" | VA guidelines | True. Funding fee varies by service type and down payment. | Saying "completely free" — the funding fee is a real cost |

---

## How to Use This

For EVERY spoke page that includes a factual claim:

1. **Identify which claim cluster** the page touches
2. **Pull the actual number** from the primary ground truth source (don't guess)
3. **State the source explicitly** in the content ("According to TREC..." / "HAR data shows...")
4. **Stay within the truth range** — if your number differs, attribute to a specific methodology
5. **For gray areas** (e.g., "what's the best school district?"), show multiple authoritative perspectives rather than asserting one

---

## What Happens If Content Falls Outside the Range

Per methodology: Google's algorithms flag claims that deviate from consensus. Consequences:
- **Reduced E-E-A-T signal** — content appears unreliable
- **Lower ranking** for YMYL-adjacent queries (real estate is financial YMYL)
- **Knowledge Panel won't populate** your claimed attributes
- **Competitors within the range outrank you** by default

---

## Integration With EAV Triples

Every numerical EAV triple must now include:
```
Entity → Attribute → Value → Source → Within Truth Range?
```

Example:
```
Katy TX → median home price → $X → HAR.com April 2026 report → ✅ Matches Redfin within 5%
Katy TX → average DOM → Y days → HAR.com → ✅ Within range
```

---

## Groundedness Validation Protocol

**Principle:** Algorithmic systems like Google's LaMDA and ranking evaluators prioritize **Groundedness** — accuracy of factual claims measured against authoritative consensus. A page that claims "Texas property taxes are 0.5%" when the consensus is ~1.8% will be flagged for low accuracy and lose Knowledge-Based Trust (KBT). Every claim on quann.homes must pass a groundedness check before publish.

### Hard Truth Ranges (With Specific Numbers)

These are the consensus values for Quan's niche. Claims must stay within the stated band — or cite a specific, verifiable source and methodology.

| Claim | Consensus Value | Acceptable Range | Source(s) | NEVER Claim |
|---|---|---|---|---|
| Texas average effective property tax rate | ~1.80% | 1.60% – 2.10% (varies by county) | Texas Comptroller, Tax Foundation | Below 1.0% or above 3.0% without specifying county |
| Harris County effective tax rate | ~2.13% | 1.90% – 2.40% | Harris County Appraisal District | "Texas taxes are low" — they're among the highest nationally |
| Fort Bend County effective tax rate | ~2.25% | 2.00% – 2.50% | Fort Bend CAD | Mixing Harris and Fort Bend rates |
| Katy median home price | TBD (pull from HAR) | HAR ± 5% from nearest Redfin value | HAR.com, Redfin Data Center | Round-number estimates ($400K) without source |
| FHA minimum down payment | 3.5% (580+ FICO) | Must specify credit score tier | HUD 4155.1 | "3.5% for everyone" — 500-579 bracket needs 10% |
| Conventional minimum down payment | 3% | 3% – 20% | Fannie Mae HomeReady, Freddie Mac Home Possible | "You need 20% down" — false for first-time buyers |
| Homestead exemption school tax savings | $100,000 × local ISD rate | Must calculate per district | Texas Comptroller, local CAD | Flat dollar amount without showing the math |
| Typical closing costs (TX) | 2% – 5% of purchase price | Must cite specific % from Bankrate or ClosingCorp | Bankrate, ClosingCorp | "Closing costs are always 3%" |
| Builder incentive typical value | $5,000 – $15,000 | Range: $2,000 – $25,000 | Quan's transaction history + builder programs | "Builders always give $20K" without qualifiers |
| MUD tax typical rate | $0.50 – $1.50 per $100 valuation | Varies by district maturity | Individual MUD district financials | "MUD taxes go away after 10 years" — some are perpetual |
| Days on Market (Katy) | TBD (pull from HAR) | HAR ± 10% from Redfin | HAR.com, Redfin | "Homes sell in 3 days" without specifying the segment |

### Pre-Publish Groundedness Checklist

For every page before it goes live:

- [ ] Every numerical claim has a cited source (not "research shows" — "According to HAR's Q1 2026 report...")
- [ ] Every claim falls within the truth range above OR cites a specific methodology explaining the deviation
- [ ] No round-number estimates presented as facts (never "$400K" when the number is $387,450)
- [ ] All % claims include the base (2% of *what*?)
- [ ] No superlatives without attribution ("Katy is the best suburb" → "Katy is ranked #3 Houston suburb by Niche.com (2025)")
- [ ] Quan-specific claims (incentive amounts, negotiation outcomes) framed as "typical results" with a specific real example, not as guarantees

### What Happens If Groundedness Fails

| Violation | Algorithmic Consequence |
|---|---|
| Claiming 0.5% tax rate when consensus is 1.8% | Low accuracy flag → KBT score drops → entire site's E-E-A-T reduced |
| Round-number price estimates without sources | Extracted triple gets low confidence → Knowledge Graph ignores it |
| Superlatives without attribution | Marketing language classifier → page de-ranked for informational queries |
| Out-of-range claim without citation | Trustworthiness signal drops → YMYL penalty on mortgage/financial pages |
| Repeated low-accuracy claims across multiple pages | Site-wide KBT collapse → all rankings decline, not just the inaccurate page |

### Integration with Content Briefs

Every content brief now includes a **Ground Truth Anchor** field:

```
Ground Truth Anchor:
- Primary fact: [specific claim with number]
- Source: [exact source name + date]
- Consensus verification: [does this match other authoritative sources? Y/N]
- Truth range check: [claim X is within the Z% consensus band]
```

