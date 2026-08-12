#!/usr/bin/env python3
"""
LightRAG Chunking Model Sandbox Runner.

Runs LightRAG's exact extraction prompt against N candidate models
on M representative chunks. Saves raw outputs for quality comparison.

Usage:
    python3 scripts/chunking-sandbox.py

Requires:
    - Chunk files at /tmp/chunking-sandbox/chunk_1.txt, chunk_2.txt, chunk_3.txt
    - Ollama accessible at http://host.docker.internal:11434
    - Models already pulled
"""

import requests, time, json, os

OLLAMA = "http://host.docker.internal:11434"
OUT = "/tmp/chunking-sandbox/results"
CHUNKS_DIR = "/tmp/chunking-sandbox"

# LightRAG's actual extraction system prompt (from lightrag/prompt.py)
ENTITY_TYPES = "Person, Organization, Location, Event, Concept, Method, Content, Data, Artifact, NaturalObject"
TUPLE = "<|#|>"
COMPLETE = "<|COMPLETE|>"

SYSTEM_PROMPT = f"""---Role---
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

# --- CONFIG: Models and their token caps ---
MODELS = [
    {"name": "gemma4:31b-cloud", "num_predict": 4096, "label": "gemma4-31b"},
    {"name": "deepseek-v4-flash:cloud", "num_predict": 16384, "label": "deepseek-v4-flash"},
    {"name": "deepseek-v4-pro:cloud", "num_predict": 8192, "label": "deepseek-v4-pro"},
]

CHUNKS = ["chunk_1.txt", "chunk_2.txt", "chunk_3.txt"]

os.makedirs(OUT, exist_ok=True)


def parse_output(raw):
    """Parse entity and relation tuples from raw output."""
    entities, relations = [], []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(TUPLE)
        if parts[0] == "entity" and len(parts) == 4:
            entities.append(parts)
        elif parts[0] == "relation" and len(parts) == 5:
            relations.append(parts)
    return entities, relations


def main():
    for model in MODELS:
        for chunk_file in CHUNKS:
            chunk_key = chunk_file.replace(".txt", "")
            out_file = os.path.join(OUT, f"{chunk_key}__{model['label']}.json")
            
            # Skip if already done
            if os.path.exists(out_file):
                print(f"  [SKIP] {model['label']} / {chunk_key} — already exists")
                continue
            
            with open(os.path.join(CHUNKS_DIR, chunk_file)) as f:
                chunk = f.read().strip()
            
            user_msg = f"""---Task---
Extract entities and relationships.

---Input Text---
```
{chunk}
```

---Output---
"""
            
            print(f"  [{model['label']}] {chunk_key}...", end=" ", flush=True)
            start = time.time()
            
            try:
                resp = requests.post(
                    f"{OLLAMA}/api/chat",
                    json={
                        "model": model["name"],
                        "stream": False,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_msg},
                        ],
                        "options": {
                            "temperature": 0.0,
                            "num_predict": model["num_predict"],
                        },
                    },
                    timeout=600,
                )
                
                elapsed = time.time() - start
                data = resp.json()
                msg = data["message"]
                raw = msg.get("content", "") or ""
                
                # Fallback: some reasoning models put output in 'thinking'
                if not raw and msg.get("thinking"):
                    raw = msg["thinking"]
                
                entities, relations = parse_output(raw)
                completed = COMPLETE in raw
                
                result = {
                    "model": model["label"],
                    "chunk": chunk_key,
                    "elapsed_s": round(elapsed, 1),
                    "tokens_in": data.get("prompt_eval_count", 0),
                    "tokens_out": data.get("eval_count", 0),
                    "output_chars": len(raw),
                    "num_entities": len(entities),
                    "num_relations": len(relations),
                    "completed": completed,
                    "source_field": "thinking" if not msg.get("content") and msg.get("thinking") else "content",
                    "raw_output": raw,
                    "num_predict_used": model["num_predict"],
                }
                
                with open(out_file, "w") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                status = "✓" if completed else "✗"
                print(f"{status} {elapsed:.0f}s | {len(entities)}e/{len(relations)}r | {data.get('eval_count', 0)} tok")
                
            except Exception as e:
                print(f"✗ FAIL: {e}")
    
    print("\n=== SANDBOX COMPLETE ===")
    # Summarize results
    print("\nSUMMARY TABLE")
    print(f"{'MODEL':<25} {'CHUNK':<25} {'TIME':>6} {'E':>4} {'R':>4} {'DONE':>5} {'TOK':>6}")
    print("-" * 77)
    for model in MODELS:
        for chunk_file in CHUNKS:
            chunk_key = chunk_file.replace(".txt", "")
            out_file = os.path.join(OUT, f"{chunk_key}__{model['label']}.json")
            if os.path.exists(out_file):
                r = json.load(open(out_file))
                print(f"{r['model']:<25} {r['chunk']:<25} {r['elapsed_s']:>5.0f}s {r['num_entities']:>4} {r['num_relations']:>4} {'✓' if r['completed'] else '✗':>5} {r['tokens_out']:>6}")


if __name__ == "__main__":
    main()
