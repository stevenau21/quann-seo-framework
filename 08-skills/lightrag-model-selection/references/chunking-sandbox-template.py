#!/usr/bin/env python3
"""
LightRAG Chunking Model Sandbox — 3 models × 3 chunks, identical prompt.
Uses LightRAG's actual entity extraction prompt format.
"""
import requests, time, json, os

OLLAMA = "http://host.docker.internal:11434"
TUPLE = "<|#|>"
COMPLETE = "<|COMPLETE|>"
OUT = "./sandbox-results"
os.makedirs(OUT, exist_ok=True)

# ── Load 3 representative chunks (~250 words each) ──
CHUNKS = {
    "chunk_intro": """...""",
    "chunk_mid": """...""",
    "chunk_advanced": """...""",
}

# ── LightRAG entity extraction prompt (verbatim from lightrag/prompt.py) ──
ENTITY_TYPES = "Person, Organization, Location, Event, Concept, Method, Content, Data, Artifact, NaturalObject"
SYSTEM = f"""---Role---
You are a Knowledge Graph Specialist. Extract entities and relationships from the input text.

---Instructions---
1. Identify clearly defined entities. Extract: entity_name, entity_type, entity_description.
2. Identify direct relationships between extracted entities. Extract: source_entity, target_entity, relationship_keywords, relationship_description.
3. Output format (strict):
   entity{TUPLE}entity_name{TUPLE}entity_type{TUPLE}entity_description
   relation{TUPLE}source_entity{TUPLE}target_entity{TUPLE}relationship_keywords{TUPLE}relationship_description
4. Output all entities first, then all relations. End with {COMPLETE}.
5. Third person. No pronouns. English. Consistent entity naming.

---Entity Types---
{ENTITY_TYPES}"""

# ── Models to test ──
MODELS = [
    ("gemma4-31b", "gemma4:31b-cloud", 4096),
    ("deepseek-v4-flash", "deepseek-v4-flash:cloud", 4096),
    ("deepseek-v4-pro", "deepseek-v4-pro:cloud", 8192),  # reasoning model needs more tokens
]

# ── Run all combinations, save each result immediately ──
for model_label, model_name, max_tok in MODELS:
    for chunk_key, chunk_text in CHUNKS.items():
        result_file = os.path.join(OUT, f"{chunk_key}__{model_label}.json")
        if os.path.exists(result_file):
            print(f"SKIP {chunk_key}__{model_label} — already saved")
            continue
        
        print(f"\n[{chunk_key}__{model_label}] Running...", flush=True)
        
        USER = f"""---Task---
Extract entities and relationships.

---Input Text---
```
{chunk_text}
```

---Output---
"""
        
        try:
            start = time.time()
            resp = requests.post(f"{OLLAMA}/api/chat", json={
                "model": model_name, "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": USER},
                ],
                "options": {"temperature": 0.0, "num_predict": max_tok},
            }, timeout=600)
            elapsed = time.time() - start
            
            data = resp.json()
            msg = data["message"]
            raw = msg.get("content", "") or msg.get("thinking", "") or ""
            
            entities = [l.split(TUPLE) for l in raw.split("\n")
                       if l.strip() and l.split(TUPLE)[0] == "entity" and len(l.split(TUPLE)) == 4]
            relations = [l.split(TUPLE) for l in raw.split("\n")
                       if l.strip() and l.split(TUPLE)[0] == "relation" and len(l.split(TUPLE)) == 5]
            completed = COMPLETE in raw
            
            result = {
                "model": model_label, "chunk": chunk_key,
                "elapsed_s": round(elapsed, 1),
                "tokens_in": data.get("prompt_eval_count", 0),
                "tokens_out": data.get("eval_count", 0),
                "num_entities": len(entities),
                "num_relations": len(relations),
                "completed": completed,
                "raw_output": raw,
            }
            
            with open(result_file, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            status = "✓" if completed else "✗"
            print(f"  {status} {elapsed:.0f}s | {len(entities)}e/{len(relations)}r | saved", flush=True)
            
        except Exception as e:
            with open(result_file, "w") as f:
                json.dump({"error": str(e)}, f)
            print(f"  ✗ FAIL: {e}", flush=True)

# ── Summary ──
print(f"\n{'='*80}")
print(f"RESULTS: {OUT}/")
for f in sorted(os.listdir(OUT)):
    if f.endswith(".json"):
        with open(os.path.join(OUT, f)) as fh:
            r = json.load(fh)
        if "error" in r:
            print(f"  {f}: ERROR — {r['error'][:60]}")
        else:
            print(f"  {f}: {r['elapsed_s']:.0f}s {r['num_entities']}e/{r['num_relations']}r {'✓' if r['completed'] else '✗'}")
print("COMPLETE")
