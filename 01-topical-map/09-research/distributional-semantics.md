# Distributional Semantics — Site-Wide N-Grams & Boilerplate Optimization

**Date:** 2026-05-05
**Purpose:** Define the site-wide phrase taxonomy so quann.homes is classified as a "Vertical Knowledge Site" — not a generalist blog.

---

## Core Principle

A search engine builds a **site-level language model** from the statistical distribution of n-grams across all crawlable content — including headers, footers, and navigation. A tightly clustered n-gram profile signals "vertical authority." A flat, scattered distribution signals "generalist blog."

**Goal:** Quann.homes must generate a composite score that says: "This is a Texas buyer education site operated by a licensed real estate professional."

---

## Target N-Gram Clusters

These n-grams must appear with high frequency across the entire domain — in content pages AND boilerplate:

### Tier 1 — Entity Anchors (Appear on Every Page)

| N-Gram | Appears In |
|---|---|
| "Quan Nguyen" | Header, footer, every page |
| "License #0774451" | Footer, About page |
| "REAL BROKERAGE" | Footer, About page |
| "The Quantum Team" | Header, footer |
| "Texas home buyer" | Footer tagline, area pages |
| "Katy TX" / "Houston TX" | Footer location block, area pages |

### Tier 2 — Topic Clusters (Appear in Navigation & Sidebar)

| Cluster | Key N-Grams |
|---|---|
| First-time home buyer | "first-time home buyer," "FTHB," "down payment," "mortgage pre-approval," "closing costs" |
| Katy area | "Katy neighborhoods," "Katy ISD," "Katy real estate," "Katy homes for sale" |
| Out-of-state relocation | "relocating to Texas," "out-of-state buyer," "Texas relocation guide" |
| Builder incentives | "builder incentive," "get paid to buy," "new construction," "closing cost credit" |

### Tier 3 — Expert Vocabulary (Appear in Content Body)

| Cluster | Key N-Grams |
|---|---|
| Financial | "MUD tax," "PID," "homestead exemption," "property tax rate," "loan limit" |
| Process | "option period," "earnest money," "third-party financing addendum," "TREC" |
| Market | "median price," "days on market," "price per square foot," "inventory" |

---

## Boilerplate Optimization Plan

### Header (Every Page)

```
LOGO: Quann Home | The Quantum Team

NAV: Buying a Home | Katy Area Guide | Relocating to Texas | About | Blog | Schedule a Call
```

**N-Grams planted:** "Buying a Home," "Katy Area Guide," "Relocating to Texas," "Schedule a Call"

### Footer (Every Page)

```
QUAN NGUYEN — The Quantum Team at REAL BROKERAGE
Texas License #0774451
Serving home buyers in: Katy · Houston · Austin · Dallas · Rio Grande Valley
📞 (832) 400-3152 | ✉️ quan@thequantumteam.net

[Schedule a Buyer Consultation]
```

**N-Grams planted:** "Quan Nguyen," "The Quantum Team," "REAL BROKERAGE," "License #0774451," "Serving home buyers," "Katy," "Houston," "Austin," "Dallas," "Rio Grande Valley," "Schedule a Buyer Consultation"

### Sidebar / In-Page CTAs (Blog Pages)

```
Buying your first home in Katy?
→ [First-Time Home Buyer Guide]
Building new? Get builder incentives.
→ [How to Get Paid to Buy]
Relocating from out of state?
→ [Texas Relocation Guide]
```

**N-Grams planted:** "First-Time Home Buyer," "Katy," "Builder incentives," "Relocating," "Texas"

---

## Internal Link Anchor Text Rules

Anchor text is the highest-signal n-gram placement. Rules:

1. **Brand anchors:** "Quan Nguyen" — links to Home or About
2. **Pillar anchors:** "Texas Home Buying Guide" — links to pillar hub
3. **Spoke anchors:** Exact match only — "Katy ISD School Guide" links to that spoke page
4. **CTA anchors:** "Schedule a Buyer Consultation" — identical text on every CTA link
5. **NEVER use generic anchors:** "click here," "learn more," "read this"

---

## Composite Score Targets

| Signal | Current State | Target |
|---|---|---|
| Entity n-gram frequency (Quan Nguyen) | 1-2 per page | 3+ per page |
| Location n-gram frequency (Katy) | Low | 5+ per page on area pages |
| Topic cluster density (FTHB) | Blog posts only | Nav + footer + sidebar |
| License/credentials n-grams | Footer only | Footer + About + schema |

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|---|---|
| Vary boilerplate per page | Identical footer on all pages |
| "Click here for the guide" | "Texas First-Time Home Buyer Guide" |
| No entity in footer | Entity name + license in every footer |
| Generic nav labels ("Services") | Specific nav labels ("Buying a Home in Katy") |
