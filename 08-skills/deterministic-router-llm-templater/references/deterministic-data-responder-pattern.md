# Deterministic Data Responder Pattern

## When to Use

Add this layer to a deterministic-router chatbot when:
- The bot has a structured data source (Google Sheet, DB, API)
- Users ask simple field-mapping questions ("how many beds?", "what price?", "what area?")
- The LLM writer times out on these simple questions, causing fallback to a dead-end action (form push)
- The answer is already in the data dict the router fetched — no creativity needed

## Architecture (Three-Tier Short-Circuit)

```
User Message → Python Router (0ms) → [Data Responder (0.4ms)] → LLM Templater (~8s)
                    ↓                        ↓                               ↓
              WHAT to do              DATA LOOKUP (skip LLM)         HOW to say it
              (action enum)           (if data exists, answer)        (creative text)
```

Three tiers, checked in order:
1. **Router short-circuits** (0ms): deterministic actions with fixed URLs (`push_to_form`, `push_to_call`)
2. **Data responder** (0.4ms): field-mapping questions answered from data dict (beds, price, area, etc.)
3. **LLM writer** (~8s): everything else — creative replies, context-aware phrasing

Latency tells you which tier fired: 0ms = router, <1ms = data responder, >1s = LLM.

## Implementation

```python
def _property_data_reply(decision: RouterDecision, current_message: str) -> str | None:
    """Answer simple data questions from the data dict. Returns reply text or None."""
    if not decision.property_data:
        return None  # no data → fall through to LLM

    p = decision.property_data
    ml = current_message.lower().strip()

    # Each field: check keywords, check data exists, return formatted string
    if any(k in ml for k in ["how many bed", "beds", "bedroom", "number of bed"]):
        beds = p.get("beds", "")
        if beds:
            return f"It has {beds} beds."
        return None  # field empty → fall through

    if any(k in ml for k in ["how much", "price", "cost", "starting from"]):
        price = str(p.get("price", "")).strip()
        if price:
            return f"It is starting from {price}."
        return None

    if any(k in ml for k in ["area", "location", "where"]):
        area = p.get("area", "") or p.get("area_city", "")
        if area:
            return f"It is located in {area}."
        return None

    if any(k in ml for k in ["sqft", "square", "size"]):
        sqft = p.get("sqft", "")
        if sqft:
            return f"It is {sqft} sqft."
        return None

    if any(k in ml for k in ["garage", "parking"]):
        garage = p.get("garage", "")
        if garage:
            return f"It has a {garage}-car garage."
        return None

    if any(k in ml for k in ["model", "models", "floor plan"]):
        models = p.get("models", "")
        if models:
            return f"Available models: {models}."
        return None

    # "Tell me about it" → full summary from all available fields
    if any(k in ml for k in ["tell me about", "more details", "full details", "about this"]):
        parts = []
        if p.get("area"): parts.append(f"located in {p['area']}")
        if p.get("beds"): parts.append(f"{p['beds']} beds")
        if p.get("baths"): parts.append(f"{p['baths']} baths")
        if p.get("sqft"): parts.append(f"{p['sqft']} sqft")
        if p.get("price"): parts.append(f"starting from {p['price']}")
        if parts:
            return f"This property is {', '.join(parts[:-1])}, and {parts[-1]}."
        return None

    return None  # not a data question → LLM handles it


# In the writer's execute() method, BEFORE building the LLM prompt:
async def write_reply(decision, current_message, session):
    # Tier 2: Data responder (0.4ms)
    prop_reply = _property_data_reply(decision, current_message)
    if prop_reply:
        return {"reply": prop_reply, "latency_ms": 0.4, "llm_called": False}

    # Tier 3: LLM writer (~8s)
    prompt = build_prompt(decision, current_message, session)
    result = await llm.call(prompt)
    # ... LLM handling continues ...
```

## Design Rules

1. **Only intercept field-mapping questions.** Beds, baths, price, area, sqft, garage — questions where the answer is a single field value from the data dict.
2. **Only answer if the field has data.** Empty field → return `None` → LLM handles (it can say "not available" or push form). Never fabricate.
3. **Never fabricate.** Use exactly what's in the property_data dict. If `price` is empty, don't guess.
4. **"Tell me about it" = full summary.** Build a natural-language summary from ALL available fields, not just one. Handle the Oxford comma gracefully.
5. **Return None for non-matching messages.** Complex questions ("Is this a good area for schools?") still go to the LLM. The responder only handles direct field lookups.
6. **Runs after router, before LLM.** The router already re-attached property data from session state. The responder just reads the dict.
7. **Latency is the diagnostic.** If a property question takes >1s, the data responder didn't fire — check why (property_data was None, keyword didn't match, field was empty).

## Measured Results (QuanBot SBX, 2026-06-19)

| Question | Latency | Answer | LLM Called? |
|----------|---------|--------|-------------|
| "How many beds" | 0.4ms | "It has 5 beds." | No |
| "How much" | 0.4ms | "It is starting from $262K." | No |
| "What area" | 0.4ms | "It is located in about 45 minutes outside Houston." | No |
| "How many sqft" | 0.4ms | "It is 2416 sqft." | No |
| "Tell me about it" | 0.4ms | Full summary from all fields | No |
| "Is this a good area for schools?" | ~8s | LLM creative reply | Yes |

6/6 data questions answered in 0.4ms. Zero LLM calls. Zero timeout failures.

## When NOT to Use This Pattern

- Bot has no structured data source (pure conversational, no sheet/DB)
- All questions require creative phrasing (no field-mapping questions)
- Data source is unreliable/stale and LLM hallucination is actually safer than stale data
- The bot's replies are always short-form and never time out