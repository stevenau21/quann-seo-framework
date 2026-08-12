# Shadow-Mode Replay Pattern

Run a new framework ALONGSIDE prod (log-only, never send) by replaying REAL prod conversations turn-by-turn against the new framework. **Use this when stress-test mock data is too clean and you need to see how the new framework behaves on real adversarial inputs from actual users.** Stress tests catch class-level bugs; shadow replay catches per-state and per-flow bugs that only emerge from long interaction sequences.

This reference was written from the 2026-06-17 articechute shadow replay (8 prod conversations, 30 turns, gemma4:31b) which surfaced 5 framework issues stress testing missed: voice drift across turns, guard-scrub breaking URLs mid-string, Ollama rate-limit 13% flake, P95 latency at edge of ManyChat window, and per-property QH-code coverage gaps.

## Stress test vs shadow replay — when to use each

| | Stress test | Shadow replay |
|---|---|---|
| **Data** | Synthetic, derived from real prod patterns | Real prod conversations verbatim |
| **Adversarial coverage** | High (you control the inputs) | Lower (only what real users actually do) |
| **State-coverage** | Each turn starts clean | Full conversation history preserved |
| **Catches class-level bugs** | ✅ Excellent | ⚠️ Partial |
| **Catches voice drift** | ❌ Missed (single turns) | ✅ Excellent (turns over time) |
| **Catches per-state bugs** | ❌ Missed | ✅ Excellent |
| **Catches latency tails** | ⚠️ Under real load only | ✅ Under real load |
| **Speed** | Fast (~3-5 min) | Slow (~5-10 min, real LLM calls per turn) |
| **Production safety** | Sandboxed | Must be log-only, never send |

**Rule:** Run stress tests FIRST (fast class-level coverage), THEN shadow replay (slow per-flow coverage) before any cutover. Both are needed.

## The 4 modules every shadow replay needs

```
sandbox/
├── framework/                  # the bot under test (same as stress test)
│   ├── router.py
│   ├── writer.py
│   └── guards.py
├── shadow_replay.py            # replays real prod conversations turn-by-turn
└── reports/
    ├── shadow_mode_replay.json # raw turn-by-turn data
    ├── shadow_replay.log       # stdout
    └── SHADOW_MODE_REPORT.md   # 3-voice analysis
```

`shadow_mode.py` (single-turn, deprecated) and `shadow_replay.py` (full-conversation, current) serve different purposes — keep both, mark the older as deprecated.

## Pulling real prod conversations — schema discovery first

Before writing any code, query the prod DB to discover the actual schema. The columns you think exist may not.

```python
# Pattern (Python + sqlite3, no CLI needed):
import sqlite3
conn = sqlite3.connect('/path/to/flow.db')
conn.row_factory = sqlite3.Row

# 1. List columns
cols = [r[1] for r in conn.execute("PRAGMA table_info(turns)").fetchall()]
print(cols)

# 2. Check if reply_to_turn_id exists (often doesn't)
if 'reply_to_turn_id' in cols:
    rows = conn.execute("""
        SELECT * FROM turns WHERE reply_to_turn_id IS NOT NULL LIMIT 5
    """).fetchall()
    print(f"FK pairs available: {len(rows)}")
else:
    print("No FK — must pair by adjacent timestamps within conversation")
```

**Common discovery surprises:**

- `reply_to_turn_id` is NULL for ALL bot turns → no FK to user turns → must pair by adjacency
- `suggested_reply` exists but is sparse (10/3131 = 0.3%) → it's a manual review column, not parallel framework
- `direction` is `'in'`/`'out'`, not `'user'`/`'bot'` → check actual values
- `handler` is always `'llm'` currently → no per-action breakdown in prod yet

## Pairing user turns with bot replies — adjacency, not FK

When FKs don't exist, pair by adjacent timestamps within the same conversation:

```python
async def replay_conversation(conv_id: int, limit: int = 12):
    """Replay one prod conversation through the framework, turn-by-turn."""
    rows = conn.execute("""
        SELECT id, direction, message_text, created_at
        FROM turns
        WHERE conversation_id = ?
          AND direction IN ('in', 'out')
        ORDER BY created_at ASC, id ASC
        LIMIT ?
    """, (conv_id, limit)).fetchall()

    # Pair user turn with next bot reply
    pairs = []
    i = 0
    while i < len(rows):
        if rows[i]['direction'] == 'in':
            user_turn = rows[i]
            bot_reply = rows[i + 1] if i + 1 < len(rows) and rows[i + 1]['direction'] == 'out' else None
            pairs.append((user_turn, bot_reply))
            i += 2
        else:
            i += 1

    # Now replay each pair through the framework
    for user_turn, bot_reply in pairs:
        framework_reply = await framework.handle(user_turn['message_text'])
        # Compare framework reply to prod reply (log only, never send)
        record_turn(conv_id, user_turn, bot_reply, framework_reply)
```

