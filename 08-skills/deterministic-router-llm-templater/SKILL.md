---
name: deterministic-router-llm-templater
description: Architecture pattern for chatbots that need deterministic behavior with human-like tone. Splits WHAT to do (Python state machine router, 0ms) from HOW to say it (thin LLM template filler, ~50-word prompts). Use when LLM-based chatbots keep falling into "how can I help" fallback loops, miss keyword triggers, or need guaranteed routing with natural language.
tags: [chatbot, llm, router, state-machine, fastapi]
---

# Deterministic Router + LLM Templater Architecture

## When to Use This Pattern

- Your LLM chatbot keeps ignoring system prompts and defaulting to "let me know how I can help"
- You need guaranteed routing (e.g., property codes, intent detection) where LLM hallucination is unacceptable
- You want deterministic, testable behavior but still need natural-sounding replies
- The LLM is too chatty or overstepping its role (trying to close deals instead of just routing)

## Architecture

```
User Message → Python Router (deterministic, 0ms) → LLM Templater (thin, ~50 words)
                    ↓                                       ↓
              WHAT to do                              HOW to say it
              (action enum)                           (personalized text)
```

**Key insight:** The LLM should NEVER decide WHAT action to take. It should only decide HOW to phrase the chosen action. This eliminates the entire class of "LLM went off-script" failures.

## File Structure

```
project/
├── src/
│   ├── router.py      # State machine — decides action
│   ├── templater.py   # LLM prompt templates — personalizes text
│   ├── session.py     # SessionState dataclass
│   └── main.py        # FastAPI app
```

## Router (State Machine)

```python
from enum import Enum

class Action(Enum):
    INTRO_QUALIFY = "intro_qualify"
    ASK_FOR_CODE = "ask_for_code"
    NO_CODE_HELP = "no_code_help"
    SEND_FORM = "send_form"
    SEND_CALENDLY = "send_calendly"
    SHOW_PROPERTY = "show_property"
    CLARIFY = "clarify"
    DONE = "done"

class State(Enum):
    NEW = "new"
    QUALIFYING = "qualifying"
    NEEDS_CODE = "needs_code"
    PROPERTY_SHOWN = "property_shown"
    SIMILAR_SHOWN = "similar_shown"
    UNLISTED_OFFERED = "unlisted_offered"
    FORM_SENT = "form_sent"
    CALL_OFFERED = "call_offered"
    DONE = "done"

def decide_action(message: str, state: State) -> Action:
    # Priority 1: Property code detection (regex)
    if re.search(r'\b[A-Z]{2}\d{3,4}\b', message):
        return Action.SHOW_PROPERTY

    # Priority 2: Schedule/call intent (regex)
    if re.search(r'(schedule|call|speak|talk|appointment|meet)', message, re.I):
        return Action.SEND_CALENDLY

    # Priority 3: State machine flow
    if state == State.NEW:
        return Action.INTRO_QUALIFY
    elif state == State.QUALIFYING:
        return Action.SEND_FORM
    elif state == State.FORM_SENT:
        return Action.SEND_CALENDLY
    # ...
```

### Router Design Rules

1. **Regex first, LLM never.** Hard keyword/pattern matches take priority. Property codes, intent keywords, URLs — all regex.
2. **Broad → Narrow — each tier MUST narrow the decision space.** Think of routing tiers the same way a topical map or geographic query narrows: country → city → neighborhood → street address. If a tier catches MORE than the tier below it, that tier is too broad and will starve lower tiers.
   - **Analogy (Koray SEO):** Germany (broadest) → Munich → Schwabing → "apartments for rent in Schwabing" (narrowest). Each step filters the remaining search space.
   - **Analogy (QuanBot):** Hard block (broadest, all NSFW) → Property code (specific structured data) → Rejection (intentional exit) → Acknowledgment (very specific trivial patterns) → Greeting (exact-match only) → Everything else → LLM.
   - **Anti-pattern:** Tier 3 being `/(buy|sell|house|home|property|rent|apartment)/i`. That's too broad — it would catch legitimate leads that the LLM should handle. Tier 3 should ONLY catch trivial/ambiguous responses (`ok`, `thanks`, `cool`, `lol`) — the "Schwabing"-level specificity.
3. **Priority order is critical.** Order matters — each tier gates the next:
   - **Tier 0: Property code** — always wins, even mid-conversation. Code → show card.
   - **Tier 1: Phone number** — must come BEFORE schedule intent. "Call me at 555-1234" is someone giving their number, NOT asking for Calendly.
   - **Tier 2: Schedule intent** — "let's schedule a call" → send Calendly. Skip if already CALL_BOOKED or DONE.
   - **Tier 3: Clear rejection** — "no thanks", "not interested", "leave me alone" → acknowledge and go to DONE. Never follow up after rejection.
   - **Tier 4: Acknowledgments** — "ok", "thanks", "booked!", "all set" → acknowledge, stay in current state. Don't push anything new.
   - **Tier 5: State machine** — fallback routing by conversation state.
4. **State machine is the fallback.** After regex checks, flow through states linearly: NEW→QUALIFYING→FORM_SENT→CALL_OFFERED→DONE.
5. **No LLM in the router.** The router is pure Python. Zero LLM calls. Testable with unit tests.
6. **Always advance state.** Every action moves the state forward. No loops back to "how can I help."

### How to Evaluate a New Tier or Regex Expansion

Before adding a new regex or re-ordering tiers, ask:
- Does this catch **MORE** or **LESS** than the tier below it?
- If MORE → the tier is too broad. Narrow the regex or move it down.
- If LESS → it's correctly positioned. It should only catch a strict subset of what the tier above misses.

### Pitfall: Database Column Mapping After ALTER TABLE (Index Misalignment)

**Root cause:** You add session fields to the `SessionState` dataclass and run an `ALTER TABLE` to add columns. SQLite appends new columns at the END of the table. Code that used `SELECT *` with ordinal indexing (`row[3]`, `row[7]`) now reads the wrong values — boolean flags from offsets that now point to different columns.

**Concrete example from this session:**
```python
# BEFORE — broken after ALTER TABLE:
cur = db.execute("SELECT * FROM sessions WHERE subscriber_id = ?", (sid,))
row = cur.fetchone()
return SessionState(
    subscriber_id=row[0],
    state=row[1],
    property_code=row[2],
    form_sent=row[3],   # ← WAS form_sent, but after ALTER it became schedule_offered!
    ...
)
```

After `ALTER TABLE ADD COLUMN unlisted_offered DEFAULT 0`, the new column is appended AFTER the existing columns. `row[3]` is no longer `form_sent`.

**Fix — explicit column names everywhere:**
```python
# AFTER — migration-safe:
cur = db.execute(
    """SELECT subscriber_id, state, property_code, form_sent, link_sent,
              call_booked, schedule_offered, created_at, updated_at,
              lead, similar_shown, unlisted_offered
       FROM sessions WHERE subscriber_id = ?""", (sid,)
)
row = cur.fetchone()
# Now row[3] is ALWAYS form_sent, regardless of ALTER TABLE history

# Similarly for INSERT/UPDATE:
db.execute("""
    INSERT INTO sessions
       (subscriber_id, state, property_code, form_sent, link_sent, ...)
    VALUES (?, ?, ?, ?, ?, ...)
    ON CONFLICT(subscriber_id) DO UPDATE SET ...
""")
```

**Alternative fix:** Use `row["column_name"]` with `sqlite3.Row`.

**Rule:** Never use `SELECT *` + ordinal indexing on tables that might be ALTERed. Explicit column lists or named row factories only.

### Pitfall: `next_state()` Overwriting Explicit Handler State

**Root cause:** The `decide_action` logic chooses WHAT to do. A separate `next_state()` convenience method chooses the NEXT session state. If both run unconditionally — especially if `next_state()` is called AFTER the handler already set state explicitly — the handler's carefully computed state gets overwritten.

**Example from brain.py:**
```python
# BEFORE — buggy:
action = router.decide(msg, session.state)
reply = await handler_for(action)(msg, session)
session.state = next_state(session.state)  # ← BUG: handler set SIMILAR_SHOWN,
                                            #     but next_state saw QUALIFYING → FORM_SENT
```

**Fix — `manual_state` override pattern:**
```python
# AFTER — fixed:
manual_state = None  # action handlers CAN override this

if action == Action.SHOW_PROPERTY:
    # ... show property logic ...
    manual_state = "SIMILAR_SHOWN"  # first code → similar shown
    session.similar_shown = True
# ... other handlers also assign manual_state ...

# AFTER all handlers:
if manual_state:
    session.state = manual_state
else:
    session.state = next_state(session.state)  # fallback only when no override
```

**Rule:** Always give action handlers a `manual_state` escape hatch. The handler knows the correct next state better than any generic `next_state()` helper.


**Scenario:** The user corrects you: *"property code is the narrowest, not the broadest."*

This signals a tier ordering error. Before fixing, ask yourself: does the earlier tier catch **more messages** than the later tier? If yes, the earlier tier is too broad and will starve all tiers below it.

**Real example from this codebase:**
- Original tier order: URL in message → generic response → ACK → Property code
- Problem: A post with a code URL in the caption would hit "URL detected" first and send a generic "go back to get the code" — the user expected the router to extract the code FROM the message and show the property card immediately.
- Fix tested but not merged: Move property code extraction to Tier 0 (before URL check) with regex parsing the caption from the nested body. The URL check stays at Tier 1 as a safety valve when no code is present.

**Rule:** When a user says a router tier feels wrong, draw the decision tree. Each tier's catch area should be a strict subset of the one above it.

### Pitfall: Stale `next_state()` Overriding Action Handler Work

**Root cause:** The `decide_action` logic chooses WHAT to do. A separate `next_state()` convenience method chooses the NEXT session state. If both run unconditionally — especially if `next_state()` is called AFTER the handler already set state explicitly — the handler's carefully computed state gets overwritten.

**Example from brain.py:**
```python
# BEFORE — buggy:
action = router.decide(msg, session.state)
reply = await handler_for(action)(msg, session)
session.state = next_state(session.state)  # ← BUG: handler set SIMILAR_SHOWN,
                                            #     but next_state saw QUALIFYING → FORM_SENT
```

**Fix — `manual_state` override pattern:**
```python
# AFTER — fixed:
manual_state = None  # action handlers CAN override this

if action == Action.SHOW_PROPERTY:
    manual_state = "SIMILAR_SHOWN"  # if showing similar for first time
    session.similar_shown = True
elif action == Action.ASK_FOR_CODE:
    manual_state = "NEEDS_CODE"
# ... other branches ...

if manual_state:
    session.state = manual_state
else:
    session.state = next_state(session.state)  # fallback only when no override
```

**Rule:** Always give action handlers a `manual_state` escape hatch. The handler knows the correct next state better than any generic `next_state()` helper.

### Pitfall: Router Regex Too Narrow — Missing Natural Language Objects

You expand `NO_CODE_RE` to catch variants like "don't have one", "don't have the code", "no code". But when a user says **"I don't have it"**, the regex fails because "**it**" is not in the allowed object list after the verb.

**Pre-fix regex:**
```python
NO_CODE_RE = re.compile(
    r"(?:don't|do\s*not)\s*(?:have|know|got)"
    r"\s*(?:one|any|the|a|code|number)s?"        # ← "it" is NOT here
    r"|no\s+code"
    r"|\b(?:i\s+(?:don't\s*have|need)\s+(?:a\s+)?code)\b",
    re.IGNORECASE,
)
```

**Problem:** `NO_CODE_RE.search("i dont have it")` returns `None`. Router falls through to `ANSWER_NATURALLY`.

