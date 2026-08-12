# Phase 3 Deliverable: Information Retrieval & Indexing
> **Koray Framework:** SEO Information Retrieval (7 grounded rules)  
> **Allocation:** 86% ENGINE — 14% human (design constraint only)  
> **Artifacts:** PageRank distribution, Boolean term matrix, RankBrain query signals

---

## ENGINE OUTPUT

### 1. PageRank Simulation (17 planned pages)
The engine computed PageRank for the full site structure using Koray's iterative formula: PR(A) = (1-d)/N + d × Σ(PR(B)/L(B)). 100 iterations, damping factor 0.85.

| Rank | Page | PageRank | In-Links |
|---|---|---|---|
| 1 | **buying-hub** | 0.1059 | 8 |
| 2 | homepage | 0.0996 | 5 |
| 3 | katy-hub | 0.0842 | 5 |
| 4 | contact | 0.0818 | 5 |
| 5 | about | 0.0737 | 3 |
| 6 | katy-neighborhoods | 0.0707 | 5 |
| 7 | fthb-process | 0.0596 | 4 |
| 8 | fha-vs-conv | 0.0563 | 4 |
| 9 | pre-approval | 0.0474 | 3 |
| 10 | new-construction | 0.0473 | 3 |

### 2. PR Sink Warning
Two pages have high PageRank but dangerously low out-degree (traffic dead ends):

- **about page:** PR=0.0737, only 3 out-links → needs cross-spoke links to share authority
- **contact page:** PR=0.0818, only 2 out-links → add contextual links to hub pages

### 3. Boolean Term-Document Matrix
Key finding: zero pages matched "houston," "first-time buyer," "school," or "relocation" in their page slug structure. The term matrix is limited to filenames at this stage, but the gap is real — Houston appears nowhere in the planned URL structure despite being a primary SEO target.

### 4. RankBrain Query Signals
Five primary target queries identified:
- "homes for sale katy tx first time buyer"
- "houston relocation guide buyer agent"
- "katy isd schools new construction homes"
- "texas first time home buyer programs 2025"
- "builder incentives houston new construction"

**Entity salience rule:** Homepage must rank for "Quan Nguyen real estate Katy TX" before spoke pages can inherit authority. **Click satisfaction signal:** Every page must answer its primary query in the first 3 sentences (above the fold).

---

## HUMAN TASK (Single Item)

### Design Constraint: Multilingual Consistency
**[Koray Rule: "Ensure consistent design, topicality, and brand identity across all language versions."]**

quann.homes is English-primary. If a Vietnamese version is added later (Quan speaks Vietnamese natively), the engine will produce parallel page templates with hreflang mapping. No action now — deferred to post-launch.

---

## COPYWRITER GUIDANCE

The PageRank results confirm the publishing order: **buying-hub first, then katy-hub, then spokes in PR-descending order.** Each spoke page inherits authority from its pillar. The contact page needs more internal links to avoid becoming a dead end.

*Engine: Phase 3 complete. 7 grounded IR rules executed. PageRank simulated. Boolean matrix computed. RankBrain signals mapped. Stand by for Phase 4.*
