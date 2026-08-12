#!/usr/bin/env python3
"""
Phase 2: Per-Document Extraction Pipeline
=========================================
Processes all 394 documents individually with Ollama to extract:
- Named frameworks/methodologies
- Mental models
- Methods/techniques
- Ranking signals
- Tools/software

Then deduplicates and aggregates.
"""

import json
import time
import os
import httpx
from collections import Counter, defaultdict
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
DOCS_PATH = "/home/steve/lightrag-apps/koray-gubur/workspace/kv_store_full_docs.json"
OLLAMA_URL = "http://192.168.4.148:11434/v1/chat/completions"
MODEL = "gemma4:31b-cloud"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"
os.makedirs(OUTDIR, exist_ok=True)

SYSTEM_PROMPT = """You extract structured data from SEO methodology documents.

For the document content provided, extract ALL named frameworks, methodologies, mental models, methods, ranking signals, and tools.

You MUST return ONLY a valid JSON object with these keys:
- "frameworks": array of {name, definition, type: "framework"|"methodology"|"system"|"strategy"}
- "mental_models": array of {name, description} 
- "methods": array of {name, description, steps: [string] (if available)}
- "signals": array of {name, description, importance: "primary"|"secondary"|"supporting"}
- "tools": array of {name, purpose}
- "key_concepts": array of {name, description}

DO NOT include HTML tags, browser names, programming language fundamentals, or obvious non-SEO entities.
DO include actual named frameworks, methodologies, techniques, and mental models Koray describes.
If nothing relevant is found for a category, return an empty array.

Return ONLY the JSON object. No markdown, no explanation."""


def call_ollama(doc_content: str, max_tokens: int = 2000) -> dict:
    """Extract structured data from a single document."""
    # Truncate long docs
    text = doc_content[:5000]
    
    user_prompt = f"Document content:\n\n{text}"
    
    for attempt in range(2):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "temperature": 0.2,
                        "max_tokens": max_tokens,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                    },
                )
                resp.raise_for_status()
                content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse JSON
                content = content.strip()
                # Remove markdown fences
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:]) if len(lines) > 1 else content
                    if content.endswith("```"):
                        content = content[:-3]
                
                return json.loads(content) if content else {}
        except json.JSONDecodeError:
            # Try extracting JSON from response
            import re
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            return {}
        except Exception as e:
            if attempt == 1:
                return {}
            time.sleep(2)
    
    return {}


def normalize_name(name: str) -> str:
    """Normalize for deduplication."""
    return name.strip().lower()