**Post-fix (expanded):**
```python
NO_CODE_RE = re.compile(
    r"(?:don'?t|do\s*not)\s*(?:have|know|got|remember|see|find)"
    r"\s*(?:one|any|the|a|code|number|it|id|that|mine|them)?s?"
    r"|no\s+code"
    r"|\b(?:i\s+(?:don't\s*have|need)\s+(?:a\s+)?code)\b",
    re.IGNORECASE,
)
```

**Changes:**
- **Verbs added:** `remember`, `see`, `find`
- **Objects added:** `it`, `id`, `that`, `mine`, `them`
- **Object made optional with `?`** — so `I don't remember` (no object at all) still matches
- **`s?` on the object list** — handles pluralized variants naturally

**Rule:** Router regexes that catch user intent MUST be permissive, not prescriptive. If a human agent would understand the intent from this phrasing, the regex should too. Post-verb objects should include common English pronouns (`it`, `that`, `mine`) and the trailing object should be optional (with `?`).

**Every funnel step should bait the next.** The form is never a roadblock — it's a VIP unlock:

| Step | Action | The Bait | Session Fields |
|------|--------|----------|----------------|
| No code provided | `ASK_FOR_CODE` | "Go back to the post, get the code from the caption" | — |
| Property card shown (1st) | `SHOW_PROPERTY` | Card has redacted info. "I have more like this in the same area — some not even posted yet." | `similar_shown=True` → `SIMILAR_SHOWN` |
| Property card shown (2nd) | `SHOW_PROPERTY` | "I have unlisted properties in the same area that aren't even on Instagram. Reply YES." | `unlisted_offered=True` → `UNLISTED_OFFERED` |
| → YES typed | `SEND_FORM` | "Fill this out and I'll send them your way — unposted inventory nobody else sees." | `FORM_SENT` |
| → Call offered | `OFFER_CALL` / `SEND_CALENDLY` | "I'm already finding matches for you — let's walk through them before anyone else gets them." | `CALL_OFFERED` / `CALL_BOOKED` |
| → Follow-up | `FOLLOW_UP` | "Got new ones in that area — want me to send them over?" | `DONE` |

**Key technique:** Session fields (`similar_shown`, `unlisted_offered`) act as branching logic gates inside the same `Action.SHOW_PROPERTY` handler. The router stays simple — one action for "show property card" — but the handler branches based on whether the user has been downroad before.

**The form is the defense against spies.** Everyone — spy or legit — gets routed through the form. The data in sheets is intentionally redacted (no exact addresses). Even property cards don't give away the farm. The form is framed as "exclusive access to unposted inventory" which genuinely appeals to buyers while blocking info-extractors.

### Edge Cases Worth Handling

```python
# Phone number detection — must come BEFORE schedule intent
PHONE_RE = re.compile(
    r"\b(call\s+(me|us|my\s+phone|this\s+number)\s+at\s+[\d\-\(\)\+\. ]{7,}"
    r"|[\d\-\(\)\+\. ]{10,}"
    r"|here'?s?\s+my\s+(number|phone|cell|digits))\b",
    re.IGNORECASE,
)

# Expanded acknowledgments — include booking confirmations
ACK_RE = re.compile(
    r"^(ok|okay|thanks|thank\s*you|thx|got\s*it|perfect|great|awesome"
    r"|sounds?\s*good|cool|nice|alright|will\s*do|bet|fs"
    r"|ya|yeah|yes|s[ií]|vale|gracias|de\s*acuerdo|entendido|perfecto"
    r"|ok\s+ya|ya\s+la\s+agende"
    r"|booked|done|all\s+set|scheduled|confirmed)[!.…\s]*$",
    re.IGNORECASE,
)

# Clear rejection — don't push
REJECTION_RE = re.compile(
    r"\b(no\s+thanks|not\s+interested|I'?m\s+good|I'?ll\s+pass"
    r"|leave\s+me\s+alone|stop\s+(texting|messaging|dm)"
    r"|unsubscribe|don'?t\s+(text|message|dm|contact)\s+me"
    r"|no\s+gracias|no\s+me\s+interesa)\b",
    re.IGNORECASE,
)
```

### Spanish Support

Add Spanish keywords to BUYING_RE and INTEREST_RE:
- `me interesa`, `quiero comprar`, `comprar una casa` → buying intent
- `presupuesto`, `financiamiento` → buying intent  
- `casa`, `hogar` → interest


### Pitfall: Nag Loop — Missing Escape Hatch for Soft Rejection

**Root cause:** When a user in `QUALIFYING` or `NEEDS_CODE` state pushes back with "no", "i dont", "nah", "nope", "not really", or confusion words ("why", "huh", "wait"), the Tier 10 fallback keeps routing back to `ASK_FOR_CODE`. The bot repeats the same template indefinitely — "do you have a property code?" — creating a negative UX loop.

**Pre-fix** — Tier 10 NEEDS_CODE fallback always returned `ASK_FOR_CODE`:
```python
if session.state == "NEEDS_CODE":
    return Action.ASK_FOR_CODE  # No escape on pushback
```

**Post-fix — Three new layers:**

1. **SOFT_REJECTION_RE** — catches gentle push-back without requiring a hard rejection (REJECTION_RE):
```python
SOFT_REJECTION_RE = re.compile(
    r"\b(no[. !]*|nah[. !]*|nope[. !]*|i\s*don'?t.*?|pass[. !]*|not really[. !]*|never mind[. !]*)$",
    re.IGNORECASE,
)
```

2. **CONFUSION_RE** — catches confusion/frustration when they don't understand why they're being asked for a code:
```python
CONFUSION_RE = re.compile(
    r"\b(huh[.!?]*|what[.!?]*|what\?+|which one\?|where[.!?]*|why[.!?]*|"
    r"i\s*don'?t\s*understand|not\s*sure|confused|lost|wait[.!?]*|"
    r"what (do you mean|is that|does that mean)|what property code)\b",
    re.IGNORECASE,
)
```

3. **NO_CODE_HELP action** — when soft-rejection or confusion is detected in a code-gathering state, instead of looping `ASK_FOR_CODE`, route to `NO_CODE_HELP`. This action offers a form link + phone number as an escape hatch.

**Router modification:**
```python
if session.state == "QUALIFYING":
    if _is_soft_rejection(msg):
        return Action.NO_CODE_HELP
    return Action.ASK_FOR_CODE

if session.state == "NEEDS_CODE":
    if _is_confusion(msg) or _is_soft_rejection(msg):
        return Action.NO_CODE_HELP
    return Action.ASK_FOR_CODE
```

**Brain.py handler:**
```python
elif action == Action.NO_CODE_HELP:
    reply = await generate_reply("no_code_help", message, form_url=FORM_URL)
    manual_state = "QUALIFYING"  # Reset for retry, don't lock in NEEDS_CODE
```

**Template for `no_code_help`:**
```python
Action.NO_CODE_HELP: (
    "Lead doesn't have a property code or is confused. Respond helpfully: "
    "no problem, they can fill out this form instead ({form_url}) or text Quan at (832) 400-3152. "
    "Keep it warm and under 50 words."
)
```

**Rule:** Every state that repeatedly asks the user for something MUST have an escape-hatch action. The escape hatch must offer genuine forward progress (form, phone) — not just another rephrased version of the same question. Monitor for soft-rejection and confusion words in funnel-gate states.

### Pitfall: Optional Apostrophe in Casual Text Regexes

**Root cause:** You write `don't` in a regex, but Instagram DMs and casual text frequently drop the apostrophe — users type "dont", "cant", "won't" (missing the apostrophe), or they type without it entirely.

**Fix:** Make the apostrophe optional with `?`:
```python
r"don'?t"   # matches both "don't" and "dont"
r"can'?t"   # matches both "can't" and "cant"
r"won'?t"   # matches both "won't" and "wont"
```

**Rule:** In router regexes matching common English contractions used in casual text, always make the apostrophe optional. This triples regex coverage for real-world DMs.

### Pitfall: URL Detection Without Code — Lecturing About Codes When User Sent a Link

**Root cause:** When a user pastes an Instagram reel/post URL into the DM (e.g. `www.instagram.com/sad213ds` or `https://www.instagram.com/reel/CODE/`), the bot can't resolve the URL without authentication. The bot sees "no property code in message" and falls through to `ASK_FOR_CODE`, which lectures the user about QH codes. The user just sent a link, not a question about codes — the response is irrelevant.

**Pre-fix** — Tier 2 catches URL + inquiry → `ASK_FOR_CODE`:
```python
if (URL_RE.search(msg) or INQUIRY_RE.search(msg)) and not code and not session.similar_shown:
    return Action.ASK_FOR_CODE  # ← lectures about QH codes
```

**Post-fix** — URLs get a separate tier that offers the form:
```python
# Tier 1: Property code provided
code = extract_property_code(msg)
if code:
    return Action.SHOW_PROPERTY

# Tier 1.5: URL sent but no code
# Instagram URLs need login to resolve, so we can't extract codes from them.
# Treat this as: "I saw something, I want info" → offer form so Quan matches manually.
if URL_RE.search(msg):
    return Action.SEND_FORM

# Tier 2: Inquiry without URL or code → ask for code
if INQUIRY_RE.search(msg) and not session.similar_shown:
    return Action.ASK_FOR_CODE
```

**Rule:** When the user sends a URL but no code, the actionable response is the FORM (so a human can match them), not a code-lookup. Codes are extracted from text, not URLs. Don't conflate "user asked about a property" with "user pasted a link."

### Pitfall: Hardcoded Phone Fallback When Lookup Fails

**Root cause:** When `fetch_property(code)` returns `None` (code not in sheet), the brain defaults to a hardcoded phone fallback: `"I couldn't find details for {code}. Text Quan at (832) 400-3152!"`. This is a dead-end UX — the user is left to cold-call, the form (which would actually let Quan match them) is never offered.

**Pre-fix** — `brain.py`:
```python
else:
    reply = f"I couldn't find details for {code}. Text Quan at {QUAN_PHONE} for more info!"
    manual_state = "QUALIFYING"
```

**Post-fix** — Offer the form, not the phone. Phone is for users who want to talk NOW, not for code-lookup failures:
```python
else:
    # Code not in sheet — they probably have a real interest, just bad code.
    # Offer the form so Quan can match them manually.
    reply = (
        f"Hmm, I can't pull up {code} in our system. "
        f"Could be a typo or it might not be listed on IG yet. "
        f"Fill this out and Quan will send you matches directly: {FORM_URL}"
    )
    manual_state = "QUALIFYING"
```

**Rule:** For ambiguous/missing data cases, default to the form (a forward action that captures lead info) over the phone (a passive dead-end). The form feeds Quan's matching pipeline; the phone just adds friction. Phone is reserved for "I want to talk to someone now" intent, not for "the bot couldn't find my code."

### Pitfall: Empty Data Source Causes "Stupid Bot" Symptom

**Root cause:** The user reports the bot is "stupid" or "makes no sense" because the bot responds with hardcoded fallback text for every code lookup. The actual root cause is upstream — the data source (Google Sheet, Airtable, DB) is empty. You spend hours tightening router regexes and rewriting templates before realizing the sheet has zero rows.

**Diagnostic — verify the data source first:**
```python
import httpx
# Google Sheet via gviz (no auth needed)
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&range=A1:Z500"
resp = httpx.get(url, timeout=10)
rows = resp.text.strip().split("\n")
print(f"Total rows: {len(rows)}")  # ← if 1 (header only), sheet is empty

# Also try alternate tab names
for tab in ["Properties", "Sheet1", "Listings", "Homes", "Data"]:
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={tab}"
    resp = httpx.get(url, timeout=10)
    if len(resp.text.strip().split("\n")) > 1:
        print(f"Tab '{tab}' has data")
```

**Rule:** Before debugging router/templater logic when the user says "the bot is stupid," verify the upstream data source has data. A 2-minute gviz CSV check beats an hour of regex tightening. Symptoms like "doesn't work for ANY code" or "always returns the fallback" almost always mean the data source is empty, not that the routing is wrong.

