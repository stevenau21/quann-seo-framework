# Articechute v2 Implementation Patterns (2026-06-19)

Reusable architecture patterns from the Articechute v2 framework build.
These are general techniques applicable to any deterministic-router chatbot,
not Articechute-specific implementation details.

## Pattern 1: code_ask_count — Strike-Based Escalation in the Router

**Problem:** The router needs to know how many times the bot has already asked
for a code to decide whether to ask again or escalate. But the router is
stateless — it receives a message and prior state, not a conversation history.

**Solution:** Pass `code_ask_count` as an explicit parameter to `decide()`:

```python
@dataclass
class RouterDecision:
    intent: Intent
    action: Action
    state_after: State
    needs_llm: bool = True
    confidence: float = 1.0
    rationale: str = ""
    code_ask_count: int = 0  # ← added

def decide(
    prior_state: State,
    message: str,
    code_ask_count: int = 0  # ← caller passes this
) -> RouterDecision:
    if intent == Intent.CANT_FIND_CODE:
        return RouterDecision(
            ...,
            code_ask_count=code_ask_count,  # pass through
        )
    if intent == Intent.ASK_FOR_CODE:
        new_count = code_ask_count + 1
        if new_count >= 3:
            action = Action.PUSH_TO_FORM  # escalate
        else:
            action = Action.ASK_FOR_CODE
        return RouterDecision(
            ...,
            code_ask_count=new_count,
        )
```

**Caller tracks the count** (runner.py, shadow_replay.py, server.py):
```python
code_ask_count = 0
for turn in conversation:
    decision = router.decide(state, turn.text, code_ask_count=code_ask_count)
    code_ask_count = decision.code_ask_count
    state = decision.state_after
```

**Key insight:** The count lives in the RouterDecision dataclass, not in
session state. This keeps the router stateless — the caller is responsible
for persisting the count between turns. All call sites must be updated
when the signature changes.

## Pattern 2: current_message — First-Reply Acknowledgment

**Problem:** The LLM writer needs to know the user's current message to
acknowledge it in the first reply. But the writer only receives the
RouterDecision and prior messages — not the raw current message.

**Solution:** Pass `current_message` through the call chain:

```python
# writer.py
def build_user_prompt(
    decision: RouterDecision,
    prior_messages: list[dict],
    current_message: str = ""  # ← added
) -> str:
    if not prior_messages:  # first reply
        prompt += (
            f"The user just said: '{current_message}'. "
            "Respond to what they actually said first — if they mentioned "
            "an area, acknowledge it; if they said hi, introduce yourself. "
            "THEN ask if they have a property code. Under 40 words."
        )
```

**Why this matters:** 59% of conversations are single-message. The first
reply IS the entire conversation. Leading with a code request causes
drop-off; acknowledging the user's actual message first demonstrates
understanding and keeps them engaged.

## Pattern 3: Live Google Sheets Property Store via gviz (No Auth)