def main():
    start_time = time.time()
    
    # Load docs
    print("Loading documents...")
    with open(DOCS_PATH) as f:
        docs = json.load(f)
    print(f"  {len(docs)} documents loaded")
    
    # Checkpoint file for resuming
    checkpoint_path = f"{OUTDIR}/extraction_checkpoint.json"
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path) as f:
            done = set(json.load(f))
        print(f"  Resuming from checkpoint: {len(done)} already processed")
    else:
        done = set()
    
    # Aggregation buckets
    all_frameworks = Counter()  # name -> count
    all_framework_details = {}  # name -> list of definitions
    all_mental_models = Counter()
    all_mental_model_details = {}
    all_methods = Counter()
    all_method_details = {}
    all_signals = Counter()
    all_signal_details = {}
    all_tools = Counter()
    all_tool_details = {}
    all_concepts = Counter()
    all_concept_details = {}
    
    # Co-occurrence tracking
    framework_cooccurrence = defaultdict(Counter)
    
    doc_list = list(docs.items())
    batch_size = 20
    
    for i, (doc_id, doc) in enumerate(doc_list):
        if doc_id in done:
            continue
        
        content = doc.get("content", "")
        if len(content) < 500:
            continue
        
        extracted = call_ollama(content)
        
        # Collect frameworks
        doc_frameworks = set()
        for fw in extracted.get("frameworks", []):
            name = fw.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_frameworks[nname] += 1
                if nname not in all_framework_details:
                    all_framework_details[nname] = []
                all_framework_details[nname].append(fw.get("definition", ""))
                doc_frameworks.add(nname)
        
        # Track co-occurrence
        fw_list = list(doc_frameworks)
        for a in range(len(fw_list)):
            for b in range(a+1, len(fw_list)):
                framework_cooccurrence[fw_list[a]][fw_list[b]] += 1
                framework_cooccurrence[fw_list[b]][fw_list[a]] += 1
        
        # Mental models
        for mm in extracted.get("mental_models", []):
            name = mm.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_mental_models[nname] += 1
                if nname not in all_mental_model_details:
                    all_mental_model_details[nname] = []
                all_mental_model_details[nname].append(mm.get("description", ""))
        
        # Methods
        for m in extracted.get("methods", []):
            name = m.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_methods[nname] += 1
                if nname not in all_method_details:
                    all_method_details[nname] = []
                all_method_details[nname].append(m)
        
        # Signals
        for s in extracted.get("signals", []):
            name = s.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_signals[nname] += 1
                if nname not in all_signal_details:
                    all_signal_details[nname] = []
                all_signal_details[nname].append(s)
        
        # Tools
        for t in extracted.get("tools", []):
            name = t.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_tools[nname] += 1
                if nname not in all_tool_details:
                    all_tool_details[nname] = []
                all_tool_details[nname].append(t.get("purpose", ""))
        
        # Concepts
        for c in extracted.get("key_concepts", []):
            name = c.get("name", "").strip()
            if name and len(name) > 2:
                nname = normalize_name(name)
                all_concepts[nname] += 1
                if nname not in all_concept_details:
                    all_concept_details[nname] = []
                all_concept_details[nname].append(c.get("description", ""))
        
        done.add(doc_id)
        
        # Progress & checkpoint
        if (i + 1) % batch_size == 0 or i == len(doc_list) - 1:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(docs) - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(docs)}] {elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining")
            print(f"    Frameworks: {len(all_frameworks)}, Models: {len(all_mental_models)}, "
                  f"Methods: {len(all_methods)}, Signals: {len(all_signals)}")
            
            # Save checkpoint
            with open(checkpoint_path, "w") as f:
                json.dump(list(done), f)
            
            # Save intermediate results
            intermediate = {
                "progress": f"{i+1}/{len(docs)}",
                "frameworks": dict(all_frameworks.most_common(100)),
                "mental_models": dict(all_mental_models.most_common(50)),
                "methods": dict(all_methods.most_common(50)),
                "signals": dict(all_signals.most_common(30)),
                "tools": dict(all_tools.most_common(30)),
            }
            with open(f"{OUTDIR}/extraction_intermediate.json", "w") as f:
                json.dump(intermediate, f, indent=2)
        
        # Rate limiting
        time.sleep(0.5)
    
    # ── Assemble final output ────────────────────────────────────
    print("\nAssembling final results...")
    
    # Build framework objects
    frameworks_out = []
    for name, count in all_frameworks.most_common():
        definitions = all_framework_details.get(name, [])
        # Pick the longest/most detailed definition
        best_def = max(definitions, key=len) if definitions else ""
        
        # Get co-occurring frameworks
        related = framework_cooccurrence.get(name, {})
        top_related = [n for n, c in related.most_common(10) if c >= 2]
        
        frameworks_out.append({
            "name": name.title(),
            "occurrences": count,
            "definition": best_def[:500],
            "related_frameworks": top_related,
        })
    
    # Build mental model objects
    models_out = []
    for name, count in all_mental_models.most_common():
        descriptions = all_mental_model_details.get(name, [])
        best_desc = max(descriptions, key=len) if descriptions else ""
        models_out.append({
            "name": name.title(),
            "occurrences": count,
            "description": best_desc[:500],
        })
    
    # Build signal objects
    signals_out = []
    for name, count in all_signals.most_common():
        details = all_signal_details.get(name, [])
        best = max(details, key=lambda x: len(x.get("description", ""))) if details else {}
        signals_out.append({
            "name": name.title(),
            "occurrences": count,
            "description": best.get("description", ""),
            "importance": best.get("importance", ""),
        })
    
    # Build methods
    methods_out = []
    for name, count in all_methods.most_common():
        details = all_method_details.get(name, [])
        best = max(details, key=lambda x: len(x.get("description", ""))) if details else {}
        methods_out.append({
            "name": name.title(),
            "occurrences": count,
            "description": best.get("description", ""),
            "steps": best.get("steps", []),
        })
    
    final = {
        "extraction_metadata": {
            "method": "per-document-llm-extraction",
            "documents_processed": len(done),
            "model": MODEL,
            "date": datetime.now().isoformat(),
        },
        "frameworks": frameworks_out,
        "mental_models": models_out,
        "ranking_signals": signals_out,
        "methods": methods_out,
        "tools": [{"name": n.title(), "occurrences": c, "purpose": all_tool_details.get(n, [""])[0]} 
                  for n, c in all_tools.most_common(30)],
        "framework_cooccurrence": {
            "pairs": [
                {"a": a, "b": b, "weight": w}
                for a in framework_cooccurrence
                for b, w in framework_cooccurrence[a].most_common()
                if a < b and w >= 2
            ]
        },
    }
    
    outpath = f"{OUTDIR}/extraction_per_doc.json"
    with open(outpath, "w") as f:
        json.dump(final, f, indent=2)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Extraction complete in {elapsed:.0f}s")
    print(f"   Frameworks found: {len(frameworks_out)}")
    print(f"   Mental models: {len(models_out)}")
    print(f"   Ranking signals: {len(signals_out)}")
    print(f"   Methods: {len(methods_out)}")
    print(f"   Output: {outpath}")


if __name__ == "__main__":
    main()