### Pitfall: Pipe Separators in LLM Output Break `\s*` Regex Guards

**Root cause:** When the LLM returns a JSON `reply` field, it often separates sentences with a `|` pipe character instead of whitespace:

```json
{"intent": "ask_for_code", "reply": "No worries.|The code's on the reel caption.|Drop it here."}
```

A regex guard like `r"no worries[.,]?\s*(the\s+code...)"` returns `None` because `\s*` doesn't match `|`. The banned template slips through.

**Fix:** Use `[\s|]*` (or `[\s|—]*` if the model uses em-dashes) in the whitespace class:

```python
BANNED_REPLY = re.compile(
    r"(?i)no worries[.,]?[\s|]*"  # ← allow pipe as a sentence boundary
    r"(the\s+code'?s?\s+(on|under|in))",
    re.IGNORECASE,
)
```

**Why the LLM uses pipes:** The prompt doesn't tell the model what separator to use, so it picks something that looks "safe" — `|`. Other models emit `\n`, `\n\n`, ` — `, or just plain spaces. **Always allow the pipe as a delimiter** when writing regex to match multi-clause LLM output.

**Verification:** When a guard "doesn't work," check the raw LLM output in the tagger log. If you see `No worries.|The code's on...` and your regex returns `None`, it's the pipe. Don't waste time debugging the prompt — fix the regex.

**Rule:** Regex guards for LLM text must use `[\s|]` (or wider) for inter-clause whitespace, never bare `\s*`.

### Pitfall: Hardcoded Paths in Copied Bot Versions (env_file, shortlinks, DATA_DIR)

**Root cause:** When you copy a bot from `/home/steve/quanbot-v3/` → `/home/steve/quanbot-v3-hybrid/` (a parallel dev version), `cp -r` copies the file contents — including any hardcoded absolute paths. Three files are the usual offenders:

