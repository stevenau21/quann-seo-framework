# Central Entity — Quann.Homes

**Date:** 2026-05-04 | **Revised:** 2026-05-05 (Quan interview — EAV values confirmed)
**Status:** ✅ Complete — All entity attributes populated

> **Related:** [Proactive Entitization Strategy](../09-research/proactive-entitization-strategy.md) — how this entity gets created in the Knowledge Graph. [Distributional Semantics](../09-research/distributional-semantics.md) — how this entity appears site-wide. [Entity Disambiguation Plan](../03-web-entity/entity-disambiguation-plan.md) — preventing entity collision.

## Central Entity Definition

### Core Identity

| Attribute | Value |
|---|---|
| **Entity Type** | Person (RealEstateAgent) |
| **Full Name** | Quan Nguyen |
| **License** | #0774451 (Texas, Active) |
| **Brokerage** | Walzel Properties |
| **Brand Names** | Quann Home / The Quantum Team |
| **Team** | The Quantum Team |
| **Role** | REALTOR® — Buyer Representation Specialist |

### Experience & Credentials

| Attribute | Value |
|---|---|
| **Years of Experience** | 5 years |
| **Languages** | English (native), Vietnamese (native) |
| **AI Translation** | Custom AI-powered translation layer — enables seamless communication with buyers in any language. Non-English speakers interact with Quan through real-time AI translation, removing the language barrier for Texas home buyers worldwide. |
| **Education** | Texas Real Estate Commission (TREC) licensed. Continuing education maintained per TREC requirements. |

### Certifications & Designations

| Certification | Full Name | Relevance |
|---|---|---|
| **ABR** | Accredited Buyer's Representative | Core designation for buyer representation — advanced training in buyer advocacy, negotiation, and fiduciary duty |
| **GRI** | Graduate, REALTOR® Institute | Advanced professional designation — 90+ hours of training across contracts, finance, marketing, and ethics |
| **C2EX** | Commitment to Excellence | NAR endorsement — verified excellence in 10 competency areas including client service, professionalism, and market knowledge |
| **MRP** | Military Relocation Professional | Specialized certification for working with relocating military families and veterans — aligns with out-of-state relocation focus |
| **PSA** | Pricing Strategy Advisor | Advanced training in comparative market analysis, property valuation, and pricing strategy |

### Professional Affiliations

| Organization | Membership | Notes |
|---|---|---|
| **NAR** | ✅ Member | National Association of REALTORS® |
| **TAR** | ✅ Member | Texas Association of REALTORS® |
| **HAR** | ✅ Member | Houston Association of REALTORS® — required for Houston metro practice |
| **Katy Chamber of Commerce** | ✅ Member | Local business community membership |
| **AREAA** | ✅ Member | Asian Real Estate Association of America — serves Vietnamese-American community and pan-Asian buyers |

### Service Geography

| Attribute | Value |
|---|---|
| **Primary Office Location** | Katy, TX (address on TREC license) |
| **Primary Service Area** | Katy, TX — ZIP codes: 77494, 77450, 77449, 77493 |
| **Extended Service Area** | Greater Houston metro, Austin metro, Dallas-Fort Worth metro, Rio Grande Valley |
| **NAP Anchor** | Quan Nguyen, Walzel Properties, Katy, TX 77494 |

### Track Record

| Attribute | Value |
|---|---|
| **Transaction Volume (Career)** | 75+ closed transactions |
| **Transaction Volume (Last 12 Months)** | 20+ closed transactions |
| **Buyer vs Seller Split** | 85% buyers / 15% sellers (buyer-focused practice) |
| **Average Buyer Outcome** | $8,500 in negotiated builder incentives and closing cost credits per transaction |
| **Awards** | Walzel Properties Top Producer (2024, 2025). HAR Rising Star recognition. |

### Client Profile (Priority Order)

| Rank | Buyer Type | % of Business |
|---|---|---|
| 1 | First-Time Home Buyers | 40% |
| 2 | Out-of-State Relocators | 25% |
| 3 | New Construction Buyers | 20% |
| 4 | Move-Up / Luxury Buyers | 10% |
| 5 | Investors | 5% |

### Service Confirmation

| Service | Active? | Content Priority |
|---|---|---|
| **Buyer Representation** | ✅ Core business | BUILD ALL 12 SPOKES |
| **Seller Listings** | ⚠️ Occasional (15%) | Defer — Build only if Quan explicitly requests later |
| **Investment Consulting** | ⚠️ Occasional (5%) | Defer — Reference as secondary service, no dedicated spokes |

### Unique Differentiators

| Differentiator | Description |
|---|---|
| **AI Language Bridge** | Proprietary AI translation layer — any buyer in any language can communicate with Quan. Vietnamese, Spanish, Mandarin, Arabic, Hindi — no language barrier. This is Quan's most defensible competitive moat. |
| **Get Paid to Buy** | Quan's signature approach: stack builder incentives, lender credits, and closing cost buy-downs into a single negotiation. Average buyer outcome: $8,500 in captured value. |
| **Cross-Texas Coverage** | Licensed across Texas with boots-on-ground knowledge of Katy, Houston, Austin, Dallas, and the Rio Grande Valley — not just a referral agent but direct service across metros. |
| **The Quantum Team System** | A documented, repeatable process for every buyer type: pre-approval prep → neighborhood matching → offer strategy → negotiation → closing. Every client gets the same system, proven across 75+ transactions. |

### Contact

| Attribute | Value |
|---|---|
| **Phone** | (832) 400-3152 |
| **Email** | quan@thequantumteam.net |
| **Website** | quann.homes |
| **Social (Confirmed)** | [Verify all during web entity audit] |

## What We DON'T Cover (Per Quan Confirmation)

- **No dedicated seller content.** Quan's practice is 85% buyer-focused. Seller spokes are cut.
- **No dedicated investor content.** 5% of business — referenced only as secondary service, no spokes.
- **No generic Texas lifestyle content.** Stay within Katy/Houston focus + destination city overviews for relocators.

## Site-Wide Implementation (per SEO RAG methodology)

1. **JSON-LD** on homepage: `@type: RealEstateAgent` with license, brokerage, areas, contact point, credentials, languages
2. **H1**: "Quan Nguyen — Texas REALTOR® | The Quantum Team at Walzel Properties"
3. **Header/Logo alt text**: "Quan Nguyen — Quann Home"
4. **Footer boilerplate**: "Quan Nguyen, REALTOR® — License #0774451, Walzel Properties. Serving Katy, Houston, Austin, Dallas, and the Rio Grande Valley. English · Tiếng Việt · AI-Powered Multilingual Support."
5. **All pages** must reference the central entity — either directly (about, contact) or via author/about schema properties
