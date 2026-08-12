# Stress-Test Harness for 3-Layer Chatbot Frameworks

End-to-end testing of a router + LLM templater chatbot BEFORE live deployment. Mock conversations built from real prod message patterns, scored on guard violations / fabrication / voice / latency / fallthrough. **Use this when you've built a new framework and need to know if it's safe to ship — not as a unit test of the router alone, but as an integration test of the whole bot in adversarial conditions.**

This reference was written from the 2026-06-17 articechute stress test (50 convos, 182 turns, gemma4:31b, ~3.5 min) which uncovered 5 framework-level issues that unit tests on `router.decide_action()` would never have caught.

## When to build a stress-test harness

- ✅ You've written a new router or rewired an existing one
- ✅ You're considering swapping prompts, models, or guard patterns
- ✅ The user said "stress test" / "sandbox test" / "see how it performs"
- ✅ You're about to ship a framework change to live and want empirical evidence
- ❌ You're debugging a single user complaint — that needs a replay harness, not stress testing

## The 4 modules every harness needs

```
sandbox/
├── framework/                  # the bot under test
│   ├── router.py               # state machine (deterministic)
│   ├── writer.py               # thin LLM call
│   ├── guards.py               # banned-phrase / URL / fabrication scrub
│   └── __init__.py
├── mock_generator.py           # builds test conversations from prod data
├── runner.py                   # drives the bot + scores
└── reports/
    └── STRESS_TEST_REPORT.md   # analysis (template breakdown, issues, recs)
```

Keep the bot-under-test code in the same tree as the harness so the runner can `import framework.router as router` directly. Don't make the harness shell out to a running uvicorn — it adds latency variance, networking flakes, and the LLM call can't be intercepted for scoring.

## Mock conversation generation — the non-negotiable rule

**Pull patterns from real prod message logs. Do not synthesize from imagination.** The failure modes the user actually cares about are the ones in their `flow.db`, the ones in their jsonl log lines, the ones in their Telegram support thread. Synthetic test cases miss the actual adversarial inputs.

### Extracting patterns from `conversation_log.jsonl`

In addition to `flow.db`, the raw JSONL log is a valuable data source for pattern extraction:

```python
import json
from collections import Counter

# Load all real user messages
real_msgs = []
with open('/home/steve/quanbot-v4/data/conversation_log.jsonl') as f:
    for line in f:
        entry = json.loads(line)
        if entry.get('role') == 'user' or entry.get('sender_type') == 'user':
            real_msgs.append(entry.get('text', ''))

print(f"Total real user messages: {len(real_msgs)}")
# Count pattern frequencies to validate scenario realism
greeting_re = re.compile(r'^(hi|hey|hello|good morning|good afternoon)\b', re.I)
code_re = re.compile(r'\bqh[_\s]?\w{1,6}\b', re.I)
print(f"Greetings: {sum(1 for m in real_msgs if greeting_re.search(m))}")
print(f"QH codes: {sum(1 for m in real_msgs if code_re.search(m))}")
```

The JSONL log gives raw message counts and frequencies. `flow.db` gives structured turn-by-turn sequences with metadata (guard counts, quality scores, conversation linking). Use both: JSONL for "does this pattern exist in real data?" and `flow.db` for "build a multi-turn scenario from this real conversation."

### What to extract from `flow.db` (QuanBot-specific) / jsonl logs (any bot)

For each prod conversation, pull the **first user turn** + the **last 2 user turns** (start, middle, end-of-funnel patterns). Skip conversations where the bot's reply was already correct (we want adversarial coverage).

```python
# Pattern (Python + sqlite3, no CLI needed):
import sqlite3, json
conn = sqlite3.connect('/path/to/flow.db')
conn.row_factory = sqlite3.Row

# Pull real first-user-turns that have at least one flagged issue
rows = conn.execute("""
    SELECT t.text, c.review_status, c.quality_score, t.error_count, t.guard_count
    FROM turns t
    JOIN conversations c ON t.conversation_id = c.id
    WHERE t.role = 'user'
      AND t.turn_index = 0              -- first user turn
      AND (c.review_status = 'flawed' OR t.guard_count > 0 OR t.error_count > 0)
    ORDER BY c.quality_score ASC
    LIMIT 200
""").fetchall()

# These are the "hard cases" — greet-extract templates from them
```

