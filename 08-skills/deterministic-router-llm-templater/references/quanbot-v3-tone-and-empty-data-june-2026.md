# Session Notes: QuanBot v3 Tone + Empty Data Fix — June 2026

## What the User Complained About
- "this is just live v2!" — assumed wrong service was responding
- "the response its not humanistic or smart"
- "why are all the responses hard coded. this feels too robotic"
- "you continue to fail me with the responses sounding robotic and not human"
- "it was suppose to send the form or call urls" — wrong fallback for unknown codes
- "the call is when they want to imedietly get in contact" — clarification on flow

## Root Causes Found

### 1. Empty Google Sheet (the non-obvious one)
The Google Sheet at `10K53qX5dRVIv5Bbe67cvx5YYKJgbZ-NMqQXs06Z_ROQ` returned ONLY the header row. No data rows. Every `fetch_property(code)` returned `None`, every code lookup fell to the fallback.

**Verification:**
```python
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&range=A1:Z500"
resp = httpx.get(url, timeout=10)
rows = resp.text.strip().split("\n")
# len(rows) == 1  → sheet is empty (only header)
```

This is the **most important** finding — every "stupid bot" symptom was downstream of this. Without sheet data, the user can never see `show_property` / `show_similar` work end-to-end. Need real property data to test the full flow.

### 2. Wrong fallback for unknown codes
Pre-fix: `f"I couldn't find details for {code}. Text Quan at (832) 400-3152!"` — dead-end, no form offered.
Post-fix: Offers the form URL so Quan can manually match the lead.

### 3. URL detection treated as code-lookup request
`can you share the location of the house in the reel please? www.instagram.com/sad213ds` hit Tier 2 → `ASK_FOR_CODE` → bot lectured about QH codes even though user sent a link.

Fix: New Tier 1.5 in router that detects URL and routes to `SEND_FORM` (Instagram URLs need login to resolve, so we can't extract codes from them — but we can offer the form for human matching).

### 4. Templater prompts were too salesy
Old prompts included "I'd love to pull up the details for you!", "Happy to help", "I have everything ready for you instantly!", "😊", multiple exclamation points, marketing-speak. Replaced with casual 1-2 sentence prompts that cap output at 40 words with no exclamation points.

## What Was Changed

### `src/router.py`
- Added Tier 1.5: `if URL_RE.search(msg): return Action.SEND_FORM`
- Renamed Tier 2 from "URL or inquiry" to "inquiry without URL or code"
- Already had NO_CODE_HELP, SOFT_REJECTION_RE, CONFUSION_RE from previous session

### `src/brain.py`
- Replaced hardcoded phone fallback for unknown codes with form offer
- New fallback: `f"Hmm, I can't pull up {code} in our system. Could be a typo or it might not be listed on IG yet. Fill this out and Quan will send you matches directly: {FORM_URL}"`

### `src/templater.py`
All 12 templates rewritten to be casual. Key changes:
- "I'd love to..." → direct action ("Reply in 1-2 short sentences...")
- Removed "😊" emoji
- Cap word counts (Under 40, Under 30, Under 20)
- No exclamation points
- No marketing-speak ("VIP", "exclusive", "instantly!")
- Third person "I'm Quan's assistant" (not "I'm Quan")

## Verification
```bash
sudo systemctl restart quanbot-v3
python -m py_compile src/router.py src/brain.py src/templater.py  # all clean
curl -s http://localhost:8002/health  # healthy
```

Tested with user's exact messages via direct POST to `localhost:8002/webhook/quanbot-v30`:
- `hi` → "Hi, I'm Quan's assistant. Do you have a property code (like QH001) you're looking for?"
- `qh232` → "Hmm, I can't pull up QH232 in our system. Could be a typo or it might not be listed on IG yet. Fill this out and Quan will send you matches directly: [form]"
- `can you share the location of the house in the reel please? www.instagram.com/sad213ds` → "I can't pull up that specific link. Please fill out this form so Quan can match you with the right properties: [form]"

## Open Question for User
Sheet is empty — need real property data to test `show_property` and `show_similar` end-to-end. Awaiting direction:
- (A) User adds property data to the sheet
- (B) Build a fixture for testing
- (C) Wire up a different data source (FUB, Airtable)

## Environment
- Service: `quanbot-v3` on port 8002 via systemd
- Webhook: `POST /webhook/quanbot-v30`
- Test UI: `https://v3-test.quann.homes/test-chat`
- Production domain: `quanbot.quann.homes` (still on v2 — no cutover)