- `src/config.py` — `env_file` path (loaded secrets from the original v3 dir, not the new hybrid dir)
- `src/config.py` — `shortlinks_path` (e.g. `links.json` lives in original v3 dir)
- `src/database.py` — `DATA_DIR` if hardcoded (sessions DB will silently share the original v3 DB, polluting both bots' state)

**Symptom:** The new bot "works" (uvicorn starts, health check passes) but it reads/writes the WRONG files. You edit the hybrid's templates.py and they don't take effect because it's still reading from the original v3's env. Or the new bot's sessions show up in the production bot's DB.

**Fix — grep for hardcoded paths after every `cp -r`:**
```bash
# After copying a bot version, audit for hardcoded paths
NEW_DIR=/home/steve/quanbot-v3-hybrid
OLD_DIR=/home/steve/quanbot-v3

# 1. Find any string references to the old directory
grep -rn "$OLD_DIR" "$NEW_DIR"/src/ 2>/dev/null
# Expected: zero hits

# 2. Find any hardcoded /home/steve/ paths that aren't a generic
#    "compute from __file__" pattern
grep -rn "/home/steve" "$NEW_DIR"/src/ 2>/dev/null

# 3. Verify env file is the new one, not a symlink or copy of the old
diff -q "$OLD_DIR/.env" "$NEW_DIR/.env" 2>/dev/null
ls -la "$NEW_DIR/.env"  # if it's a symlink to the old, replace with copy

# 4. Verify the database dir is a fresh one
ls -la "$NEW_DIR"/data/sessions.db
# If MD5 matches the old bot's sessions.db, it's a copy — first write will
# diverge, but reads will return the old bot's state
```

**The safe pattern (preferred):**
```python
# In src/config.py:
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")
SHORTLINKS_PATH = os.path.join(BASE_DIR, "links.json")

# In src/database.py:
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
```

Computing paths from `__file__` (not from a hardcoded string) means `cp -r` always works — the new directory computes its own paths. Any absolute hardcoded path in a bot version is a latent bug.

**Rule:** After every `cp -r` of a bot version, grep for the old directory name in `src/`. Zero hits is the only acceptable result. Compute paths from `__file__`, not from string constants.

### Pitfall: Terse `next_step` Instruction Produces Terse Bot Reply

**Root cause:** In the Articechute architecture, the router's `next_step` string is the ONLY instruction the LLM writer sees for how to phrase the response. A terse instruction like `"ask for the QH code from the reel"` produces a blunt reply: *"hey. what's the qh code from the reel caption?"* — no warmth, no context, no explanation of where to find it.

**User feedback (2026-06-19):** *"that's too straight forward and rude"*

**Fix — every `next_step` that initiates user action must include three components:**
1. **Warmth cue** — "greet warmly", "keep it friendly and natural, not demanding"
2. **WHERE to find the info** — "tap the caption on the reel, look for a code that starts with QH"
3. **WHAT happens after they provide it** — "say you'll pull the full details once they share it"

```python
# BAD — terse, produces blunt reply:
next_step = "ask for the QH code from the reel"

# GOOD — warm, contextual, explains next steps:
next_step = ("greet warmly and ask for the QH code. explain WHERE to find it: "
             "tap the caption on the reel, look for a code that starts with QH. "
             "say you'll pull the full details once they share it. "
             "keep it friendly and natural, not demanding.")
```

**After fix:** *"hey there. can you share the qh code from the reel caption? i'll pull the full details for you once you send it over."*

**Rule:** The `next_step` string is not just a routing label — it IS the LLM's creative direction. Treat it like a prompt: include tone, context, and user guidance. Never assume the user knows what a QH code is, where to find it, or what the bot will do with it. This applies to ANY action that asks the user for something — the instruction must explain why, where, and what-next.

### Style Rule: Casual Tone, No Sales-Rep Filler

User preference for templater prompts in IG DM context: the bot sounds "robotic" or "not humanistic" when prompts include phrases like:
- "I'd love to pull up the details for you!"
- "Happy to help"
- "I have everything ready for you instantly!"
- Multiple exclamation points
- Lecturing about what a code is
- Marketing-speak ("exclusive VIP unlock")

**Tone rules that work:**
- One short sentence for simple acknowledgments
- 1-2 casual sentences for qualifying
- No "I'd love to" / "happy to help" filler — start with the action
- "I'm Quan's assistant" (third person) — not "I'm Quan"
- Cap word counts aggressively in the prompt (e.g. "Under 40 words")
- No emoji in templater output (delivery is plain text DMs)

**Example — bad (sounds robotic):**
> "I'd love to pull up the details for you! Property codes starting with QH (like QH001) help me find the exact home fast. Please go back to the post you saw, copy the code from the caption, and paste it here. I'll have everything ready for you instantly!"

**Example — good (sounds like a person):**
> "Hi, I'm Quan's assistant. Do you have a property code (like QH001) you're looking for?"

**Rule:** When writing templater prompts for DMs, test them by reading the EXPECTED OUTPUT aloud. If it doesn't sound like something you'd say to a friend texting you, rewrite. The prompt itself should cap the response (e.g. "Under 40 words, no exclamation points") so the LLM doesn't drift back to salesy defaults.

### Pitfall: SYSTEM Prompt "Voice Examples" Invert When Model Copies Wrong One

**Root cause:** When the SYSTEM prompt lists voice examples and the model copies one verbatim, any third-person example ("Quan can walk you through that") becomes a literal reply — not a useful template. Quoted examples in the SYSTEM prompt are not just *style hints*, they're *patterns the model will pattern-match and reproduce* in user-facing replies. A bad example in the prompt IS the bot's voice for the first few turns.

**Real symptom:** User types "Hello I'm trying to buy my first house in Texas" → bot replies "Quan can walk you through the process. Want to set up a quick chat?" — exactly mirroring a "voice example" the prompt included.

**Fix — example policy in the prompt itself:**
- Every VOICE EXAMPLE in the SYSTEM prompt must be **first-person, in-character, safe to copy verbatim**
- Add an explicit "DO NOT SAY" list with the exact phrasings you don't want reproduced
- Put both the examples and the ban list near the top of the prompt, before the role description, so the model weights them highest

```python
# WRONG — third-person example becomes the bot's voice:
VOICE_EXAMPLES = '''
"Quan can walk you through the process."  # ← model copies this
"Quan can help you narrow it down."        # ← model copies this too
'''

# RIGHT — first-person examples + explicit ban:
VOICE_EXAMPLES = '''
"Yes, I can help you get started."
"I'd love to walk you through it."
"Quan can answer that on a quick call."  # permitted only when SETTING UP CALL, not stating Quan's abilities
'''
```

**Rule:** Any sentence in the SYSTEM prompt that the model could reproduce verbatim is a **published voice** — write it as if it'll be the first thing the user reads. Test by sending 5 messages and reading the actual responses; if any reply is literally a copy of a prompt sentence and that sentence sounds wrong, the prompt is wrong.

**Root cause:** Multiple QuanBot versions run as parallel systemd services (v1:8000, v2:8001, v3:8002). When the user tests via the test UI or directly posts a message, they may report "the bot is responding wrong" without specifying which endpoint. You start debugging v2 (the production version) when the bug is actually in v3 (the new dev version).

**Diagnostic — identify which service is responding:**
```bash
# All three should be running
sudo systemctl status quanbot quanbot-v2 quanbot-v3

# Health check all ports
for port in 8000 8001 8002; do
  echo "--- port $port ---"
  curl -s http://localhost:$port/health || echo "DOWN"
done
```

**Confirm via direct POST:**
```python
import urllib.request, json
for port in [8001, 8002]:
    req = urllib.request.Request(
        f"http://localhost:{port}/webhook/quanbot-v30",  # v3 endpoint on v2 port = 404
        data=json.dumps({"subscriber_id": "diag", "message": "hi"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=10)
        print(f"port {port}: {r.read().decode()[:200]}")
    except urllib.error.HTTPError as e:
        print(f"port {port}: HTTP {e.code}")  # ← 404 = wrong port for that endpoint
```

**Rule:** When debugging a "stupid bot" symptom, confirm the version first. The webhook path is version-specific (`/webhook/quanbot-v20` on v2, `/webhook/quanbot-v30` on v3). A 404 on a known path means the request hit the wrong service. Ask the user which endpoint or test UI they're using before assuming which version is broken.

## Templater (LLM Prompt)

```python
TEMPLATES = {
    Action.INTRO_QUALIFY: (
        "You are a friendly Houston realtor named Quan. A new lead just said: \"{message}\". "
        "Respond warmly in 1 sentence: introduce yourself, say you're a realtor, "
        "and ask what kind of home or area they're looking for. "
        "Keep it under 50 words. Sound human."
    ),
    Action.SEND_FORM: (
        "Lead said: \"{message}\". They're looking for a home. "
        "Respond in 2 sentences: validate their interest, then gently direct them to fill out "
        "this form so you can send matching properties: {form_url}. "
        "Keep it under 50 words. Sound like a helpful friend."
    ),
    # ...
}
```

### Templater Design Rules

1. **~50 word prompts.** The LLM only needs to be charming, not a decision-maker. Long prompts invite hallucination.
2. **All variables injected by router.** Form URLs, property codes, names — all come from the router, not the LLM.
3. **LLM never changes the action.** The prompt describes the action to take; the LLM just phrases it.
4. **One action = one prompt.** No branching logic in the prompt. The router already decided.
5. **Temperature 0.0.** The templater personalizes tone, not content. Zero temperature prevents the LLM from inventing actions or drifting off-template.
6. **NO conversation history in the LLM call.** The templater sends exactly one system prompt + one user message. No `history` array. The router already knows the state; injecting history lets the LLM ignore system instructions and regress to generic replies.
7. **Persona = "Assistant of [Name]," not "[Name]."** The bot speaks as "Quan's Assistant" — warm, helpful, but clearly NOT the human. Prevents first-person impersonation that feels deceptive when the user realizes it's a bot.
   - **SPEAKS AS THE ASSISTANT, NOT FOR QUAN.** The bot uses "I / me / we (the team)" — it does NOT say "Quan can help with that" or "Quan will reach out" or any third-person framing where the assistant is talking ABOUT Quan. Third-person framing about Quan is the AI-ism slip — it sounds like a press release about someone rather than a person helping.
   - **Hard ban list in SYSTEM prompt:** "Quan can", "Quan will", "Quan helps", "Quan knows" — and explicit VOICE EXAMPLES showing first-person phrasing.
   - **Permitted Qu...[truncated]
8. **Lead-complete bypass — skip the LLM entirely.** When the router detects all required lead fields (name + email + phone) are collected, it must NOT call the templater. Send a hardcoded form link directly. The LLM cannot be trusted to output the exact URL (hallucination risk) and calling the LLM wastes tokens for a deterministic reply.

## Session State

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SessionState:
    subscriber_id: str
    state: State = State.NEW
    form_sent: bool = False
    property_code: str | None = None
    last_message: str = ""
    last_action: Action | None = None
    created_at: datetime = field(default_factory=datetime.now)
```

Store in memory dict (`{subscriber_id: SessionState}`). For production, persist to Redis or SQLite.

## Common Pitfalls

### Pitfall 1: LLM defaulting to "let me know how I can help"
**Root cause:** System prompt is too conversational; LLM treats routing instructions as suggestions.
**Fix:** Remove all routing from the LLM. Router handles it. Templater prompts are single-action, no fallback language.

### Pitfall 2: Double message insertion
**Root cause:** Appending user message to history AND passing it as explicit message to LLM.
**Fix:** Pass message once. If using history, don't duplicate. Check `ollama.py` or equivalent integration.

### Pitfall 3: State not advancing
**Root cause:** Router method not updating `session.state` after deciding action.
**Fix:** Every `decide_action` path must set the next state: `session.state = next_state`.

### Pitfall 4: LLM changing the action
**Root cause:** Prompt includes conditional language ("if they seem interested, offer a call").
**Fix:** Remove all conditionals from templater prompts. The router already decided. The prompt is imperative: "Respond warmly... ask what they're looking for."

## Bot Backend Migration Pattern (ManyChat + Tunnel Repointing)

When multiple bot versions run on different WSL ports and ManyChat's automation is hardcoded to a specific webhook URL, the cleanest way to switch which bot serves traffic is NOT the ManyChat dashboard — it's repointing the Cloudflare tunnel and adding a path alias on the new backend.

### The Problem

ManyChat External Request blocks are hardcoded to URLs like `https://quanbot.quann.homes/webhook/quanbot-v20`. Changing this URL requires:
- Manual dashboard editing (slow, error-prone)
- ManyChat MCP cannot edit External Request block URLs (read-only on flow internals)

### The Solution: Tunnel Repoint + Backend Alias

**Step 1 — Repoint the tunnel** (change backend port):
```yaml
# /mnt/c/Users/steve/n8n-deploy/data/cloudflared/config.yml
# BEFORE:
#   - hostname: quanbot.quann.homes
#     service: http://host.docker.internal:8000   # v2
# AFTER:
ingress:
  - hostname: quanbot.quann.homes
    service: http://172.27.155.109:8003   # v3-hybrid (WSL IP, changes per boot)
```

**Step 2 — Add path alias on the new backend** (if paths differ):
```python
# /home/steve/quanbot-v3-hybrid/src/main.py
@app.post("/webhook/quanbot-v30")  # new backend's canonical path
@app.post("/webhook/quanbot-v20")   # ← alias for backward compatibility
async def webhook(request: Request):
    """Handles both old and new paths so tunnel repointing works
    without touching ManyChat dashboard."""
    return await _handle_webhook(request)
```

**Step 3 — Restart tunnel**:
```bash
docker restart cloudflared
```

**Step 4 — Verify both routes**:
```bash
curl -s -X POST http://localhost:8003/webhook/quanbot-v30 \
  -H "Content-Type: application/json" -d '{"message":"hi","subscriber_id":"test"}'
curl -s -X POST http://localhost:8003/webhook/quanbot-v20 \
  -H "Content-Type: application/json" -d '{"message":"hi","subscriber_id":"test"}'
# Both must return identical responses
```

**Step 5 — Verify public**:
```bash
curl -s -X POST https://quanbot.quann.homes/webhook/quanbot-v20 \
  -H "Content-Type: application/json" -d '{"message":"hi","subscriber_id":"test"}'
# Must return hybrid reply, not old v2 text
```

### Why this beats dashboard editing

- One `config.yml` edit + restart = instant, fully reversible
- No MCP tool needed (MCP can't edit flow internals anyway)
- User's bookmarked test URL stays the same
- Rollback: change config.yml back, restart cloudflared

### Pitfall: Webhook path mismatch

Always `grep -n "app.post" src/main.py` on BOTH the old and new backends before repointing. If paths differ, the alias is mandatory — otherwise every IG DM will 404 after cutover.

### Pitfall: WSL IP changes per boot

The WSL2 `eth0` IP is not stable. After a WSL reboot:
1. `ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1` to get new IP
2. Update `config.yml` service URL
3. `docker restart cloudflared`

### Pitfall: `RouterDecision.state_after` Is the Canonical Field Name

**Root cause:** When designing the 3-layer architecture's router return type, the natural names are `next_state`, `next`, `state_after_action`, or `new_state`. The canonical name in this architecture (and the one that the shadow replay, the writer, and the brain.py glue all read) is **`state_after`** — singular, fixed, NOT `next_state`.

**Symptom (caught 2026-06-17):** Wrote `RouterDecision(state_after=session.state)` correctly on first try, then on the next feature added `next_state=` to a related helper. Replay harness silently dropped the new field because `**kwargs` filtering rejected unknown keys. Bot state stopped advancing; users got stuck in `NEEDS_CODE` indefinitely.

**Fix — the field name is part of the contract:**

```python
# RIGHT — canonical name (matches flow.db `state_after` column)
@dataclass
class RouterDecision:
    intent: Intent
    action: Action
    state_after: State        # ← THIS NAME, not next_state
    needs_llm: bool = True
    confidence: float = 1.0
    rationale: str = ""
```

The field is named to **match the `flow.db` `turns.state_after` column** so replay code can write the router's output directly to the DB without a rename. Don't rename it because `next_state` reads better; the DB schema is the contract.

**Rule:** When extending `RouterDecision`, append fields (`confidence`, `rationale`, `needs_llm`) — never rename existing ones. The shadow replay reads the router's `state_after` to advance the synthetic session; if you rename the field, the synthetic session freezes at the current state and you'll think the bot is broken when it's actually your replay harness.

### Pitfall: LLM Timeout on Simple Data Lookups — Add a Deterministic Data Responder

**Root cause:** The router correctly re-attaches property data and routes a question like "how many beds?" to `REPLY_VOICE` (LLM writer). But the LLM has an 8-second timeout. When it times out, the fallback kicks in — and the fallback pushes the form instead of answering from the data the router already fetched. The user asked "how many beds", the sheet HAS "5 beds", but the bot says "please fill out the form." This is the worst possible UX: the data exists, the router fetched it, but the LLM's latency destroyed the answer.

**Fix — add a deterministic data responder BEFORE the LLM call in the writer:**

```python
def _property_data_reply(decision: RouterDecision, current_message: str) -> str | None:
    """If the user asks a simple property data question and we have the data,
    answer directly WITHOUT calling the LLM. Returns reply text or None."""
    if not decision.property_data:
        return None  # no data → fall through to LLM

    p = decision.property_data
    ml = current_message.lower().strip()

    # Price questions
    if any(k in ml for k in ["how much", "price", "cost", "starting from"]):
        price = str(p.get("price", "")).strip()
        if price:
            return f"It is starting from {price}."
        return None  # no price data → fall through

    # Beds questions
    if any(k in ml for k in ["how many bed", "beds", "bedroom", "number of bed"]):
        beds = p.get("beds", "")
        if beds:
            return f"It has {beds} beds."
        return None

    # Baths, area, sqft, garage, models — same pattern
    # ...

    # "Tell me about it" → full summary from sheet data
    if any(k in ml for k in ["tell me about", "more details", "full details"]):
        parts = []
        if p.get("city"): parts.append(f"located in {p['city']}")
        if p.get("beds"): parts.append(f"{p['beds']} beds")
        if p.get("baths"): parts.append(f"{p['baths']} baths")
        if p.get("sqft"): parts.append(f"{p['sqft']} sqft")
        if p.get("price"): parts.append(f"starting from {p['price']}")
        if parts:
            return f"This property is {', '.join(parts[:-1])}, and {parts[-1]}."
        return None

    return None  # not a data question → fall through to LLM

# In the writer's execute() method, BEFORE building the LLM prompt:
prop_reply = _property_data_reply(decision, current_message)
if prop_reply:
    return {"reply": prop_reply, "latency_ms": 0, "llm_called": False}
# Otherwise: fall through to LLM as before
```

**Results (2026-06-19 stress test):**
- "How many beds" → 0.4ms, "It has 5 beds." (was: 8s LLM call → timeout → form spam)
- "How much" → 0.4ms, "It is starting from $262K."
- "What area" → 0.4ms, "It is located in about 45 minutes outside Houston."
- "Tell me about it" → 0.4ms, full property summary from sheet
- 6/6 property data questions answered without any LLM call

**Architecture with this layer added:**

```
User Message → Python Router (0ms) → [Property Data Responder (0.4ms)] → LLM Templater (~8s)
                    ↓                        ↓                               ↓
              WHAT to do              DATA LOOKUP (skip LLM)         HOW to say it
              (action enum)           (if data exists, answer)        (creative text)
```

**Three-tier short-circuit hierarchy:**
1. **Router short-circuits** (0ms): `push_to_form`, `push_to_call` — deterministic actions with fixed URLs
2. **Data responder** (0.4ms): beds/baths/price/area/sqft/garage/models/full-summary — data lookups from sheet
3. **LLM writer** (~8s): everything else — creative replies, context-aware phrasing, tone

**Design rules for the data responder:**
1. Only intercept messages that match specific data-field keywords (beds, price, area, etc.)
2. Only answer if the field has data — if `price` is empty, return `None` and fall through to LLM
3. Never fabricate — use exactly what's in the property_data dict
4. "Tell me about it" builds a full summary from ALL available fields, not just one
5. Anything that doesn't match → return `None` → LLM handles it (preserves creative replies)
6. The responder runs AFTER the router (which re-attached the property data) but BEFORE the LLM call
7. Latency tells you which tier fired: 0ms = router short-circuit, <1ms = data responder, >1s = LLM

**Rule:** When the bot has a structured data source (Google Sheet, DB, API) and the user asks a question that maps to a specific field in that data, answer directly from the data without calling the LLM. The LLM's job is creative phrasing — "how many beds" doesn't need creativity, it needs the number from the sheet. This eliminates an entire class of timeout failures and saves LLM calls for questions that actually need natural language.

### Pitfall: Splitting Intent Classification From LLM Kills Conversation Context Understanding

**Root cause:** The deterministic-router pattern's core selling point — "no LLM in the router, pure Python keyword matching" — eliminates the LLM from the ONE task it's actually good at: understanding conversational context and sequence. The router sees only the current message and keyword-matches it. It cannot tell the difference between:

- "How much?" (first time, no property shown) → should ask for code
- "How much?" (after seeing QH015) → should answer from property data
- "How much?" (after being asked for code twice already) → should push form

The router tries to compensate with a state machine (`prior_state` checks, `code_ask_count` escalation, `last_property_code` re-attachment). But the state machine is a crude approximation of what a context-aware LLM does naturally: understanding that "it" refers to the property we just discussed, knowing when to stop asking for codes, recognizing the conversation arc.

**Real-world comparison (2026-06-20, QuanBot SBX vs PROD):**

PROD (tagger.py) — LLM does everything in one call:
- Reads full conversation history via a context brief (last property code, last user message, last bot reply, conversation state)
- Classifies intent WITH context
- Writes reply WITH context
- Has an ANTI-LOOP RULE: "If the conversation history shows the user already said they don't have a code... do NOT ask for a code again"
- Understands "it", "this one", "that one" from conversational context

SBX (router.py + writer.py) — split into two pieces:
- Router: keyword-matches CURRENT message only → decides intent → tells writer what to do
- Writer: LLM only writes text based on router's decision — it doesn't classify or understand flow
- Router never reads conversation history to understand context
- `classify_intent()` calls `extract_signals(message)` on the CURRENT message only
- State machine has 8 states and 18 intents, but none of that matters because intent classification itself doesn't understand the conversation

**User feedback (2026-06-20):** *"It's like you fail to do what the production does best, which is knowing the sequence of the conversation and where to lead to, versus this one, where it just does whatever it wants to do. Why is that? This was supposed to be an improvement, but instead it's a disaster."*

**The irony:** The deterministic router was designed to be "deterministic and debuggable" — and it is. But by removing the LLM from intent classification, it lost conversation understanding. You gain testability and lose the ability to handle multi-turn context — which is the entire point of a conversational bot.

**When this pattern FAILS:**
- Multi-turn conversations where "it" / "this one" / "that one" refer to prior context
- Sequences where the same message means different things at different points in the conversation ("how much?" after seeing a property vs. cold start)
- Anti-loop scenarios where the bot should recognize it already asked for a code twice
- Any conversation where the user's intent depends on what was said 3 turns ago

**When this pattern WORKS:**
- Single-turn interactions (property code → show card → done)
- Deterministic routing where the current message fully determines the action (phone number → form, explicit tour request → call link)
- Simple data lookups (beds, price, area — answer from sheet, no context needed)

**Fix options:**
1. **Hybrid: LLM classifies intent with history, router handles deterministic actions.** Let the LLM see conversation history and classify intent (like PROD does), but keep deterministic short-circuits for phone numbers, form requests, and property data lookups. The router's keyword tiers become a FAST PATH, not the only path.
2. **Context-aware router layer.** Build a context analyzer that reads conversation history and extracts: what property was discussed, how many times code was asked, what the user's last question was. Pass this as structured data to the router — but this is essentially rebuilding what the LLM does naturally, in Python, poorly.
3. **Let the LLM classify with a context brief (PROD's approach).** The LLM gets a compact summary (last code, last user message, last bot reply, state) and classifies intent. This is what PROD's tagger.py does and it works.

**Rule:** The deterministic-router-LLM-templater pattern is NOT a universal improvement over LLM-based classification. It trades conversation understanding for testability. For single-turn or simple-routing bots, it's a clear win. For multi-turn conversational bots where context and sequence matter (like a real estate receptionist handling 5+ message exchanges), removing the LLM from intent classification is an architectural error. The LLM's job is not just "how to say it" — it's "understand what the user means in context." If you take that away, no amount of state machine complexity will compensate.

## Related

- `cloudflare-tunnel` skill — full tunnel management docs
- `manychat-mcp` skill — MCP limitations (cannot edit flows)
- `references/deterministic-data-responder-pattern.md` — three-tier short-circuit pattern for chatbots with structured data sources. Router (0ms) → Data Responder (0.4ms) → LLM (~8s). Answers simple field-mapping questions (beds, price, area) from the data dict without calling the LLM, eliminating timeout failures on the exact questions most likely to time out. Includes implementation code, design rules, and measured results.
- `references/stress-test-harness-pattern.md` — when you've built the framework and need to know if it's safe to ship. End-to-end integration test of router + LLM + guards against mock conversations built from real prod message patterns. Covers 14-template mock generation, baseline vs full-LLM scoring, 5 framework issues this catches (banned-phrase leak, URL hallucination, timeouts, voice drift, classifier FPs), sandbox isolation guarantees, and the harness-bug pitfalls (threading.local in async, key mismatch, whitespace inputs).
- `references/shadow-mode-replay-pattern.md` — when stress tests are too clean. Replays REAL prod conversations turn-by-turn against the new framework (log-only, never send). Catches per-state bugs, voice drift across turns, latency tails, and Ollama rate-limit behavior that mock data misses. Includes the 3-voice critique rubric (Devil's Advocate / Systems Expert / Critique Expert) that every shadow report must pass before being shown to the user.
- `references/real-conversation-pattern-stress-test-2026-06.md` — results of running 67 real multi-turn IG DM conversations from flow.db head-to-head against Production v4 vs Articechute sandbox. Contains the 5 dominant conversation patterns (QH code wall at 57%, one-message ghost at 59%, funnel stuck at 86%, process/market questions, shared reel links) and the 5 fixes for 90% improvement. Load this before designing router intent classes or funnel-gate logic — the patterns are empirical, not assumed.
- `references/articechute-stress-test-post-fix-2026-06.md` — the "after" data point: 193-turn sampled stress test run AFTER all 5 fixes + 6 additional fixes (short-circuit, guard normalization, router keyword overlap, expanded CANT_FIND_CODE). Voice score 0.854, 51.3% short-circuited, 16.6% code asks (down from ~45%). Includes 4 edge cases for next iteration and reproduction recipe.
- `references/articechute-v2-implementation-patterns.md` — 6 reusable architecture patterns from the Articechute v2 build: code_ask_count strike escalation, current_message first-reply acknowledgment, gviz Google Sheets property store (no auth), dual-webhook FastAPI server (ManyChat + Meta), short-circuit deterministic actions, shadow replay against real flow.db conversations. Load when building or extending a deterministic-router chatbot.
- `references/stress-test-harness-pattern.md` (updated 2026-06-19) — now includes 5 pitfalls from the side-by-side comparison and real-pattern stress test sessions: (1) **Unequal data access rigging** — always audit both systems' data sources before running a head-to-head comparison; (2) **Test harness banned-phrase list divergence** — source the test's banned-phrase list from the actual bot config, not from memory; (3) **Presenting results before acknowledging test flaws** — apply 3-voice critique to the TEST ITSELF, not just the framework under test, and state limitations before headline numbers; (4) **Synthetic scenarios not present in real data** — validate every scenario against real conversation logs before running; emoji spam, prompt injection, and "meaning of life" had 0 instances in 1,866 real IG DMs; (5) **`_norm_qh_code()` missing `.upper()` on suffix** — lowercase `qh_9njnf0` normalizes to `QH_9njnf0` instead of `QH_9NJNF0`, causing silent property-lookup failures.

### Pitfall: Code-Loop Is the #1 Friction Point (57% of Real Conversations)

**Empirical finding (2026-06-19, 67 real conversations):** 38 of 67 engaged users (57%) never provide a property code. The bot asks → user says "I don't have it" or ghosts. 30/67 conversations in production v4 hit the code loop. Articechute reduced this to 21/67 with better escape hatches, but it's still the dominant failure mode.

**Fix — 3-strike code escalation:**
```python
CODE_ATTEMPTS_KEY = "code_attempts"

# In router, when state == NEEDS_CODE and user hasn't provided code:
attempts = session.get(CODE_ATTEMPTS_KEY, 0) + 1
session[CODE_ATTEMPTS_KEY] = attempts

if attempts >= 3:
    return Action.SEND_FORM  # Stop asking for code, push to form
elif attempts >= 2:
    return Action.OFFER_CALL  # Offer a call as alternative to code
else:
    return Action.ASK_FOR_CODE  # Still try, but with varied phrasing
```

**Rule:** Any funnel-gate that asks the user for a specific piece of data MUST have a
3-strike escalation path. After 3 attempts, stop asking and offer an alternative
forward action (form, call, human handoff). The code loop kills more conversations
than any other single design choice.

### Pitfall: First Reply Leading With Code Request Causes 59% Drop-Off

**Empirical finding:** 175 of 296 conversations (59%) sent exactly 1 message and
disappeared. The bot's first reply is the entire conversation for most users. When
that reply leads with "do you have a property code?", users bounce.

**Fix — acknowledge first, ask for code second:**
```python
# WRONG — leads with code:
Action.INTRO_QUALIFY: "Hi, I'm Quan's assistant. Do you have a property code (like QH001)?"

# RIGHT — acknowledges the user's message, then asks:
Action.INTRO_QUALIFY: "User said: '{message}'. Greet them warmly, respond to what they "
    "actually said (if they mentioned an area, acknowledge it; if they said hi, introduce "
    "yourself). THEN ask if they have a property code from the post. Under 40 words."
```

**Rule:** The first reply must demonstrate that the bot understood the user's message.
If the user asked a question ("what areas do you cover?"), ANSWER it first. If they
said "hi", introduce yourself first. The code request comes AFTER acknowledgment, never
before. This applies to any chatbot where a gating question exists — the gate should
not be the first thing the user sees.

### Pitfall: Answering Questions Without Requiring a Code

**Empirical finding:** 33 of 67 conversations involved process or market questions
("what areas do you cover", "how does buying work", "what price range"). Both
architectures tried to redirect to property codes instead of answering the question.

**Fix — ANSWER_NATURALLY intent for process/market questions:**
```python
# Router should detect question patterns and route to ANSWER_NATURALLY
QUESTION_RE = re.compile(
    r"\b(what areas?|where|which (areas|neighborhoods|cities)|how does (buying|selling|the process) "
    r"work|what (price|budget|range|cost)|how much|how long|what (do you|are your))\b",
    re.IGNORECASE,
)

# In router:
if QUESTION_RE.search(msg) and not extract_property_code(msg):
    return Action.ANSWER_NATURALLY  # Answer the question, then offer form
```

**Rule:** Questions about the agent's service area, process, or market knowledge require
NO property code. Route them to an intent that answers the question using configured data
(coverage areas, process overview) and then offers the form as a next step. Forcing a
code for these questions is a category error — the user is qualifying the AGENT, not
asking about a specific property.

### Pitfall: 3-Voice Critique Discipline on Every Framework Change

**Root cause:** Ollama Cloud rate-limits certain models (especially the smaller/faster tiers) by cutting off generation mid-response. The HTTP status is 200 OK, `finish_reason=stop`, but `content=""` — looks like "model returned nothing" but it's actually a rate-limit cutoff.

**Symptom:**
```python
result = await llm.call(prompt)
print(result.content)        # ""
print(result.finish_reason)  # "stop"  ← not "length", not error
# 5-13s latency suggests the model was thinking when cut off
```

**Anti-pattern — retry the same model:**
```python
# WRONG — wastes 3x latency budget on rate-limited model
for _ in range(3):
    result = await llm.call(prompt)
    if result.content:
        break
# At best: 3x latency. At worst: 3x rate-limit hits.
```

**Fix — fall back to router template, not retry:**
```python
result = await llm.call(prompt)
if not result.content or len(result.content.strip()) < 5:
    # Rate-limit cutoff. Fall back to deterministic template (no LLM).
    result = router.template_for(action, message)
    result.source = "router_template"  # tag so logs distinguish
```

**Rule:** Empty content from a 200 OK response with `finish_reason=stop` is Ollama rate-limiting, not a model bug. Switch to the deterministic router template instead of retrying. The shadow-mode replay on 2026-06-17 caught 4/30 turns (13%) hitting this — a "retry 3x" pattern would have wasted 12 LLM calls for 4 successful fallbacks.

### Pitfall: P95 Latency Must Fit the Webhook Window or Users See Timeouts

**Root cause:** ManyChat's webhook window is 5-10 seconds. If your bot's P95 latency is 8 seconds, you're "fitting" the window but P99 will spike to 12-15s — and every P99 spike = user-visible timeout (bot says nothing, user thinks they're ignored).

**Diagnostic — measure P50, P95, P99 separately:**
```python
latencies = [r.latency_ms for r in replay_results]
print(f"P50: {np.percentile(latencies, 50):.0f}ms")
print(f"P95: {np.percentile(latencies, 95):.0f}ms")
print(f"P99: {np.percentile(latencies, 99):.0f}ms")
print(f"Max: {max(latencies):.0f}ms")
# All four matter. P95 ≤ window doesn't mean P99 ≤ window.
```

**Fix options when P99 > window:**
1. **Fast-path for common patterns:** Cache replies for `hi`, `QH001-QH050`, etc. Return template in <50ms, skip LLM entirely.
2. **Streaming partial responses:** Send first 30 words as soon as LLM produces them, fill in rest async. User sees activity even if full reply takes 9s.
3. **Tier the model:** Use a faster (smaller) model for short replies, reserve big model for complex queries.
4. **Async background replies:** Return 200 OK immediately, send the real reply 2s later when LLM finishes. (ManyChat may not support this — check first.)

**Rule:** Don't ship a bot where P95 is "barely fitting" the webhook window. P99 will spike. The fix isn't "optimize until P99 fits" — it's "design the architecture so P99 doesn't matter" (cache, streaming, async).

### Pitfall: Splitting Intent Classification From LLM Kills Conversation Context Understanding

**Confirmed in production (2026-06-20):** QuanBot's SBX architecture split intent
classification (deterministic router, keyword-only, 0ms) from reply generation (LLM
writer, ~8s). The router keyword-matched the CURRENT message only — it never read
conversation history. This caused catastrophic failures in multi-turn conversations:

- "How much?" after seeing QH014 ≠ "How much?" cold start — router treated them identically
- "I don't have it" (referring to a code asked 2 turns ago) was classified as a new
  statement, not a code-ask follow-up — router asked for code AGAIN
- "Yes" (answering "do you want to see it?") vs "Yes" (answering "do you have a code?")
  — same keyword, opposite meaning depending on conversation context
- No ANTI-LOOP rule — the router had no concept of "user already said they don't have
  a code, stop asking." The `code_ask_count` was a crude approximation that fired too
  late (after 3 strikes) vs an LLM that reads history and stops asking immediately

**Stress test progression proved the fix:**
- Old router+writer split: 33/52 pass (63.5%)
- Unified tagger (LLM reads history + classifies + writes in one call): 40/52 (76.9%)
- After bug fixes: 45/52 (86.5%)

**The fix — unified tagger.py:**
- Single LLM call reads full conversation history → classifies intent → writes reply → returns Pydantic TaggerResult
- Rich system prompt (~168 lines) with ANTI-LOOP RULE ported from PROD
- Deterministic shortcuts preserved for intents where LLM adds no value (form URL, phone extraction, can't-find-code fallback) — these bypass the LLM entirely (0ms)
- LEAD_INTENT and INFO_QUESTION always go to LLM (need greeting + answer + form link)

**When the split IS appropriate:**
- Single-turn bots where context doesn't matter (each message is independent)
- Bots where the keyword-to-intent mapping is unambiguous (no context-dependent meaning)
- Bots with extremely tight latency budgets where the LLM call for classification is too expensive

**When the split is NOT appropriate:**
- Multi-turn conversational bots (5+ message exchanges) where context and sequence matter
- Bots where the same word means different things depending on conversation history
- Bots with an anti-loop requirement (stop asking X after user said they can't provide it)

**Rule:** If your bot needs to understand conversation sequence and context — let the
LLM classify intent WITH history. Don't rebuild LLM understanding in Python (more
states, more keywords, more regex). The deterministic router pattern trades
conversation understanding for testability — that tradeoff fails for multi-turn bots.

See: `receptionist-agent` skill → `references/tagger-architecture-redesign.md` for
the full implementation, stress test results, and bug progression.

### Pitfall: Stress Test Passes But Shadow Replay Fails (Why Both Are Needed)

**Root cause:** Stress tests use synthetic conversations derived from prod patterns. The patterns are real, but the ORDERING and ADJACENT CONTEXT are not. A bot that handles isolated turns perfectly can fail at turn 7 of a real conversation because:
- State machine has drifted from `QUALIFYING` → `FORM_SENT` → `DONE` but a real user looped back to `NEEDS_CODE`
- Voice drift compounds: the LLM sounds different in turn 8 than turn 1
- A guard that was safe on isolated turns now breaks compound sentences

**Rule:** Stress tests catch class-level bugs (router regex, banned phrases, timeouts). Shadow replays catch per-state and per-flow bugs (voice drift, state loops, compound-input failures). Run BOTH before any framework cutover.

### Pitfall: URL Guard Mid-Sentence Scrub Breaks Output

**Root cause:** A URL allowlist guard meant to strip hallucinated URLs (`forms.gle/xyz123`) accidentally cuts valid URLs mid-string, leaving broken fragments:

```python
# BAD — naive regex strips only the path, leaves broken prefix
text = "Check https://quann.homes/qh232 today"
result = re.sub(r"/qh\d+", "", text)
# result = "Check https://quann.today"  # ← broken URL fragment
```

**Fix — strip WHOLE URL or replace with placeholder, never leave fragments:**
```python
URL_RE = re.compile(r"https?://[^\s]+")

def scrub_urls(text: str, allowlist: set[str]) -> str:
    def replace(match):
        url = match.group(0)
        # Extract host
        host = url.split("/")[2] if "://" in url else url.split("/")[0]
        if host in allowlist:
            return url  # keep allowed URL
        return "[link]"  # placeholder, not empty
    return URL_RE.sub(replace, text)
```

**Rule:** URL guards must produce clean output. Either keep the URL whole, remove it whole, or replace with a placeholder. Never leave a partial URL or empty string in user-facing text. Coherent-after-scrub is the metric — "regex matched" is not.

### Pitfall: Short-Circuit Deterministic Actions — Don't Call LLM When Template Is Enough

**Root cause:** Actions like `push_to_form` and `push_to_call` are deterministic — the reply content is fixed (a form URL, a Calendly link). Routing these through the LLM writer wastes 2-8 seconds of latency AND introduces failure modes: the LLM can return empty (Ollama rate-limit), timeout, or drift from the exact URL. In the Articechute stress test, `push_to_form` replies took 8s and sometimes came back empty.

**Pre-fix** — every action goes through the LLM writer:
```python
async def execute(action, message, session):
    prompt = TEMPLATES[action].format(message=message, **session_vars)
    reply = await llm.call(prompt)  # ← 2-8s, can be empty
    if not reply:
        reply = fallback_text  # ← but user already waited 8s
    return reply
```

**Post-fix — short-circuit deterministic actions before the LLM call:**
```python
# In writer.py — deterministic short-circuits (no LLM needed)
SHORT_CIRCUIT_REPLIES = {
    "push_to_form": "Drop your details in this form and we'll get you started: {form_url}",
    "push_to_call": "Let's get you on a quick call — pick a time that works: {calendly_url}",
}

async def execute(action, message, session):
    if action in SHORT_CIRCUIT_REPLIES:
        return SHORT_CIRCUIT_REPLIES[action].format(**session_vars)  # <2ms, always succeeds
    # Only creative actions (ask_for_code, reply_voice, show_property) use LLM
    prompt = TEMPLATES[action].format(message=message, **session_vars)
    return await llm.call(prompt)
```

**Results from 193-turn stress test (2026-06-19):**
- `push_to_form` latency: 8102ms → 2ms (short-circuit)
- `push_to_call` latency: 749ms → 0.4ms
- 51.3% of turns short-circuited (didn't need LLM at all)
- LLM errors dropped because LLM is only called for creative actions
- Voice score 0.854 (the LLM turns that DO run get full attention)

**Rule:** If an action's reply is deterministic (URL, fixed text, template with no creative writing), short-circuit it. The LLM should only be called when the reply needs to adapt to what the user said. This eliminates an entire class of empty-reply failures and cuts P95 latency in half. The form URL must be exact — an LLM hallucinating a URL is worse than a template.

**Caveat:** Short-circuit replies still pass through guards (banned phrases, URL allowlist). The banned-phrase guard caught "Quan will" in the form reply — rephrased to "we'll get you started" (not "Quan will reach out"). Always test short-circuit text through the guard pipeline.

### Pitfall: Price Fabrication Guard False-Positive from $/Comma Mismatch

**Root cause:** A fabrication guard compares LLM-output prices against expected prices from the property sheet. The regex captures `"258,990"` (no `$`), but the expected value is `"$258,990"` (with `$`). The string comparison never matches → every real price gets flagged as fabrication.

**Pre-fix:**
```python
# Guard compares raw regex capture vs expected
match = PRICE_RE.search(reply)
if match and match != expected_price:  # "258,990" != "$258,990" → always flags
    return GuardResult(violation="fabrication")
```

**Post-fix — normalize both sides before comparison:**
```python
def normalize_price(s: str) -> str:
    return s.replace("$", "").replace(",", "").strip()

match = PRICE_RE.search(reply)
if match and normalize_price(match) != normalize_price(expected_price):
    return GuardResult(violation="fabrication")
```

**Rule:** Guards that compare LLM output to reference data MUST normalize both sides (strip currency symbols, commas, whitespace, units) before comparison. The LLM might output `$258,990`, `258990`, `$258,990.00`, or `258,990` — all are the same price. Without normalization, every real price is a false positive.

### Pitfall: Router Keyword Overlap — "What Property" Routing to Wrong Intent

**Root cause:** Messages like "what property is this" start with "what" (a question keyword) but don't contain the specific phrase the router expects ("the property"). The router falls through to a broader intent (LEAD_INTENT → push_to_call) instead of the correct one (ASK_FOR_CODE).

**Pre-fix:**
```python
# Only catches "the property" — misses "what property", "which home"
INQUIRY_RE = re.compile(r"\b(the property|the home|the listing)\b", re.I)
```

**Post-fix — add direct property-reference phrases:**
```python
# "what property is this" → user is asking about a specific property → ask for code
PROPERTY_REF_RE = re.compile(
    r"\b(what|which|that|this)\s+(property|home|house|listing|place)\b",
    re.I
)
# Check BEFORE generic inquiry/lead intent
if PROPERTY_REF_RE.search(msg) and not extract_property_code(msg):
    return Action.ASK_FOR_CODE
```

**Rule:** When a router tier catches more messages than the tier below it, it's too broad. "What property is this" should NOT route to LEAD_INTENT — it's a specific property inquiry. Add explicit property-reference patterns to the ASK_FOR_CODE tier, checked before generic lead/question tiers. The broad→narrow rule from the Koray analogy applies: each tier must be a strict subset of the one above.

### Pitfall: Expanded CANT_FIND_CODE Patterns — Casual DMs Drop Words

**Root cause:** Users type "i dont hava code", "no i dont", "dont see a code", "where is the qh" — the original CANT_FIND_CODE regex only caught 4-5 variants. 57% of users who engage never provide a code, and their phrasings are wildly varied.

**Post-fix — ~15 expanded patterns:**
```python
CANT_FIND_CODE_RE = re.compile(
    r"(?:don'?t|do\s*not)\s*(?:have|know|got|remember|see|find)"
    r"\s*(?:one|any|the|a|code|number|it|id|that|mine|them)?s?"
    r"|no\s+code"
    r"|don'?t\s+(?:see|know|have)\s+(?:the\s+)?(?:qh?|code)"
    r"|where(?:'?s| is)\s+(?:the\s+)?(?:qh?|code)"
    r"|\b(?:i\s+(?:don't\s+have|need)\s+(?:a\s+)?code)\b",
    re.IGNORECASE,
)
```

**Key additions:** verbs `remember`, `see`, `find`; pronouns `it`, `that`, `mine`; optional trailing object `?` (catches "I don't remember" with no object at all); `where's the code` and `where is the qh` (user asking WHERE the code is, not just saying they don't have it).

**Rule:** Router regexes for user intent MUST be permissive. If a human agent would understand the intent from the phrasing, the regex should too. Post-verb objects should include common pronouns (`it`, `that`, `mine`) and the trailing object should be optional. Apostrophes must be optional (`don'?t`). Test against real DM logs from flow.db, not synthetic examples.

### Pitfall: QH Code Format Evolution — Two Formats in the Same Sheet

**Root cause:** The Google Sheet evolved from old-format property codes (`QH001`, `QH017`) to new-format codes derived from Instagram reel URLs (`QH_9NJNF0`, `QH_X_JIMA`). The router's regex was `r'\b(QH|qh)\s*(\d{1,3})\b'` — only matches old format. 35 of 39 sheet codes are new-format. Every property-lookup scenario with a new-format code silently fails: the regex doesn't match, the router never extracts the code, and the bot falls through to a generic response.

**Symptom:** User tests with a real sheet code like `QH_9NJNF0` and the bot says "I don't see a property code" or pushes to form. The sheet has the code, property_store returns data, but the router never extracts it from the message.

**Fix — dual-format regex + uppercase normalization:**
```python
# Matches BOTH old (QH001) and new (QH_9NJNF0) formats
QH_CODE_RE = re.compile(
    r'\b(QH|qh)[_\s]?([A-Z0-9]{1,6})\b',  # QH followed by optional underscore/space + alphanumeric
    re.IGNORECASE,
)

def _norm_qh_code(raw: str) -> str:
    """Normalize extracted code to uppercase sheet format."""
    code = raw.upper().replace(' ', '_')
    # Old format: QH001 → QH001 (no underscore)
    # New format: qh_9njnf0 → QH_9NJNF0
    if '_' not in code and code.startswith('QH') and code[2:].isdigit():
        return code  # old format, no underscore needed
    return code  # new format already has underscore from .upper()

# Cross-reference: if user types "QH9NJNF0" (no underscore), check sheet
# for "QH_9NJNF0" by trying both with and without underscore
def lookup_with_fallback(raw_code):
    normalized = _norm_qh_code(raw_code)
    result = property_store.lookup_property(normalized)
    if not result and '_' not in normalized:
        # Try inserting underscore after QH prefix
        alt = normalized[:2] + '_' + normalized[2:]
        result = property_store.lookup_property(alt)
    return result
```

**Rule:** When a property-code format evolves (new URL-derived codes, different prefix structure), the router regex MUST match ALL formats in the sheet. Audit the sheet for code formats BEFORE writing the regex. Case-insensitive input with uppercase normalization before sheet lookup — users type `qh_9njnf0` but the sheet has `QH_9NJNF0`. Always cross-reference codes typed without underscores against the underscored version in the sheet.

### Pitfall: Context-Aware LLM Fallback for Empty Replies

**Root cause:** When the LLM returns `None` or empty string (Ollama rate-limit cutoff, timeout, model error), the writer returns an empty reply to the user. The existing pitfall about "Empty content from 200 OK" says "fall back to router template, not retry" — but a static template fallback is itself a quality regression. The bot goes from natural, context-aware replies to a canned template with no reference to what the user just said.

**Fix — generate fallback from router decision data, not a static string:**
```python
async def write_reply(decision: RouterDecision, message: str, session) -> str:
    prompt = build_prompt(decision, message, session)
    result = await llm.call(prompt)
    
    if not result.content or len(result.content.strip()) < 5:
        # LLM returned empty — generate context-aware fallback from
        # the router's decision data, NOT a static template
        fallback = _context_aware_fallback(decision, session)
        return fallback  # still passes through guards
    
    return result.content

def _context_aware_fallback(decision: RouterDecision, session) -> str:
    """Build a reply from the router's decision when LLM fails."""
    intent = decision.intent
    prop = decision.property_data  # may be None
    
    if intent == 'show_property' and prop:
        return (f"{prop['area']} with {prop['beds']} beds, {prop['baths']} baths, "
                f"{prop['sqft']} sqft for ${prop['price']:,.0f}. "
                f"Want to see more like this one?")
    elif intent == 'ask_for_code':
        return "Do you have a property code from the Instagram post? It starts with QH."
    elif intent == 'lead_intent':
        return "Drop your details in this form and we'll get you started: " + FORM_URL
    elif intent == 'info_question':
        return ("I cover the Greater Houston area including Katy, Cypress, and Spring. "
                "What area are you looking in?")
    else:
        return "I'm Quan's assistant — what can I help you with?"
```

**Rule:** The LLM fallback should use the SAME data the router already computed (intent, property data, next-step hint). This produces a reply that's relevant to the user's message even when the LLM fails. A static "I'm having trouble, please try again" fallback is a dead end. The router decision is the fallback's data source — it already knows what the bot was trying to say.

### Pitfall: LEAD_INTENT vs TOUR_REQUEST — Don't Canned-Template All Lead Signals

**Root cause:** When the router detects lead intent (user wants to talk to Quan, schedule something, or move forward), the writer gives every lead signal the same canned response: a Calendly or form link. But there's a meaningful difference between "I want to schedule a tour" (deterministic — just give the link) and "I'm interested but have questions about the process" (needs LLM to craft a warm, varied response that acknowledges what they said).

**Fix — split TOUR_REQUEST (deterministic) from LEAD_INTENT (LLM with richer hint):**
```python
# TOUR_REQUEST — user explicitly wants to see a property or book a tour
# → deterministic short-circuit, canned tour link, no LLM needed
SHORT_CIRCUIT_REPLIES = {
    "tour_request": "Let's get you on the schedule — pick a time that works: {calendly_url}",
}

# LEAD_INTENT — user signals interest but hasn't explicitly asked for a tour
# → LLM with a richer hint that includes router context
TEMPLATES["lead_intent"] = (
    "User said: \"{message}\". They've shown interest in buying or learning more. "
    "Intent hint: {intent_hint}. Property context: {property_context}. "
    "Respond warmly in 1-2 sentences. Acknowledge what they said, then suggest "
    "a next step (form link: {form_url}, or offer a call). Under 50 words. "
    "Sound like a helpful friend, not a sales rep."
)
```

**Rule:** Not all lead signals are the same. "Can I tour this house?" → give the link (deterministic). "I'm interested but need to think about it" → LLM crafts a warm, varied response that acknowledges their hesitation. Split deterministic lead actions (explicit tour/call requests) from creative lead actions (soft interest, process questions) so the bot doesn't sound like a form-dispensing machine.

### 4 Known Edge Cases (from 193-turn stress test, 2026-06-19)

These were identified but not yet fixed in the router:

1. **"it does have the code"** → routes to push_to_form (should ask for code — user says they HAVE it, just needs to find/send it)
2. **"interested same house you have posted"** → routes to push_to_form (should ask for code — property reference without code)
3. **"Ok"** → routes to push_to_form (should be soft acknowledgment, stay in current state — not push form on a simple "ok")
4. **"test ping"** → routes to push_to_form (spam/test messages should not trigger form push — add a spam/test filter)

These are priority tuning items for the next router iteration. The pattern: the router is too eager to push_to_form on short/ambiguous messages. Acknowledgments and spam need their own tier before the form-push fallback.

### Pitfall: Buyer Intent Routed to Code Gate Instead of Form

**Root cause:** When a user says "I want to buy a house" or "I'm looking to buy
my first home," the router detects buying intent but routes to `ASK_FOR_CODE` —
demanding a property code from someone who hasn't even seen a property yet.
This is a category error: the user is expressing purchase intent, not asking
about a specific listing. 57% of engaged users never provide a code — routing
buyer-intent messages to the code gate wastes the highest-intent conversations.

**Fix — buyer intent → SEND_FORM immediately, never ASK_FOR_CODE:**
```python
BUYER_INTENT_RE = re.compile(
    r"\b(i\s+want\s+to\s+buy|looking\s+to\s+buy|first\s+time\s+(buyer|homeowner)"
    r"|ready\s+to\s+buy|want\s+(a\s+)?(?:new\s+)?home|buying\s+a\s+(?:house|home))\b",
    re.IGNORECASE,
)

# In router — check BEFORE code-gate tiers:
if BUYER_INTENT_RE.search(msg) and not extract_property_code(msg):
    return Action.SEND_FORM  # Skip code gate entirely
```

**Rule:** Buyer intent messages skip the code gate. The form captures their
requirements (area, budget, timeline) so Quan can match them manually — more
valuable than a code they don't have. This applies to any chatbot where the
gating mechanism assumes the user has already seen a specific listing.

### Pitfall: Inventing Location Data When Sheet Fields Are Empty

**Root cause:** When a user asks "what area is QH232 in?" and the Google Sheet
has an empty `area_city` field, the LLM fabricates a location (e.g., "Katy, TX")
based on the bot's general service area. The user then makes plans based on a
fabricated location. Same for zip code requests — the LLM invents a plausible
zip code for the area.

**Fix — three rules for missing data:**
1. **Missing area/city:** Bot says "Quan hasn't publicly shared the location
   for this property yet" and offers the form link. Never invent or guess.
2. **Zip code requests:** Same path — form link. Never fabricate zip codes,
   even if the bot knows the general area.
3. **Garage default:** Use "2" (standard 2-car for TX new construction) when
   the field is empty — this is a safe default, NOT a fabrication.

**Rule:** When the data source has empty fields for user-facing attributes
(location, zip, price), the bot must acknowledge the gap and route to the form
— never fabricate. The LLM's tendency to "helpfully fill in" missing data is a
bug. Only use defaults for non-location attributes where a standard value
exists (e.g., garage=2 for TX new construction).

### Pitfall: Property Data Re-Attachment for Follow-Up Questions

**Root cause:** User looks up QH001 → sees property card → asks "what area is this in?" The router
treats this as a new question (LOCATION_QUESTION intent) but has no property data in scope because
the lookup happened on the PREVIOUS turn. The router pushes to form or says "Quan hasn't shared
that yet" — even though the data was fetched one turn ago and is still in session state.

**This is the #1 cause of "the bot contradicts itself" symptoms.** The bot shows property data on
turn 1, then on turn 2 says it doesn't have that same data. Users lose trust immediately.

**Fix — track `last_property_code` and re-attach property_data on follow-up intents:**

```python
# server.py — UserSession tracks last property code
@dataclass
class UserSession:
    subscriber_id: str
    state: str = "NEW"
    code_ask_count: int = 0
    last_property_code: str = None  # ← NEW

# In the webhook handler, after router returns a decision:
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
# router.py — decide() re-fetches property data for follow-up intents
def decide(prior_state, message, code_ask_count=0, last_property_code=None):
    intent = classify(message, prior_state)
    
    # Follow-up intents that need previously-fetched property data:
    FOLLOWUP_INTENTS = {
        Intent.LOCATION_QUESTION, Intent.PRICE_QUESTION,
        Intent.MORTGAGE, Intent.SCHOOL_ZONE, Intent.COMPARE,
        Intent.WHAT_ABOUT
    }
    
    if intent in FOLLOWUP_INTENTS and last_property_code:
        prop = property_store.lookup_property(last_property_code)
        if prop:
            decision.property_data = prop
            decision.property_code = last_property_code
            # DON'T push to form — answer from the data
            decision.action = Action.REPLY_VOICE
            decision.needs_llm = True
```

**Writer must be told to USE the data, not refuse it:**

```python
# writer.py — SYSTEM_PROMPT must include:
# "When PROPERTY DATA is provided in the decision, answer USING that data.
#  Do NOT say 'I can't share that' or 'Quan hasn't shared that' when the
#  answer is in the property_data dict. Read the dict and answer directly."

# _llm_fallback for price/location questions should read from dict:
def _llm_fallback(decision):
    prop = decision.property_data
    if not prop:
        return None
    if decision.intent == Intent.PRICE_QUESTION:
        return f"This one starts at ${prop['price']:,.0f}."
    if decision.intent == Intent.LOCATION_QUESTION:
        return f"It's in {prop['area']}. Want to see more like this?"
```

**Rule:** Any follow-up question about a previously-shown property MUST re-attach the property
data from the prior turn. The router is stateless — the session (server.py) must pass
`last_property_code` so the router can re-fetch and include `property_data` in the decision.
The writer must be explicitly instructed to answer from the dict, not refuse the data. This
fixes the "bot shows data then says it doesn't have data" contradiction pattern.

### Pitfall: `fetch_similar()` — 3-Pass Property Matching for "Show Me More"

**Problem:** When a user asks "what else do you have?" or "show me more like this," the bot
needs to find similar properties. A naive approach fetches ALL properties and filters — slow
and unfocused. The production `sheets.py` uses a 3-pass narrowing strategy that should be
ported to any sandbox framework.

**Solution — 3-pass matching, ported from PROD `sheets.py`:**

```python
def fetch_similar(code: str, all_properties: list[dict]) -> list[dict]:
    """Find similar properties using 3-pass narrowing.
    Each pass widens the criteria if the previous pass returned too few."""
    target = lookup_property(code)
    if not target:
        return []
    
    # Pass 1: same area + same beds + tight price range (±$50k)
    matches = [
        p for p in all_properties
        if p['code'] != code
        and p.get('area') == target.get('area')
        and p.get('beds') == target.get('beds')
        and abs(_price(p) - _price(target)) <= 50000
    ]
    if len(matches) >= 3:
        return _dedupe_siblings(matches, code)
    
    # Pass 2: same area + same beds + loose price range (±$100k)
    matches = [
        p for p in all_properties
        if p['code'] != code
        and p.get('area') == target.get('area')
        and p.get('beds') == target.get('beds')
        and abs(_price(p) - _price(target)) <= 100000
    ]
    if len(matches) >= 3:
        return _dedupe_siblings(matches, code)
    
    # Pass 3: same area only (any beds, any price)
    matches = [
        p for p in all_properties
        if p['code'] != code
        and p.get('area') == target.get('area')
    ]
    return _dedupe_siblings(matches, code)
```

**Key details:**
- Dedupes sibling codes (same property posted on different reels gets different QH codes —
  keep only one per address/area+beds+price combo).
- 3-pass narrowing ensures at least a few results without being irrelevant.
- Ported directly from production `src/integrations/sheets.py` — keep the two in sync.

**Rule:** "Show me more" is not a form push — it's a property lookup with relaxed matching.
Use 3-pass narrowing (tight → loose → area-only) to find similar listings. Dedupe siblings
so the user doesn't see the same house twice.

### Pitfall: Multi-Code Back-Referencing — "How Much Was the First One?"

**Problem:** User asks about QH001, then QH017, then asks "how much was the first one?"
`last_property_code` only stores ONE code, so the bot can't answer — it doesn't have
QH001's data anymore. This is a context-window issue, not a retrieval issue.

**Current state (partial fix):** `last_property_code` (single string) handles the common
case of "what area is THIS one in?" — follow-up questions about the most-recently-viewed
property. This covers ~90% of real conversations.

**Full fix (not yet implemented):** Store a small dict `{code: property_data}` instead of
a single code:

```python
@dataclass
class UserSession:
    # ...
    viewed_properties: dict[str, dict] = field(default_factory=dict)
    # { "QH001": {area, beds, baths, price, ...}, "QH017": {...} }

# In webhook handler:
if decision.property_code and decision.property_data:
    session.viewed_properties[decision.property_code] = decision.property_data

# In router, for back-reference questions:
if intent == Intent.REFERENCE_PRIOR and "first" in message.lower():
    # Find the first property the user viewed
    first_code = list(session.viewed_properties.keys())[0]
    prop = session.viewed_properties.get(first_code)
```

**Rule:** Single-code tracking (`last_property_code`) handles the common case. For multi-code
conversations (user browses 3+ properties), upgrade to a viewed-properties dict. This is a
context-window enhancement, not a router architecture change.

### Pitfall: 3-Voice Critique Discipline on Every Framework Change

**Root cause:** Framework changes pass synthetic stress tests, ship to prod, and break under real user load — not because the code was wrong, but because no one asked the right questions BEFORE shipping. The framework author's blind spots are: missing failure modes in their own design, scale cliffs they didn't test, and metrics that LOOK good but measure the wrong thing.

**Fix — three voices on every design decision, every report, every ship:**

1. **Devil's Advocate — what proves this wrong?**
   - Run through the strongest counter-arguments. "If this were wrong, what would I see?"
   - Question every headline metric. "0% fabrication — but did the test ever ask for URLs?"
   - "Coherent after scrub" — coherent to whom? A regex pass? A human reader?

2. **Systems Expert — what breaks at scale?**
   - p95 8s fits ManyChat's 10s window — but p99 WILL spike. What's the failure mode?
   - 13% flake rate × 1000 turns/day = 130 user-visible failures. Is that acceptable?
   - Voice drift compounds: 1.5%/turn × 30 turns = 45% drift by conversation end.

3. **Critique Expert — what are the headline metrics hiding?**
   - Voice score 0.78 vs prod — quantifiably different, but is it VISIBLE to humans?
   - Sample bias: did the test pick easy cases or hard cases?
   - Circular metrics: "voice score matches reference" when the reference IS the model's output.

**Rule:** Make these voices a discipline, not an afterthought. Run them BEFORE writing code (do we even need this?), DURING implementation (what's the scale cliff?), and BEFORE shipping (what's the metric hiding?). The 3 voices are how you avoid the "passes every test, breaks in prod" pattern.
- `references/shadow-mode-replay-pattern.md` — when stress tests are too clean. Replays REAL prod conversations turn-by-turn against the new framework (log-only, never send). Catches per-state bugs, voice drift across turns, latency tails, and Ollama rate-limit behavior that mock data misses. Includes the 3-voice critique rubric (Devil's Advocate / Systems Expert / Critique Expert) that every shadow report must pass before being shown to the user.

## Testing

```python
# Router tests — no LLM needed
def test_property_code_detection():
    assert decide_action("QH282", State.NEW) == Action.SHOW_PROPERTY
    assert decide_action("QH009", State.QUALIFYING) == Action.SHOW_PROPERTY

def test_schedule_intent():
    assert decide_action("let's schedule a call", State.QUALIFYING) == Action.SEND_CALENDLY
    assert decide_action("call me tomorrow", State.PROPERTY_SHOWN) == Action.SEND_CALENDLY
Users want to QA the bot from their browser as if they were a real subscriber — not via curl. Build and serve a standalone test chat page wired to the production webhook endpoint.

### Architecture

```
Browser → GET /test-chat → FastAPI → test-ui/index.html (self-contained)
Browser → POST /webhook/quanbot-v30 → FastAPI → brain.py → reply
```

### 1. Create `test-ui/index.html`

Self-contained HTML file (no build step) with:
- DM-style chat interface (dark theme, left/right bubbles)
- Editable **Subscriber ID** field (to simulate new vs returning users)
- **NEW SESSION** button appends timestamp to current ID, resets chat
- **CLEAR** button wipes chat
- **RAW** toggle to show/hide JSON payloads below each bot reply
- Auto-focus input field, Enter-to-send
- Mobile-responsive layout

Key design: the JavaScript `fetch()` POSTs directly to the production webhook endpoint with a `subscriber_id` payload. The bot can't tell it's a browser vs ManyChat because the payload shape is identical.

### 2. Add FastAPI route

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

TEST_UI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test-ui", "index.html")

@app.get("/test-chat", response_class=HTMLResponse)
async def test_chat_ui():
    if os.path.exists(TEST_UI_PATH):
        with open(TEST_UI_PATH, encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h1>Test UI not found</h1>", status_code=404)
```

> **CORS:** When the UI is served from the same origin (same domain/port), CORS is not needed. When served cross-origin (e.g., local file → localhost), add `allow_origins=["*"]` to `CORSMiddleware` during development.

### 3. Expose via Cloudflare Tunnel (so user tests from phone/browser anywhere)

```bash
# Get WSL2 IP (changes per boot)
WSL_IP=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
# Verify from Docker network before adding route:
docker run --rm --network n8n-deploy_default alpine:latest \
  sh -c "apk add curl \u0026\u0026 curl --connect-timeout 5 http://$WSL_IP:8002/health"
```

Add route to `/mnt/c/Users/steve/n8n-deploy/data/cloudflared/config.yml`:
```yaml
  - hostname: v3-test.quann.homes
    service: http://172.27.155.109:8002
```

```bash
# Add DNS + restart
docker exec cloudflared /usr/local/bin/cloudflared tunnel route dns n8n-tunnel v3-test.quann.homes
docker restart cloudflared
```

### Pitfall: Cloudflare Caches Static Assets

When you update `index.html` and redeploy, the browser may still show the old version because Cloudflare edge caches `.html` and `.js` aggressively.

**Fix:** Add cache-busting headers in the FastAPI response.

### Pitfall: The "Three-Layer Staleness" Trap (Browser shows old behavior even though curl passes)

You edit a `.py` file, run `curl` against the webhook, and it returns the new text. You open the browser test UI, type the same message, and get the **old** reply. Most people suspect the browser first, but the real culprits are three layers deep:

| Layer | Symptom | Fix |
|-------|---------|-----|
| **Browser cache** of `index.html` | UI code is old (stale JS/page structure) | Hard refresh (Ctrl+Shift+R), or add `no-store` cache headers in FastAPI |
| **Python `__pycache__`** + **in-memory module** | `curl` passes (hits a freshly-restarted worker) but the systemd service still holds old compiled bytecode | `find . -type d -name __pycache__ -exec rm -rf {} +` **AND** `sudo systemctl restart <service>` |
| **SQLite session DB** | Returning user (`test_user_001`) has persisted state that short-circuits the new greeting logic (already `QUALIFYING`, so greeting → `ANSWER_NATURALLY`) | `rm data/sessions.db` (dev only) or use a fresh subscriber ID |

**Real scenario from this session:**
1. Updated `templater.py` → `__pycache__` still held old compiled version
2. Restarted systemd service → worker picked up new code
3. `curl` with a fresh `subscriber_id` passed — new greeting returned
4. Browser test UI used `subscriber_id = "test_user_001"` from its `<input>` default
5. That ID had `state = QUALIFYING` in `sessions.db`, so greeting hit `ANSWER_NATURALLY` path instead of `INTRO_QUALIFY` 
6. Result: browser showed the old generic "How can I help you?" while `curl` showed the new greeting

**One-shot clearance command (dev):**
```bash
cd /home/steve/quanbot-v3 \
  && find . -type d -name __pycache__ -exec rm -rf {} + \
  && rm -f data/sessions.db \
  && sudo systemctl restart quanbot-v3 \
  && sleep 2 \
  && curl -s http://localhost:8002/health
```

**Rule:** After any code change that affects routing logic or templates, always clear `__pycache__` + sessions DB + restart. FastAPI `--reload` only watches file changes; it does not invalidate compiled bytecode caches in running workers or wipe persisted SQLite sessions.
```python
from fastapi.responses import Response
# Instead of HTMLResponse
return Response(
    content=html_content,
    media_type="text/html",
    headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
)
```

URL query param cache-busting (`?v=2`) is unreliable — Cloudflare may ignore query params.

## Deployment Pattern

- **v1 on port 8000** (production, untouched)
- **v2 on port 8001** (development, new architecture)
- **v3 on port 8002** (new features, branching property flows)
- Test endpoint: `POST /webhook/quanbot-v30` — returns `{"response": "..."}`
- Health check: `GET /health` → `{"status": "healthy", "service": "QuanBot v3", "version": "3.0.0"}`
- Run: `python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload`
- **Live domain (`quanbot.quann.homes`) stays on v2 until explicit cutover.**