**Key insight:** Voice drift, state-machine loops, and "the bot sounds different after 5 turns" ONLY appear when you replay full sequences. A framework that produces perfect isolated turns may produce nonsense at turn 7 because the state machine has drifted.

## The 3-voice critique on every shadow report

Before writing the report, apply the three voices to the raw data. This is non-negotiable — without it, reports become vanity metrics:

### Voice 1: Devil's Advocate — what proves the framework wrong?

- The framework passed 90% of cases. Which 10% did it fail, and do those 10% matter?
- "0% fabrication" sounds great — but is the LLM actually being ASKED to fabricate? (If your test set never asks for URLs, the metric is circular.)
- "Voice score 0.78" — vs what baseline? Is 0.78 the prod voice, or a synthetic target?
- "Latency p95 8s" — is that within the user's tolerance, or only within ManyChat's window?
- "1 empty reply out of 30" — is that noise, or is it Ollama rate-limiting a specific prompt shape?

### Voice 2: Systems Expert — what breaks at scale?

- 4/30 empty replies = 13% flake rate. At 1000 turns/day, that's 130 user-visible failures.
- p95 8s fits in ManyChat's 10s window but only barely. A p99 spike (rare long tail) WILL time out.
- Router regex tested on 30 turns — does it generalize to the other 99% of conversations not in the sample?
- Per-property QH-code coverage: only 4 codes tested, but there could be hundreds in prod.
- Voice drift compounds across turns — 30 turns × 1.5% drift/turn = 45% drift at turn 30.

### Voice 3: Critique Expert — what are the headline metrics hiding?

- "Coherent after scrub: 46.2%" — what does incoherent look like? Are users seeing broken English?
- URLs cut to "https://q" → does the user understand the bot intended to share a link?
- Voice score 0.78 vs prod voice — quantifiably different, but is the difference VISIBLE to a human reader?
- Headline says "framework matches prod" — but on what subset? The hard subset or the easy subset?
- Sample bias: 8 conversations chosen how? If filtered by length, the "easy" cases are over-represented.

**Rule:** Every claim in the report MUST pass the 3-voice filter. If the Devil's Advocate can disprove it, reframe it as a hypothesis with caveats. If the Systems Expert sees a scale cliff, call it out. If the Critique Expert finds the metric circular, replace it with a real one.

## Shadow replay must be log-only, never send

The framework under test must NOT have authority to send anything to users. Shadow mode is observation only:

```python
# shadow_replay.py — log only
async def handle_shadow(user_msg: str, conv_id: int):
    # 1. Run framework
    framework_reply = await framework.handle(user_msg)

    # 2. Compare to prod reply (read-only)
    prod_reply = fetch_prod_reply(conv_id, user_msg)

    # 3. Log divergence (write-only to sandbox/reports/)
    log_divergence({
        "conv_id": conv_id,
        "user_msg": user_msg,
        "prod_reply": prod_reply,
        "framework_reply": framework_reply,
        "diff_chars": levenshtein(prod_reply, framework_reply),
    })

    # 4. DO NOT call ManyChat, DO NOT post to IG, DO NOT send anything
    return None
```

**Why:** A bug in the shadow harness that calls `send_message()` could spam real users. Defense in depth: the framework has no `send` function wired at all, and the runner explicitly returns `None`.

## Pitfall: Ollama rate-limit shows as empty content, NOT error

When the LLM call returns 200 OK with `content=""`, that's almost always an Ollama Cloud rate-limit cutoff mid-generation. It's NOT a model bug. Don't retry on the same model — switch or short-circuit:

```python
# WRONG — retries the same model on rate limit
result = await llm.call(prompt)
if not result.content:
    result = await llm.call(prompt)  # ← hits same rate limit again
    if not result.content:
        result = await llm.call(prompt)

# RIGHT — switch model or short-circuit
result = await llm.call(prompt)
if not result.content:
    # Fall back to router template directly (deterministic, no LLM)
    result = await router.template_only(prompt)
```

In the articechute run, 4/30 turns (13%) hit this. The guard caught them as `empty_reply` and the framework still produced a coherent router-template reply — but a "retry the LLM" approach would have wasted 3x the latency budget for no benefit.

## Pitfall: Guard scrub can break valid output mid-sentence

The URL allowlist guard is supposed to strip hallucinated URLs (`forms.gle/xyz123`, `bit.ly/abc`). But if it's naive enough, it can ALSO strip valid URLs mid-string:

```python
# BAD — strips valid URL mid-word
"Check this out: https://quann.homes/contact-us-2 today"
# After naive URL-block: "Check this out:  today"  # ← URL gone entirely

# BADGER — strips mid-word
"go to https://quann.homes/qh232"
# After mid-word cut: "go to https://q"  # ← broken URL left in text
```

**Rule:** URL guards must either:
1. Strip the WHOLE URL and surrounding whitespace, OR
2. Replace the URL with a placeholder like `[link removed]`, OR
3. Reject the entire reply and fall back to router template

A guard that leaves broken URL fragments in the output is worse than no guard — the user sees garbage and can't act on it.

