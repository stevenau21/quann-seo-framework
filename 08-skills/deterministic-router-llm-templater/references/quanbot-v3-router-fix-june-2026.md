# Session Notes: QuanBot v3 Router Fix — June 2026

## Problem
Browser test UI showed old behavior for "i dont have it" → generic fallback instead of `ASK_FOR_CODE`.

## Root Cause
`NO_CODE_RE` regex in `router.py` too narrow — `it` not in post-verb object list.

Pre-fix:
```python
r"(?:don't|do\s*not)\s*(?:have|know|got)\s*(?:one|any|the|a|code|number)s?"
```

**V2 — Nag Loop Fix (June 2026)**:
- Added `SOFT_REJECTION_RE` to catch "no", "nah", "nope", "i dont" without requiring `REJECTION_RE` severity
- Added `CONFUSION_RE` to catch "why", "huh", "what", "i don't understand" in `NEEDS_CODE` state
- Added `Action.NO_CODE_HELP` — offers form + phone escape hatch instead of looping `ASK_FOR_CODE`
- Tier 10 `QUALIFYING` fallback: `_is_soft_rejection(msg)` → `NO_CODE_HELP` before falling to `ASK_FOR_CODE`
- Tier 10 `NEEDS_CODE` fallback: `_is_confusion(msg) or _is_soft_rejection(msg)` → `NO_CODE_HELP`
  
```python
# New helpers
SOFT_REJECTION_RE = re.compile(
    r"\b(no[. !]*|nah[. !]*|nope[. !]*|i\s*don'?t.*?|pass[. !]*|" +
    r"not really[. !]*|never mind[. !]*)$",
    re.IGNORECASE,
)

CONFUSION_RE = re.compile(
    r"\b(huh[.!?]*|what[.!?]*|what\?+|which one\?|where[.!?]*|why[.!?]*|" +
    r"i\s*don'?t\s*understand|not\s*sure|confused|lost|wait[.!?]*|" +
    r"what (do you mean|is that|does that mean)|what property code)\b",
    re.IGNORECASE,
)

# In brain.py action handler:
elif action == Action.NO_CODE_HELP:
    reply = await generate_reply("no_code_help", message, form_url=FORM_URL)
    manual_state = "QUALIFYING"
```

Post-fix:
```python
r"(?:don'?t|do\s*not)\s*(?:have|know|got|remember|see|find)\s*(?:one|any|the|a|code|number|it|id|that|mine|them)?s?"
```

## Supporting Fixes
- `test-ui/index.html`: Added `randomId()` generating 12-char alphanumeric for page load / CLEAR / NEW SESSION so QA always gets a fresh `subscriber_id` and no stale SQLite session state
- `src/main.py`: `/test-chat` endpoint returns `Response(..., headers={"Cache-Control":"no-store, no-cache, must-revalidate, max-age=0","Pragma":"no-cache"})`
- `scripts/deploy.sh`: Deploy script with `find . -name "*.pyc" -delete`, `find . -type d -name __pycache__ -exec rm -rf {} +`, grep smoke test for `"Quan's assistant"`, health check, warm-up POST asserting `"assistant"` in response body

## Environment
- Service: `quanbot-v3` on port 8002 via systemd (`Restart=always`)
- Webhook: `POST /webhook/quanbot-v30`
- Domain: `v3-test.quann.homes/test-chat`
