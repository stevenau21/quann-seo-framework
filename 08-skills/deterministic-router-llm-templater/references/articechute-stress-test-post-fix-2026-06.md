# Articechute Stress Test — Post-Fix Results (2026-06-19)

Results of running the Articechute framework against 193 sampled turns
from `flow.db` AFTER all 5 fixes were applied. This is the "after" data
point for the 67-conversation head-to-head documented in
`references/real-conversation-pattern-stress-test-2026-06.md` (the "before").

## What Changed Since the 67-Conversation Head-to-Head

All 5 fixes from the architecture review were applied:
1. **Code escalation (3-strike)** — after 3 code attempts, push to form (not loop)
2. **First reply acknowledges** — writer prompt says "acknowledge user first, then ask for code"
3. **Answer questions without code** — INFO_QUESTION intent for process/market questions
4. **Google Sheets integration** — property_store.py pulls 55 live codes (was 4 fixtures)
5. **FastAPI + shadow mode** — server.py runs on port 8020, LIVE/SHADOW modes

Additional fixes applied during this session:
6. **Short-circuit deterministic actions** — push_to_form/push_to_call return fixed text (<2ms, was 8s)
7. **Price fabrication guard normalization** — strips $/commas before comparing (was false-positive)
8. **Router: "what property" → ASK_FOR_CODE** — was routing to LEAD_INTENT → push_to_call
9. **Router: ~15 expanded CANT_FIND_CODE patterns** — catches "dont hava code", "where is the qh", etc.
10. **Writer: "Quan will" → "we'll get you started"** — banned phrase guard was stripping form replies
11. **Context amnesia fix in production** — brain.py now appends bot replies to session.history (3 return paths)
12. **Dual-format QH code regex** — `QH_CODE_RE` now matches both old (`QH001`) and new (`QH_9NJNF0`) sheet codes; uppercase normalization before sheet lookup; cross-reference for codes typed without underscore (`QH9NJNF0` → try `QH_9NJNF0`)
13. **Context-aware LLM fallback** — when LLM returns empty/None, writer generates fallback from router decision data (intent + property data + next-step hint) instead of static template
14. **LEAD_INTENT vs TOUR_REQUEST split** — TOUR_REQUEST stays deterministic (canned tour link); LEAD_INTENT goes to LLM with richer contextual hint for varied responses
15. **Stress test fairness fixes** — removed false banned phrases ("I'm Quan's assistant" is correct behavior, not banned); replaced fake codes (QH010, QH688) with real sheet codes (QH_9NJNF0, QH_X_JIMA, QH_0PJI0I, QH001, QH017); added property_store import for real code validation

## Methodology

- **Data:** 193 turns sampled from 1,734 inbound turns in `flow.db`
  (294 conversations total, 3,373 turns). Sampling was random with a
  fixed seed for reproducibility.
