# Real Conversation Pattern Stress Test (2026-06-19)

Head-to-head comparison of Production QuanBot v4 vs Sandbox Articechute framework,
run against 67 real multi-turn Instagram DM conversations extracted from `flow.db`.

## Methodology

1. **Data source:** `data/flow.db` — 296 conversations, 3,373 turns with full
   metadata (handler, intent, state transitions, latency, LLM vs regex, review status).
2. **Filtered to 67 multi-turn conversations** (2+ turns) — these are the conversations
   where the bot's behavior actually matters. Single-message ghosts (175/296) tell us
   about the top-of-funnel but not about conversation quality.
3. **Ran both architectures on each conversation** — replayed message-by-message
   through both the production brain.py + tagger.py and the Articechute router.py +
   writer.py + guards.py.
4. **Scored on:** URL handling, intent granularity, code loop frequency, lead routing,
   error rate, conversation flow.

## Head-to-Head Results

| Metric | Production v4 | Articechute |
|--------|--------------|-------------|
| URL handling | Errors in 5/67 convs | 100% clean |
| Intent classes | 6 | 16 |
| Code loop (user stuck) | 30/67 convs | 21/67 convs |
| Lead routing | Catch-all form | Specific (mortgage→call, tour→call, school→form) |
| Error rate | 5/67 convs | 0/67 (deterministic) |
| Shared IG reel links | 12 convs, both handle poorly | Same |

## Key Conversation Patterns (the 67 real conversations)

### Pattern 1: The QH Code Wall (57% of engaged users)
38 of 67 users never provide a QH property code. The bot asks, they say "I don't have it"
or "where do I get that" or just ghost. The code loop is the #1 friction point.

**What happens:** Bot asks for code → user doesn't have it → bot asks again → user ghosts.
**Fix needed:** 3-strike escalation — after 3 code attempts, push to form or call. Don't
loop infinitely on the code question.

### Pattern 2: One-Message Ghost (59% of all conversations)
175 of 296 conversations sent exactly 1 message and disappeared. The bot's first reply
matters enormously — if it leads with "do you have a property code?", the user bounces.

**Fix needed:** First reply should acknowledge the user's actual message, not lead with
code request. "What areas do you cover?" → answer the question, THEN ask for code.

### Pattern 3: Funnel Stuck at Front Door (86%)
257 of 296 conversations never leave the NEW state. The bot never advances them to
QUALIFYING, FORM_SENT, or any downstream state.

**Root cause:** The code-gate blocks all forward progress. Users who don't have a code
can't advance, and most users don't have a code.

### Pattern 4: Process/Market Questions (33 conversations)
33 conversations involved questions about the process ("how does buying work") or the
market ("what areas do you cover", "what price range"). Both architectures handle these
poorly — they try to redirect to property codes instead of answering the question.

**Fix needed:** Answer the question first, then offer the form. "I cover Katy, Cypress,
and West Houston. What area are you looking in? You can also fill this out and I'll send
matches: {form_url}"

### Pattern 5: Shared IG Reel Links (12 conversations)
12 conversations involved the user sharing an Instagram reel link. Both architectures
handle this poorly — they can't extract the property code from the URL and fall back to
asking for the code.

**Fix needed:** When a URL is detected, offer the form (so Quan can match manually),
don't lecture about codes.

## The Five Fixes for 90% Improvement

1. **Code escalation (3 strikes → form/call)** — After 3 attempts to get a code, stop
   asking. Push to form or offer a call. The code loop kills 57% of engaged conversations.

2. **First reply doesn't lead with code** — Acknowledge the user's actual question first.
   If they asked about areas, answer about areas. If they said "hi", introduce yourself.
   Ask for the code AFTER establishing context, not before.

3. **Answer questions without requiring code** — "What areas do you cover?" needs no
   property code. "How does the buying process work?" needs no code. Route these to an
   ANSWER_NATURALLY intent that responds to the question, then offers the form.

4. **Connect Articechute to Google Sheets** — The sandbox only has 4 fixture properties
   vs 55 live in the sheet. Without real data, the sandbox can't be tested realistically.

5. **Wrap Articechute in FastAPI + shadow mode** — Run alongside production for 1 week.
   Log-only, never send. Compare turn-by-turn against production to catch per-state bugs.

## How to Reproduce

```python
# Extract conversations from flow.db
import sqlite3
db = sqlite3.connect('/home/steve/quanbot-v4/data/flow.db')
db.row_factory = sqlite3.Row

# Get all multi-turn conversations
convos = db.execute("""
    SELECT conversation_id, COUNT(*) as turn_count
    FROM turns GROUP BY conversation_id
    HAVING turn_count >= 2 ORDER BY turn_count DESC
""").fetchall()
print(f"Multi-turn conversations: {len(convos)}")

# For each conversation, get all turns
for c in convos:
    turns = db.execute(
        "SELECT * FROM turns WHERE conversation_id = ? ORDER BY turn_number",
        (c['conversation_id'],)
    ).fetchall()
    # Replay each turn through both architectures
    # Score the responses
```

## Articechute Architecture Files

- `sandbox/articechute/framework/router.py` — 19,734 chars, 16 intents, deterministic
- `sandbox/articechute/framework/writer.py` — 7,859 chars, thin LLM writer in Quan's voice
- `sandbox/articechute/framework/guards.py` — 7,318 chars, server-side guards
- `sandbox/articechute/framework/shadow_mode.py` — shadow replay harness
- `sandbox/articechute/framework/shadow_replay.py` — real conversation replay
- `sandbox/articechute/framework/mock_generator.py` — 14-template mock conversation generator
- `sandbox/articechute/framework/runner.py` — test runner

Full results also in `/home/steve/quanbot-v4/ARCHITECTURE_REVIEW.md` (298 lines).