**Problem:** The bot needs to look up property codes (QH###) against a
Google Sheet, but doesn't have Google OAuth credentials. The sheet is
public (view-only) and the gviz JSON endpoint requires no auth.

**Solution:** `property_store.py` — a cached gviz lookup:

```python
import httpx, time, re, json

SHEET_ID = "10K53qX5dRVIv5Bbe67cvx5YYKJgbZ-NMqQXs06Z_ROQ"
SHEET_NAME = "Sheet1"
CACHE_TTL = 300  # 5 minutes

_cache = {"data": None, "ts": 0}

def lookup_property(code: str) -> dict | None:
    now = time.time()
    if _cache["data"] is None or now - _cache["ts"] > CACHE_TTL:
        url = (
            f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            f"/gviz/tq?tqx=out:json&sheet={SHEET_NAME}"
        )
        resp = httpx.get(url, timeout=10)
        # gviz returns JS assignment, not pure JSON:
        # "/*O_o*/\ngoogle.visualization.Query.setResponse({...});"
        text = resp.text
        json_str = text[text.index("{"):text.rindex("}") + 1]
        data = json.loads(json_str)
        _cache["data"] = data
        _cache["ts"] = now
    # Search rows for matching code in column A
    rows = _cache["data"]["table"]["rows"]
    for row in rows:
        cells = row.get("c", [])
        if cells and cells[0] and cells[0].get("v", "").upper() == code.upper():
            return _parse_row(cells)
    return None
```

**Key details:**
- gviz returns `google.visualization.Query.setResponse({...})` — must
  extract the JSON between the first `{` and last `}`.
- 5-minute cache prevents rate-limiting on repeated lookups.
- Column A holds property codes (QH###). Map other columns by position.
- No auth needed — sheet must be "Anyone with link can view."
- Same approach used in production `src/integrations/sheets.py`.

## Pattern 4: Dual-Webhook FastAPI Server (ManyChat + Meta Forwarded)

**Problem:** The server needs to handle two completely different webhook
formats: ManyChat (subscriber + message) and Meta (entry + changes + field).
Both must return 200 immediately and process asynchronously.

**Solution:** Separate endpoints with format-specific parsing:

```python
@app.post("/webhook/articechute")
async def manychat_webhook(request: Request):
    # ManyChat format: {subscriber_id, message, ...}
    data = await request.json()
    reply = await process_message(data["subscriber_id"], data["message"])
    return {"response": reply}

@app.post("/ig-webhook")
async def meta_webhook(request: Request):
    # Meta format: {entry: [{id, changes: [{field, value: {...}}]}]}
    data = await request.json()
    # Return immediately (Meta requires <5s response)
    asyncio.create_task(trigger_sync(data))  # background
    return {"status": "EVENT_RECEIVED", "events": len(data.get("entry", []))}
```

**Key insight:** The `/ig-webhook` endpoint must return BEFORE processing.
Meta enforces a 5-second webhook response timeout — if you process
synchronously, Meta will retry, causing duplicate events. Use
`asyncio.create_task()` for any post-receipt work.

**Per-user state in SQLite:**
```python
def get_or_create_state(subscriber_id: str) -> dict:
    cur = db.execute(
        "SELECT * FROM articechute_state WHERE subscriber_id = ?",
        (subscriber_id,)
    )
    row = cur.fetchone()
    if row:
        return dict(row)
    db.execute(
        "INSERT INTO articechute_state (subscriber_id, state, code_ask_count) "
        "VALUES (?, ?, ?)",
        (subscriber_id, "NEW", 0)
    )
    return {"subscriber_id": subscriber_id, "state": "NEW", "code_ask_count": 0}
```

## Pattern 5: Short-Circuit Deterministic Actions Before LLM Call

**Problem:** Actions like `push_to_form` and `push_to_call` have fixed reply
text (a URL). Routing them through the LLM wastes 2-8 seconds and introduces
failure modes (empty reply, URL hallucination, rate-limit cutoff).

**Solution:** Check for deterministic actions BEFORE calling the LLM:

```python
SHORT_CIRCUIT = {
    "push_to_form": "Drop your details here and we'll get you started: {form_url}",
    "push_to_call": "Let's get you on a quick call — pick a time: {calendly_url}",
}

async def write(decision, prior_messages, model="gemma4:31b", current_message=""):
    if decision.action.value in SHORT_CIRCUIT:
        return SHORT_CIRCUIT[decision.action.value].format(
            form_url=FORM_URL, calendly_url=CALENDLY_URL
        )
    # Only creative actions reach the LLM
    prompt = build_user_prompt(decision, prior_messages, current_message)
    return await llm_call(prompt, model=model)
```

**Results (193-turn stress test):**
- 51.3% of turns short-circuited (no LLM call)
- push_to_form latency: 8102ms → 2ms
- LLM error rate dropped (fewer calls = fewer rate-limit hits)
- Voice score 0.854 (LLM turns that DO run get full attention)

**Caveat:** Short-circuit replies still pass through guards (banned phrases,
URL allowlist). Test them through the guard pipeline — the banned-phrase guard
caught "Quan will" in the form reply template, requiring rephrasing to
"we'll get you started."

## Pattern 6: Shadow Replay Against Real flow.db Conversations

**Problem:** Synthetic stress tests use mock conversations that match patterns
but not real conversation flow. A bot that handles isolated turns perfectly
can fail at turn 7 of a real conversation due to state drift, voice drift,
or compound inputs.

**Solution:** Replay REAL conversations from `flow.db` turn-by-turn:

```python
import sqlite3

def replay_conversations(db_path="data/flow.db", limit=67):
    db = sqlite3.connect(db_path)
    conversations = db.execute(
        "SELECT DISTINCT subscriber_id FROM turns "
        "WHERE direction = 'in' ORDER BY subscriber_id LIMIT ?",
        (limit,)
    ).fetchall()
    results = []
    for (sub_id,) in conversations:
        turns = db.execute(
            "SELECT text, direction FROM turns WHERE subscriber_id = ? "
            "ORDER BY turn_id",
            (sub_id,)
        ).fetchall()
        state = "NEW"
        code_ask_count = 0
        for text, direction in turns:
            if direction != "in":
                continue
            decision = router.decide(state, text, code_ask_count=code_ask_count)
            if decision.needs_llm:
                reply = await writer.write(decision, prior, current_message=text)
            else:
                reply = SHORT_CIRCUIT.get(decision.action.value, "").format(...)
            # Log: subscriber_id, turn_text, intent, action, reply, latency
            results.append({...})
            state = decision.state_after
            code_ask_count = decision.code_ask_count
    return results
```

**Key rules:**
- **Log-only, never send.** Shadow replay processes but doesn't send replies
  to real users.
- **Use the same flow.db** that production uses — real conversation data with
  full metadata.
- **Track state and code_ask_count across turns** within each conversation —
  this is how you catch state drift and escalation bugs.
- **Sample, don't exhaust.** 67 conversations (193 turns) is enough to catch
  patterns. Full 1,734 turns takes ~20 min and risks timeout.

## Pattern 7: Property Data Re-Attachment for Follow-Up Questions

**Problem:** User looks up QH001 on turn 1, then asks "what area is this in?" on
turn 2. The router is stateless — it doesn't have the property data from turn 1.
Without re-attachment, the bot says "Quan hasn't shared that yet" even though
it showed the data one turn ago. This is the #1 cause of "bot contradicts itself"
symptoms.

**Solution — session tracks `last_property_code`, router re-fetches:**

```python
# server.py — UserSession
@dataclass
class UserSession:
    subscriber_id: str
    state: str = "NEW"
    code_ask_count: int = 0
    last_property_code: str = None  # ← tracks last looked-up property

# In webhook handler, after decide():
if decision.property_code:
    session.last_property_code = decision.property_code

# Pass to router on next turn:
decision = router.decide(
    prior_state=session.state,
    message=msg,
    code_ask_count=session.code_ask_count,
    last_property_code=session.last_property_code  # ← re-attach
)
```

```python
# router.py — re-fetch property data for follow-up intents
FOLLOWUP_INTENTS = {
    Intent.LOCATION_QUESTION, Intent.PRICE_QUESTION,
    Intent.MORTGAGE, Intent.SCHOOL_ZONE, Intent.COMPARE, Intent.WHAT_ABOUT
}

if intent in FOLLOWUP_INTENTS and last_property_code:
    prop = property_store.lookup_property(last_property_code)
    if prop:
        decision.property_data = prop
        decision.property_code = last_property_code
        decision.action = Action.REPLY_VOICE  # answer from data, don't push to form
```

```python
# writer.py — SYSTEM_PROMPT must include:
# "When PROPERTY DATA is provided, answer USING the data.
#  Do NOT say 'I can't share that' when the answer is in the dict."
# _llm_fallback reads directly from decision.property_data:
def _llm_fallback(decision):
    prop = decision.property_data
    if not prop: return None
    if decision.intent == Intent.PRICE_QUESTION:
        return f"This one starts at ${prop['price']:,.0f}."
    if decision.intent == Intent.LOCATION_QUESTION:
        return f"It's in {prop['area']}. Want to see more like this?"
```

**Test:** After implementing, send 5 turns: "QH001" → "is it still available?" →
"what area?" → "how much?" → "show me more like this". All 4 follow-ups must
answer from re-attached property data, not push to form.

## Pattern 8: `fetch_similar()` — 3-Pass Property Matching

**Problem:** "Show me more like this" needs similar-property search. Naive approach
fetches all and filters poorly. Ported from production `src/integrations/sheets.py`.

```python
def fetch_similar(code: str, all_properties: list[dict]) -> list[dict]:
    target = lookup_property(code)
    if not target: return []
    
    # Pass 1: same area + same beds + tight price (±$50k)
    matches = [p for p in all_properties
               if p['code'] != code
               and p.get('area') == target.get('area')
               and p.get('beds') == target.get('beds')
               and abs(_price(p) - _price(target)) <= 50000]
    if len(matches) >= 3: return _dedupe_siblings(matches, code)
    
    # Pass 2: same area + same beds + loose price (±$100k)
    matches = [p for p in all_properties
               if p['code'] != code
               and p.get('area') == target.get('area')
               and p.get('beds') == target.get('beds')
               and abs(_price(p) - _price(target)) <= 100000]
    if len(matches) >= 3: return _dedupe_siblings(matches, code)
    
    # Pass 3: same area only
    matches = [p for p in all_properties
               if p['code'] != code
               and p.get('area') == target.get('area')]
    return _dedupe_siblings(matches, code)
```

**Key:** Dedupes sibling codes (same property on different reels = different QH code).
3-pass narrowing ensures 3+ results without being irrelevant. Keep in sync with PROD's
`sheets.py`.

## Pattern 9: CANT_FIND_CODE — Conversational First, Form Push After 2 Asks

**Problem:** Original router pushed to form immediately when user said "I don't have
the code." This is too aggressive — the user might just need help finding it.

**Solution — first ask helps, second ask pushes form:**

```python
if intent == Intent.CANT_FIND_CODE:
    if code_ask_count >= 2:
        return RouterDecision(action=Action.PUSH_TO_FORM, ...)
    else:
        return RouterDecision(
            action=Action.REPLY_VOICE,
            needs_llm=True,
            # Prompt: "Help the user find the code — check the reel caption
            # for QH followed by numbers. Be conversational, not pushy."
        )
```

**Result:** First-time code confusion gets a helpful nudge ("check the caption for
QH followed by numbers"). Only after 2 failed attempts does the bot push to form.
This reduced form-push rate from 100% on CANT_FIND_CODE to ~40% (2nd ask only).

## Pattern 10: Multi-Code Back-Referencing (Known Gap)

**Current state:** `last_property_code` (single string) handles ~90% of follow-up
questions about the most-recently-viewed property.

**Gap:** User browses QH001 → QH017 → asks "how much was the first one?" — the
bot only has QH017's data. Full fix: store `{code: property_data}` dict in session
instead of single code. Not yet implemented as of 2026-06-19.

```python
# Future fix:
viewed_properties: dict[str, dict] = field(default_factory=dict)
# Router can look up any previously-viewed property by code
```

## File Layout (Articechute v2)

```
sandbox/articechute/
├── framework/
│   ├── router.py          # 17 intents, 3-strike escalation, INFO_QUESTION,
│   │                      # CANT_FIND_CODE conversational-first, last_property_code param
│   ├── writer.py          # LLM writer + short-circuit + current_message
│   │                      # + "answer from property_data dict" prompt + _llm_fallback
│   ├── guards.py          # URL allowlist, banned phrases, price fabrication
│   ├── property_store.py  # gviz Google Sheets lookup, 5-min cache, fetch_similar()
│   ├── runner.py          # code_ask_count tracking, state advancement
│   ├── shadow_replay.py   # flow.db replay harness
│   └── shadow_mode.py     # LIVE/SHADOW toggle, _count_prior_code_asks()
├── server.py              # FastAPI: /webhook/articechute + /ig-webhook,
│                          # UserSession with last_property_code tracking
└── run_stress_test.py     # Standalone stress test runner
```

Additional test scripts (in `sandbox/`):
- `stress_test_vs.py` — side-by-side PROD vs SBX (15 scenarios)
- `stress_test_real.py` — 12-scenario real-pattern test from conversation_log.jsonl
- `stress_test_vs_results.json` — results from side-by-side run
- `stress_test_real_results.json` — results from real-pattern run