- **Framework:** Articechute 3-layer (router.py → writer.py → guards.py)
  running on port 8020 in SHADOW mode (processes but doesn't send).
- **LLM:** gemma4:31b via Ollama Cloud
- **Duration:** ~139 seconds (193 turns, 51.3% short-circuited = 94 LLM calls)
- **Date:** 2026-06-19

## Results

### Intent Distribution

| Intent | Count | % |
|--------|-------|---|
| just_chatting | 75 | 38.9% |
| show_property | 37 | 19.2% |
| lead_intent | 23 | 11.9% |
| cant_find_code | 17 | 8.8% |
| url_share | 14 | 7.3% |
| info_question | 13 | 6.7% |
| ask_for_code | 10 | 5.2% |
| buyer_intent | 4 | 2.1% |
| other (8 intents) | ~20 | ~10% |

16 intents total (vs production's 6).

### Action Distribution

| Action | Count | % |
|--------|-------|---|
| push_to_form | 57 | 29.5% |
| reply_voice | 37 | 19.2% |
| ask_for_code | 32 | 16.6% |
| push_to_call | 26 | 13.5% |
| show_property | 25 | 13.0% |
| reply_fixed | 14 | 7.3% |
| other | ~2 | ~1% |

### Quality Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Voice score | 0.854 | 0-1 scale, higher = more natural |
| Avg LLM latency | 1473ms | Only on LLM turns (51.3% were short-circuit) |
| Short-circuited | 51.3% | push_to_form/push_to_call skip LLM entirely |
| Guard hits | 19.7% | Mostly URL stripping (expected) |
| Fabrication flagged | 1.6% | Down from false-positive rate after fix |
| LLM errors | 3.6% | Ollama rate-limit empty replies |
| Empty replies | 3.6% | Matched LLM error rate (short-circuit never empty) |

### Comparison: Before vs After All Fixes

| Metric | 67-conv head-to-head (before) | 193-turn sampled (after) |
|--------|------------------------------|--------------------------|
| Code asks | ~30/67 (45%) | 16.6% |
| Form pushes | N/A (catch-all) | 29.5% (targeted, not catch-all) |
| Intents | 16 (Articechute) vs 6 (prod) | 16 (same) |
| Errors | 0 (deterministic) | 3.6% (Ollama rate-limit) |
| Voice score | Not measured | 0.854 |
| Short-circuited | 0% (all went through LLM) | 51.3% |

## Fixes 16-20 (Session 2, 2026-06-19 — Property Data Re-Attachment)

After the 193-turn stress test, a real-pattern stress test was run against both
PROD and SBX using 12 scenarios reconstructed from `conversation_log.jsonl`
(1,866 real IG DMs, 242 real users). SBX had 10 issues; PROD had 0. All 10 were
traced to a single root cause: **SBX fetches property data but doesn't pass it
to follow-up questions.**

**Root cause chain:**
1. User sends QH code → router fetches property_data → shows property card ✓
2. User asks "what area?" → router classifies as LOCATION_QUESTION → BUT property_data
   is None (router is stateless, doesn't have turn 1's data)
3. Router pushes to form (no data to answer from) → SBX says "Quan hasn't shared that yet"
4. **User sees bot show data then say it doesn't have data** → trust destroyed

**5 fixes applied:**

16. **`fetch_similar()` in property_store.py** — 3-pass matching ported from PROD
    `sheets.py`: same area+beds+tight price → same area+beds+loose price → same area only.
    Dedupes sibling codes.

17. **`last_property_code` in router `decide()`** — new parameter. When user asks
    a follow-up question (LOCATION_QUESTION, PRICE_QUESTION, MORTGAGE, SCHOOL_ZONE,
    COMPARE, WHAT_ABOUT), router re-fetches property data using the code from the
    prior turn and re-attaches it to the RouterDecision.

18. **`last_property_code` in UserSession** — server.py tracks the last property
    code the user looked up, passes it to `decide()` on every turn, updates it
    when a new property code is detected.

19. **Writer SYSTEM_PROMPT update** — explicit instruction: "When PROPERTY DATA is
    provided, answer USING the data. Do NOT say 'I can't share that' when the
    answer is in the dict." `_llm_fallback` for price/location questions reads
    directly from `decision.property_data`.

20. **CANT_FIND_CODE conversational-first** — first ask helps user find code
    ("check the reel caption for QH followed by numbers"), only pushes to form
    after 2 asks. Was: immediate form push.

**Post-fix result:** 12-scenario real-pattern stress test — PROD 0 issues, SBX 0
issues (TIE). SBX now answers location/price/availability questions from
re-attached property data instead of pushing to form.

**Known gap:** `last_property_code` stores ONE code. Multi-code back-referencing
("how much was the first one?") needs `{code: property_data}` dict. Covers ~90%
of real conversations; multi-code browsing is the remaining 10%.

## 4 Edge Cases Found (Not Yet Fixed)

1. **"it does have the code"** → push_to_form (should ask for code — user says they have it)
2. **"interested same house you have posted"** → push_to_form (should ask for code — property reference)
3. **"Ok"** → push_to_form (should be soft ack, not form push)
4. **"test ping"** → push_to_form (spam/test should not push form)

**Pattern:** The router is too eager to push_to_form on short/ambiguous messages.
Acknowledgments and spam need their own tier before the form-push fallback.

## How to Reproduce

```bash
cd /home/steve/quanbot-v4/sandbox/articechute
python3 run_stress_test.py  # runs 193 sampled turns from flow.db
```

The script uses a single persistent SQLite connection with pre-computed
code ask counts for performance. Full 1,734-turn run is possible but
takes ~20 min (timed out at 300s in foreground; use background execution).

## Articechute Architecture Files (Current State, Post Session-2 Fixes)

- `sandbox/articechute/framework/router.py` — 17 intents, 3-strike escalation,
  INFO_QUESTION, CANT_FIND_CODE (~15 patterns, conversational-first: help on
  1st ask, form push after 2), "what property" → ASK_FOR_CODE,
  dual-format QH_CODE_RE (old `QH001` + new `QH_9NJNF0`), uppercase normalization,
  cross-reference for underscoreless codes, LEAD_INTENT → LLM with richer hint,
  `last_property_code` param in `decide()` for follow-up question re-attachment
  (LOCATION_QUESTION, PRICE_QUESTION, MORTGAGE, SCHOOL_ZONE, COMPARE, WHAT_ABOUT)
- `sandbox/articechute/framework/writer.py` — thin LLM writer with
  short-circuit for push_to_form/push_to_call/tour_request; "acknowledge user first" prompt;
  context-aware fallback from router decision data when LLM returns empty;
  LEAD_INTENT → LLM (varied responses) vs TOUR_REQUEST → deterministic (canned link);
  SYSTEM_PROMPT explicitly says "answer USING property_data, do NOT say 'I can't share that'";
  `_llm_fallback` reads price/location directly from `decision.property_data` dict
- `sandbox/articechute/framework/guards.py` — URL allowlist, banned phrases
  ("Quan will"), price fabrication (normalized comparison)
- `sandbox/articechute/framework/property_store.py` — Google Sheets, 55 codes, 5-min cache,
  `fetch_similar()` 3-pass matching (area+beds+tight price → loose price → area only),
  dedupes sibling codes
- `sandbox/articechute/server.py` — FastAPI, port 8020, LIVE/SHADOW modes,
  `UserSession.last_property_code` tracking, passes to `decide()` on every turn
- `sandbox/articechute/run_stress_test.py` — standalone stress test script
- `ARCHITECTURE_REVIEW.md` — 298-line comprehensive reference
- `sandbox/stress_test_vs.py` — side-by-side PROD vs SBX stress test (15 scenarios)
- `sandbox/stress_test_real.py` — 12-scenario real-pattern stress test reconstructed
  from `conversation_log.jsonl` (1,866 real IG DMs, 242 users)