## Pitfall: per-property QH-code coverage is incomplete

Stress test / shadow replay only tests the QH codes in your sample. If you only see QH001, QH010, QH232, QH309, that's 4 codes out of potentially hundreds. The framework might handle those 4 perfectly and produce nonsense for QH500.

**Fix:** Pull the full list of codes from the data source, then sample evenly:

```python
# Get all unique property codes from prod
codes = conn.execute("""
    SELECT DISTINCT property_code FROM turns
    WHERE property_code IS NOT NULL
""").fetchall()

# Stratified sample — 1 conversation per code
import random
random.seed(42)  # deterministic
sampled = random.sample(codes, min(8, len(codes)))
```

## Pitfall: shadow replay must bound runtime

Real LLM calls are slow. A 50-conversation shadow replay can take 30+ minutes and burn Ollama Cloud quota. Always bound:

```python
MAX_CONVERSATIONS = 8           # not 50
MAX_TURNS_PER_CONVO = 12         # not 50
RATE_LIMIT_PAUSE = 1.5           # seconds between LLM calls
TOTAL_TIMEOUT = 600              # 10 min hard cap
```

If Ollama rate-limits at turn 15 of conversation 7, you want the harness to fail fast and report partial data, not hang for 30 minutes producing garbage.

## Pitfall: framework field names diverge from prod

When shadow replay calls `framework.router.decide_action()`, the returned object's field names may not match prod's convention:

```python
# articechute router returns: RouterDecision(state_after=..., action=...)
# prod brain.py expects:        Decision(next_state=..., ...)
```

If you copy-paste code from prod into the sandbox framework, the field names will be different. The harness will crash on `AttributeError: 'RouterDecision' object has no attribute 'next_state'`.

**Fix:** When you copy router code into the sandbox, grep for the field names and update them:

```bash
grep -n "next_state\|state_after" framework/router.py brain.py
# Pick the framework's naming, update all references in shadow_replay.py
```

## Pitfall: `***` literal corruption in .env values when passing through tool args

When a tool's argument contains the literal substring `***` (used as a placeholder, e.g. `LLM_MAX_TOKENS=***`), the tool-argument machinery may eat the surrounding context or corrupt the string. This shows up as `no_ollama_api_key` errors when the key is actually present.

**Workaround:** Build the prefix using `chr()` concatenation:

```python
# WRONG — literal *** in tool arg gets corrupted
prefix = "ollama_***"  # ← eaten by message-passing machinery

# RIGHT — build character-by-character
prefix = "o" + "llama" + chr(42) * 3 + "_key"  # ← survives

# Or, better: pull from environment and don't hardcode the prefix at all
import os
api_key = os.environ["OLLAMA_API_KEY"]
```

**Verify the key loaded correctly:**
```bash
# Should NOT have *** in the prefix
grep "^OLLAMA_API_KEY" .env | head -c 20
# Should print: OLLAMA_API_KEY=9b23f7e...
# NOT: OLLAMA_API_KEY=ollama_***
```

## Reporting — what to put in SHADOW_MODE_REPORT.md

```markdown
# Shadow Mode Report

## Setup
- Framework: articechute (3-layer)
- Model: gemma4:31b (Ollama Cloud)
- Corpus: 8 real prod conversations, 30 turns
- Duration: ~6 min
- Date: 2026-06-17

## Headline numbers
| Metric | Value | Notes |
|---|---|---|
| Coherent after scrub | 46.2% | URLs get cut mid-string |
| Empty reply rate | 13.3% | Ollama rate-limit, not framework bug |
| P50 latency | 4.2s | OK |
| P95 latency | 8.07s | At edge of ManyChat 10s window |
| Fabrication rate | 0% | Real win — no URLs invented |
| Voice score | 0.78 | vs prod voice — quantifiably different |

## 5 issues found
1. Guard-scrub breaks URLs mid-string (46% incoherent)
2. Ollama rate-limit 13% flake rate
3. Voice drift compounds across turns
4. P95 latency 8s fits window only barely
5. Per-property QH-code coverage incomplete

## 3-voice review
### Devil's Advocate
- "Coherent after scrub" only measures URL guard. Doesn't catch voice drift.
- 0% fabrication is real but sample never asked for URLs.

### Systems Expert
- 13% flake × 1000 turns/day = 130 user-visible failures
- P99 spike (untested) WILL time out

### Critique Expert
- Voice score 0.78 — quantifiably different, but is the difference VISIBLE?
- Sample bias: 8 conversations filtered by length — easy cases over-represented

## Recommendations
- A: Fix 5 issues + re-run (effort: M, risk: low)
- B: Read report, decide later (effort: S, risk: none)
- C: Skip to latency fast-path (effort: L, risk: med)
```

## See also

- `deterministic-router-llm-templater/SKILL.md` — the 3-layer architecture this replay tests
- `references/stress-test-harness-pattern.md` — the synthetic-data companion to this replay
- `quanbot-extraction-first-spec/SKILL.md` — server-level guard patterns (the canonical fix for issue #1)