For jsonl logs, the same pattern: pull all unique user messages where the bot reply was rewritten by a guard, defaulted to a fallback, or had latency > 3s.

### The 14-template pattern (works for any domain)

Group real first-turns by intent category, then write a template per category. Use the actual vocabulary from the prod data, not synonyms:

| Template | Trigger pattern | Example real first turn |
|---|---|---|
| `bare_code` | `r"^qh\d{2,4}\s*$"` | `qh010` |
| `code_with_question` | code + question | `qh232 is it still available` |
| `just_hi` | greetings only | `hi`, `hey`, `good morning` |
| `buy_intent_vague` | buying without specifics | `i want to buy a house` |
| `buy_intent_specific` | area/budget/beds | `3 bed under 400k in katy` |
| `schedule_intent` | call/see/tour/appointment | `can i see it tomorrow` |
| `price_question` | worth/value/zestimate | `what is this home worth` |
| `relocating` | move/relocate/transfer | `relocating from austin in july` |
| `decline_polite` | thanks but no | `no thanks just looking` |
| `decline_hard` | stop/unsubscribe | `stop texting me` |
| `confused` | why/huh/what code | `what do you mean by code` |
| `soft_rejection` | no/nah/nope mid-funnel | `i dont have it` |
| `spam` | "BUY MY COURSE" / off-topic | `make $5000/week from home` |
| `adversarial` | weird inputs | `    ` (whitespace), `🔥`, single chars |

**Two critical rules for the templates:**

