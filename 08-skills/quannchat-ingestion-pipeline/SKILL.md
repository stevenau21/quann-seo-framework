---
name: quannchat-ingestion-pipeline
description: >
  Architecture and scripts for ingesting @quan.realtor Instagram reel captions
  into the Google Sheet that powers QuannChat property lookup. Covers Facebook Graph
  API polling, LLM extraction, Google Sheets append, and QuannChat FastAPI integration.
  Load when working on the Instagram→Sheets pipeline or QuannChat property lookup.
version: 1.0.0
deprecated: true
superseded_by: instagram-ingestion-pipeline
---

> **⚠ SUPERSEDED — DO NOT USE FOR NEW WORK.** This skill documents the
> **original** Graph-API-based ingestion pipeline. The canonical pipeline
> is now `instagram-ingestion-pipeline` (uses Brandformance meta-webhook API,
> not Facebook Graph API). This skill is kept for historical context only.
> Key differences from the current pipeline:
> - **Data source:** This says FB Graph API. The live pipeline uses
>   `https://meta-webhook.brandformance.app/raw/posts` (no auth, no app review).
> - **Bot version:** This references QuanBot v2/v20. The live bot is v4 on
>   port 8004 (`quanbot-v4.service`, `https://quanbot.quann.homes/`).
> - **Dedup key:** This says Code. The live pipeline deduplicates by IG
>   permalink (col J), not Code (col A).
> - **Extraction prompt:** This skill has no hashtag-stripping, no garage
>   default, no empty-row validation. All of these are in the current
>   pipeline.
> - **Webhook:** This skill predates the real-time webhook forward chain
>   (Meta → ig-data-pull → QuanBot `/ig-webhook` → Sheets).
> - **The `instagram_to_sheets.py` file referenced below is the LEGACY
>   Graph-API script** — it is NOT wired to cron and does NOT have valid FB
>   credentials. The canonical script is `meta_webhook_to_sheets.py`.
>
> Load `instagram-ingestion-pipeline` instead for all current work.

# QuannChat Ingestion Pipeline

## Architecture (CORRECTED — do NOT revert to YouTube)

```
Quan posts reel on @quan.realtor (Instagram Business account)
       │
       ▼
Cron (15min) → Facebook Graph API /{ig_user_id}/media
       │  Fields: id, caption, permalink, timestamp, media_type
       │  Filters: media_type == "VIDEO" (reels)
       ▼
instagram_to_sheets.py — LLM parses caption → structured listing
       │  Model: gemma4:31b-cloud via Ollama
       │  Schema: read from sheet headers at runtime (evolvable)
       ▼
Google Sheet "Quann Homes JSON Video Data Base"
  ID: 10K53qX5dRVIv5Bbe67cvx5YYKJgbZ-NMqQXs06Z_ROQ
  Tab: Sheet1
  Headers: Code, Area/City, Location, Starting From, Beds, Baths, Square Footage, Source URL
       │
       ▼
QuannChat FastAPI (/home/steve/quanbot/) — /webhook/quanbot-v20
  User pastes reel link in Instagram DM
  → ManyChat (External Request) → FastAPI webhook
  → lookup.py reads sheet → ManyChat sendContent → reply
```

## Key Files

| File | Purpose |
|---|---|
| `/home/steve/lightrag-apps/instagram-to-sheets/instagram_to_sheets.py` | Main pipeline: FB Graph API poll → LLM extract → Sheets append |
| `/home/steve/lightrag-apps/instagram-to-sheets/lookup.py` | Property lookup by reel URL or code (reads sheet) |
| `/home/steve/quanbot/src/brain.py` | QuannChat brain — routes DMs, calls lookup, sends replies |
| `~/.hermes/google_token.json` | Google OAuth token (spreadsheets scope) |
| `/.hermes/skills/productivity/google-workspace/scripts/google_api.py` | Google Workspace CLI wrapper |

## Why NOT YouTube

- Quan does NOT have a YouTube channel. The source is Instagram reels.
- YouTube OAuth, yt-dlp, and the YouTube reminder email were all wrong. Nuked.
- The `youtube-sheets-ingest/` directory is deprecated; use `instagram-to-sheets/`.

## Why NOT n8n

- QuannChat is a standalone FastAPI app (`/home/steve/quanbot/`), migrated out of n8n in April 2026.
- n8n is NOT in the DM response path. ManyChat → FastAPI directly.
- The ingestion pipeline also runs as a standalone Python cron, not an n8n workflow.

## Why NOT ManyChat for Detection

- ManyChat API has ZERO endpoints for detecting new posts/reels. It's purely messaging + subscriber management.
- Confirmed via Swagger inspection (`https://api.manychat.com/swagger/compileJson?type=Page_API`) — no growth tool webhooks, no post triggers.
- Facebook Graph API must be used for reel detection.

## Setup Requirements (for Facebook Graph API)

1. **Facebook App** at developers.facebook.com (Business type)
2. **Page Access Token** with `pages_show_list`, `pages_read_engagement`, `instagram_basic`
3. **Instagram Business Account** linked to Facebook Page (already confirmed)
4. **Long-lived token** (60-day, auto-refreshed)
5. **Google Sheets token** at `~/.hermes/google_token.json` (already exists, spreadsheets scope)

Run `python instagram_to_sheets.py --setup` for guided validation.

## LLM Extraction Details

- Model: `gemma4:31b-cloud` via Ollama (http://192.168.4.148:11434)
- Temperature: 0.0 (deterministic)
- Schema-driven: reads column headers from sheet at runtime — add a column to the sheet, LLM automatically extracts that field
- Deduplication: by Code column (case-insensitive)
- Caption format examples handled: "4 Bedrooms", "2.5+ Baths", "2,800+ sq ft", "near Houston", "QH282", "$600,000", emoji-bulleted natural language

## QuannChat Integration

- Instagram DM → ManyChat External Request → `https://quanbot.quann.homes/webhook/quanbot-v20`
- QuannChat reads the same Google Sheet for property lookup
- `lookup.py` provides standalone lookup by URL or code

## Pitfalls

- **Never assume YouTube.** The source is Instagram. The word "reel" ≠ YouTube Shorts.
- **Facebook token expires in 60 days.** Monitor and refresh.
- **Rate limits:** 200 calls/hr per app. Polling every 15 min = 4 calls/hr, well within limits.
- **IG Business Account ID ≠ IG User ID** — must resolve via `/me?fields=instagram_business_account`.
- **ManyChat is messaging only** — not a content monitoring platform. Don't try to make it one.
- **🚨 THIS sheet is shared with QuanBot v4 as its property database.**
  Every row in this sheet is a property (`QH###` code in column A) that
  the v4 bot reads via gviz with
  `SELECT B,C,D,E,F,G,H,I WHERE A = "QH###"`. Any other pipeline
  writing to this same SHEET_ID clobbers the bot's property lookup.
  See `instagram-ingestion-pipeline` for the 2026-06-10 collision
  incident — that script now has a hard guard refusing to write here.
  Keep that guard intact.