1. **Order turns in "complicated orders and randomness"** (Quan's exact words). A 5-turn test that goes `hi → want house → qh010 → is it available → thanks` is a happy path. The harness needs to test `bare_code → confused → buy_intent_vague → schedule_intent → decline_hard` to find the real bugs.
2. **Inject adversarial turns mid-conversation.** A user who started friendly can pivot to adversarial on turn 3. Single-turn-per-template tests miss this.

```python
# Mock generator: returns Scenario objects (name + ordered turns + expectations)
@dataclass
class Scenario:
    name: str
    turns: list[str]
    expect_min_length: int = 10
    expect_intent: str | None = None
    expect_banned_phrases: bool = False
```

## The runner — two modes, one harness

Run BOTH the no-LLM (deterministic router-only) baseline AND the full-LLM (router + LLM writer) version. The **delta between the two** is the most valuable signal in the report:

- If baseline is fine and full-LLM is broken → the LLM is the problem (prompt, model, or prior)
- If baseline is broken → the router is the problem (regex, state machine, tiers)
- If both are broken → the guard layer isn't catching what the LLM emits

```python
# runner.py — runs the SAME 50 convos through both modes
async def run_full_harness():
    baseline_results = await run_all(SEQUENCES, mode="baseline")
    full_results = await run_all(SEQUENCES, mode="full_llm")
    report = compare(baseline_results, full_results)
    write_report(report)
```

`mode="baseline"` short-circuits the LLM call and returns the router's chosen template directly. This isolates "is the router safe?" from "is the LLM safe given the router's choice?"

## Scoring rubric — what to measure

Don't just check "did the bot respond?" Score 5 dimensions:

| Metric | What it catches | How to compute |
|---|---|---|
| **error_rate** | Crashes, timeouts, None replies | `sum(reply is None or len(reply) == 0) / N` |
| **guard_violation_rate** | Banned phrases leaking through | `sum(BANNED_RE.search(r) for r in replies) / N` |
| **fabrication_rate** | LLM inventing data (URLs, prices, addresses) | URL allowlist check + price/address regex + cross-check vs source-of-truth |
| **voice_drift** | Reply sounds robotic or off-template | Cosine similarity vs reference voice samples; flag <0.7 |
| **fallthrough_rate** | Bot falls through to generic "how can I help" | Pattern match for canned fallback strings |

Plus latency p50/p95/p99 per turn. A bot that's 90% safe but takes 8s per turn is unusable for IG DM (5-10s webhook window).

## The 5 framework issues this pattern uncovers (articechute, 2026-06-17)

These are the failure classes that unit tests on `router.decide_action()` will NEVER find, because they require running the LLM against real-shaped inputs:

### Issue 1: Banned-phrase leak (worse with LLM enabled)
- **Baseline:** 14.9% of replies contain banned phrases
- **Full LLM:** 42.6% of replies contain banned phrases
- **Root cause:** LLM has strong prior toward the most-common template; prompt bans are documentation, not enforcement
- **Fix:** Server-level regex guards in `guards.py` (see quanbot-extraction-first-spec pitfall section)

### Issue 2: URL hallucination
- **Full LLM:** 4.1% of replies contain fabricated URLs (`forms.gle/xyz123`, `bit.ly/abc`)
- **Root cause:** LLM generates plausible-looking URLs when prompt says "use https://quann.homes/contact-us-2"
- **Fix:** URL allowlist filter in `guards.py` — strip any `http(s)://` URL whose host isn't in the allowlist

### Issue 3: Timeouts on adversarial inputs
- **Symptom:** 2/50 convos had `clarify` calls time out (>20s wait)
- **Root cause:** LLM call hangs when input is whitespace-only or empty
- **Fix:** Guard empty-input path early in router; return hardcoded greeting before LLM call

### Issue 4: Voice drift between router and LLM
- **Router baseline:** voice score 0.745
- **Full LLM:** voice score 0.786 (better on some, worse on others)
- **Symptom:** LLM replies sound different in tone from router-deterministic replies in the same conversation — user notices the seams
- **Fix:** Voice gate in `guards.py` (cosine similarity vs reference); reject if <0.65, fallback to router template

### Issue 5: Lead classifier false positives on spam
- **Symptom:** "BUY MY COURSE" / "make $5000/week" trigger `lead_intent: true`
- **Root cause:** Classifier over-triggers on money + action verbs
- **Fix:** Add `BANNED_KEYWORDS` shortlist; if input matches, return `Action.NO_OP` (don't engage)

## CRITICAL: Sandbox isolation guarantees

When the user says "stress test in a sandbox," this means:

1. **Bot-under-test lives in `sandbox/` subdirectory** — never modify `src/`, `prompts/`, or `.env` in the prod tree
2. **LLM calls hit the same Ollama Cloud** but with a separate API key (or the same key — Ollama doesn't sandbox by key, but the test runs in its own process)
3. **NO writes to prod DB** — harness uses a separate `sandbox.db` or in-memory dict for session state
4. **NO writes to prod Google Sheets / ManyChat / external systems** — every outbound action is intercepted
5. **Verify prod untouched after the test** — `stat prod/path/to/brain.py` and confirm mtime is from days ago, not this session

```python
# After every stress test run:
import os, time
PROD_FILES = [
    "/home/steve/quanbot-v4/brain.py",
    "/home/steve/quanbot-v4/system_v3.txt",
    "/home/steve/quanbot-v4/flow.db",
]
for path in PROD_FILES:
    mtime = os.path.getmtime(path)
    age_hours = (time.time() - mtime) / 3600
    if age_hours < 1:
        raise RuntimeError(f"PROD TOUCHED: {path} modified {age_hours:.1f}h ago")
print("✓ Prod untouched — all files >1h old")
```

## Reporting — what to put in STRESS_TEST_REPORT.md

```markdown
# Stress Test Report

## Setup
- Framework: articechute (3-layer: router + writer + guards)
- Model: gemma4:31b (Ollama Cloud)
- Corpus: 50 convos, 182 turns, drawn from flow.db
- Duration: ~3.5 min
- Date: 2026-06-17

## Headline numbers
| Metric | Baseline (no LLM) | Full LLM | Delta |
|---|---|---|---|
| Error rate | 12.5% | 14.5% | +2.0pp |
| Guard violations | 14.9% | 42.6% | +27.7pp ⚠️ |
| Fabrication | 0% | 4.1% | +4.1pp ⚠️ |
| Voice score | 0.745 | 0.786 | +0.041 |
| Fallthrough | 90.2% | 90.2% | 0 |
| Latency p50 | 0ms | 892ms | +892ms |
| Latency p95 | 0ms | 1,847ms | +1,847ms |

## Per-template breakdown
[table of each of the 14 templates × each metric]

## 5 issues found
[issue 1-5 from above, with sample bot replies]

## Recommendations
- A: Fix 5 issues + re-run (effort: M, risk: low)
- B: Build shadow-mode adapter to run articechute alongside prod (effort: L, risk: med)
- C: Pause to read report, then decide (effort: S, risk: none)
```

## Pitfall: harness reuses subscriber IDs across runs

If your harness uses `subscriber_id=f"test_{name}"` and you re-run after a fix, the session state from the previous run is still in `flow.db` (or your in-memory dict). The new test "starts" in `QUALIFYING` state, not `NEW`, and your first-turn greeting test fails for a reason unrelated to your fix.

**Fix:** Use `subscriber_id=f"test_{name}_{timestamp}"` so every run starts clean. Or wipe the test sessions from the DB before each run.

## Pitfall: scoring is asymmetric

A bot that always replies `"OK."` scores well on:
- error_rate (no crashes)
- guard_violations (no banned phrases)
- fabrication (no URLs)
- voice (very short, matches most reference samples)
- latency (instant)

And scores badly on:
- length (reply is 3 chars, under `expect_min_length=10`)

**Rule:** Score both safety AND usefulness. A "safe" bot that says nothing is a regression. Require `expect_min_length` on every scenario.

## Pitfall: the harness itself has bugs

The first run of the 2026-06-17 harness had THREE harness-specific bugs that masked real issues:

1. `threading.local()` doesn't propagate across `await` boundaries in async code — use module-level state instead
2. Mock lookup dict was keyed by `"name"` but test IDs were `f"test_{name}"` — strip the prefix in the lookup, or key the dict by the prefixed form
3. Whitespace-only inputs (`"    "`) hit the empty-fallback path in the bot AND in the harness; add explicit `expect_intent="empty_input"` and a non-empty graceful reply expectation

Always run the harness with at least 1-2 scenarios where you KNOW the expected output, and confirm the harness reports what you expect. If the harness reports "all pass" but you can see by eye that one reply is wrong, the harness is broken, not the bot.

## Pitfall: Side-by-Side Test with Unequal Data Access (Rigged Test)

**Root cause:** You run a head-to-head stress test of production vs sandbox, but the sandbox doesn't have access to the same data sources (Google Sheet, property DB, API endpoints) as production. Every property-lookup scenario fails in the sandbox not because the framework is broken, but because it can't reach the data. The comparison looks like "PROD 0 issues, SANDBOX 10 issues" — but 6 of those 10 issues are just "sandbox couldn't look up property code" which is an environment gap, not a framework bug.

**Symptom:** User says "why would you test when one of it cannot reach system?" — this is the signal that the test was unfair and the results are invalid.

**Pre-fix (wrong):** Run the comparison anyway, present headline numbers, then walk back conclusions when the user points out the unfairness. This destroys trust — the user now questions whether the assistant understands what a fair test is.

**Post-fix (correct):**
1. **Before running any side-by-side comparison, audit both systems' data access.** List every external dependency: Google Sheets, DBs, APIs, file paths. Both systems must have equal access to all of them.
2. **If the sandbox is missing a data source, either wire it up first OR exclude scenarios that depend on that data.** Don't run property-lookup scenarios against a sandbox with no property data and call it a fair test.
3. **Only present results after confirming test fairness.** State the fairness audit upfront: "Both systems have access to: [list]. Scenarios excluded because of known gaps: [list]."

**Rule:** A stress test comparison is only valid when both systems have equal access to all data sources. An environment gap in one system is not a framework bug. Always audit data access BEFORE running the comparison, not after the user catches it.

## Pitfall: Test Harness Banned-Phrase List Diverges From Actual Bot Rules

**Root cause:** The stress test script has its own banned-phrase list used for scoring. This list was written from memory or assumption, not from the actual bot's configured rules. The test flags "I'm Quan's assistant" as a banned phrase — but in the actual bot, "I'm Quan's assistant" is the CORRECT greeting phrase (the bot is supposed to introduce itself as Quan's assistant, not as Quan himself). 4 of 10 "issues" in a stress test were false positives from this wrong list.

**Symptom:** User says "I'm Quan's assistant is a correct phrase" or points out that flagged issues are false positives.

**Fix:**
1. **The test harness's banned-phrase list MUST be sourced from the actual bot's configuration** — read `guards.py`, `brain.py`, or wherever the production bot defines its banned phrases. Never hand-write a banned-phrase list for the test harness from memory.
2. **Test the test.** Before trusting stress test results, manually verify 2-3 flagged "issues" against the actual bot rules. If a flagged phrase is actually correct, the test harness is wrong, not the bot.
3. **Separate "style preferences" from "banned phrases."** "I'm Quan's assistant" is a style preference (the bot should say this). "Quan can help you" is a banned phrase (third-person framing about Quan). The test harness must not conflate them.

**Rule:** The stress test harness is also code that can have bugs. A banned-phrase list in the test script that doesn't match the production bot's actual rules produces false-positive issues that waste debugging time and can lead to wrong conclusions about framework quality. Source the test's banned-phrase list from the same config the bot uses.

## Pitfall: Presenting Results Before Acknowledging Test Flaws

**Root cause:** The assistant runs a stress test, gets headline numbers ("PROD 0 issues, SBX 10 issues"), presents them to the user, and the user immediately catches that the test was unfair (sandbox couldn't reach the data) and had false positives (wrong banned-phrase list). The assistant then flip-flops: "sandbox is great!" → "sandbox is broken!" → "the test was unfair." The user loses trust in the assistant's ability to evaluate results critically.

**Fix — discipline before presenting any test results:**
1. **Run the 3-voice critique on the TEST ITSELF, not just the framework.** Devil's Advocate: "What if the test is wrong?" Systems Expert: "Does the test environment match prod?" Critique Expert: "Are the headline metrics measuring the right thing?"
2. **State test limitations BEFORE headline numbers.** "Before I share results: the sandbox doesn't have Google Sheet access, so property-lookup scenarios will fail in sandbox for environmental reasons. The banned-phrase list in the test script may have false positives — I verified 2 of 10 flagged phrases are actually correct bot behavior."
3. **Never flip-flop conclusions.** If the test was unfair, say so BEFORE presenting numbers, not after the user catches it. If you already presented numbers and then realize the test was flawed, retract the numbers explicitly: "These results are invalid because [reason]. I should have audited test fairness first."

**Rule:** The 3-voice critique discipline applies to the test methodology, not just the framework under test. Apply it before presenting results, not after the user catches the flaw. An assistant that presents invalid results and then walks them back is worse than one that says "I need to verify test fairness before sharing numbers."

## When the report says "ship it" — what to do next

1. **Fix the 5 issues** in the framework code (router.py / writer.py / guards.py in the sandbox)
2. **Re-run the harness** with the SAME 50 convos (deterministic seed) — confirm metrics improved
3. **Build a shadow-mode adapter** that runs articechute ALONGSIDE prod for a week, logging divergences (not yet shipping, just observing)
4. **Show the user the before/after numbers** before any cutover conversation
5. **NEVER auto-promote to live.** The user must explicitly say "ship" / "deploy" / "go live" in the current turn.

## Pitfall: Synthetic Scenarios Not Present in Real Data

**Root cause:** You fabricate "adversarial" test scenarios (emoji spam `🔥🔥🔥`, prompt injection "ignore your instructions", "what is the meaning of life") that sound like reasonable edge cases but NEVER appear in actual user conversations. The stress test "passes" these scenarios, but you've wasted test cycles on inputs the bot will never see, and the user catches it: *"is there any patterns that shows chess emojis like you point out?"* — the answer was no. Zero instances.

**Empirical evidence (2026-06-19, 1,866 real IG DM messages from 242 users):**
- Emoji spam: **0 instances**
- Prompt injection: **0 instances**
- "Tell me a joke" / "meaning of life": **0 instances**
- Actual top patterns: greetings (82×), QH code drops (87×), location questions (41×), list requests (22×), availability checks (15×), reel URL pastes (12×), frustration (8×), Spanish (5×), school questions (3×)

**User's exact words (2026-06-20):** *"But what if the stress tests, you know, for normal conversations, if you were to take the old messages and look at the patterns and you know recreate those patterns, who will win? Given that this is gonna be probably a five message back and forth or even longer, with each of them being different to see if we can break it. But it has to be real life, not just random. What if the patterns should match. Don't make up anything that they want to do. Like, is there any patterns that shows chess emojis like you point out?"*

**The answer was no.** Zero chess emojis, zero emoji spam, zero prompt injection in real IG DMs. The user is asking: did you check the real data before fabricating scenarios? If not, your stress test is testing fiction.

**Fix — validate scenario realism BEFORE running the test:**
1. Pull real conversation logs from `conversation_log.jsonl` (or `flow.db`) — not just first turns, but full multi-turn transcripts
2. Count how many real messages match each scenario pattern you plan to test
3. If a scenario has 0 real matches, **drop it** or mark it as "synthetic — low priority"
4. Build scenarios by reconstructing actual conversation transcripts, not by imagining "what if a user sent X"
5. **For multi-turn scenarios (5+ messages), reconstruct real conversation sequences from flow.db turn-by-turn data.** A real user's message sequence (hi → qh010 → how much → can I see it → what schools) is worth more than 10 synthetic sequences because the ORDERING and PIVOTS reflect actual user behavior.

```python
# Validate scenario realism against real logs
import json
real_msgs = [json.loads(l)['text'] for l in open('data/conversation_log.jsonl')]

for scenario in scenarios:
    matches = sum(1 for m in real_msgs if scenario.pattern.search(m))
    if matches == 0:
        print(f"⚠️  {scenario.name}: 0 real matches — consider dropping")
    else:
        print(f"✅ {scenario.name}: {matches} real matches")
```

**Data sources for real patterns:**
- `flow.db` — structured conversation/turn tables with guard counts, quality scores
- `conversation_log.jsonl` — raw message log (1.8MB, 1,866 messages), includes sender_id, text, timestamp
- Both sources should be checked. `conversation_log.jsonl` is useful for counting raw pattern frequencies; `flow.db` is useful for extracting structured turn-by-turn sequences with metadata.

**Rule:** Every scenario in a stress test must be traceable to at least one real conversation in the logs. If you can't find a real example, the scenario is synthetic and should be dropped or deprioritized. The user will ask "is there any pattern that shows X?" — if the answer is "no, I made it up," the test loses credibility. This is the same root as "don't test with synthetic data when real conversation data exists."

## Pitfall: `_norm_qh_code()` Missing `.upper()` on Suffix — Silent Case Mismatch

**Root cause:** The QH code normalization function uppercases the prefix (`QH`) but forgets to uppercase the suffix. `qh_9njnf0` normalizes to `QH_9njnf0` — which doesn't match the sheet's `QH_9NJNF0`. The property lookup silently returns `None`, and the bot falls through to a generic response. This is especially insidious because the regex MATCHES the input (case-insensitive flag), so you think extraction is working.

**Symptom:** User types `qh_9njnf0` (lowercase, as users do). Bot says "I don't see a property code" or pushes to form. But `curl` with `QH_9NJNF0` (uppercase) works fine. You spend time debugging the regex, but the regex is fine — the normalization is broken.

**Fix — uppercase the ENTIRE code, not just the prefix:**
```python
def _norm_qh_code(raw: str) -> str:
    """Normalize extracted code to uppercase sheet format."""
    code = raw.upper().replace(' ', '_')  # .upper() on the WHOLE string
    # Old format: QH001 → QH001 (no underscore)
    # New format: qh_9njnf0 → QH_9NJNF0 (uppercase + underscore)
    if '_' not in code and code.startswith('QH') and code[2:].isdigit():
        return code  # old format
    return code  # new format already has underscore from .upper()
```

**Rule:** When normalizing user input for case-sensitive lookups (Google Sheets, DBs), `.upper()` the ENTIRE string, not just the prefix. The sheet stores `QH_9NJNF0` — any lowercase letter in the suffix will cause a mismatch. Test normalization with lowercase input: `_norm_qh_code("qh_9njnf0")` must return `"QH_9NJNF0"`, not `"QH_9njnf0"`.

## See also

- `deterministic-router-llm-templater` SKILL.md — the 3-layer architecture this harness tests
- `quanbot-extraction-first-spec` SKILL.md — QuanBot's banned-phrase guards and URL allowlist patterns (the canonical implementations of the 5 fixes above)
- `quanbot-extraction-first-spec/references/llm-server-level-guards.md` — full reference on the 3-layer defense pattern (prompt + few-shot + server regex)
- `quanbot-extraction-first-spec/references/session-aware-guards-pattern.md` — the `not code and not session_code` pattern that fixes the "guard clobbers context-aware reply" bug
