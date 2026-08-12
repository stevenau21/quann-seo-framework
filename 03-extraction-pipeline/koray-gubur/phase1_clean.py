#!/usr/bin/env python3
"""
Phase 1: Graph Cleaning
=======================
Takes LightRAG's raw entity graph (10,480 entities, 13,973 edges) and produces
a clean, typed entity graph suitable for community detection.

Operations:
1. Entity type classification (framework, method, tool, person, noise)
2. Deduplication (case variants, slight spelling differences)
3. Edge deduplication (same pair different forms)
4. Noise filtering (HTML tags, word lists, browser names)
5. Output: clean_graph.json for Phase 2
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────
WORKSPACE = "/home/steve/lightrag-apps/koray-gubur/workspace"
ENTITIES_PATH = f"{WORKSPACE}/kv_store_full_entities.json"
RELATIONS_PATH = f"{WORKSPACE}/kv_store_full_relations.json"
DOCS_PATH = f"{WORKSPACE}/kv_store_full_docs.json"
OUTDIR = "/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur"

# ── Entity Type Classifiers ──────────────────────────────────────

# Patterns for noise entities we definitely want to exclude
NOISE_PATTERNS = [
    # HTML tags
    r'^<.*> HTML Tag$', r'^<.*> HTML Tags?$', r'^.* HTML Tag$',
    r'^.* Tag$', r'^.* Element$', r'^.* Attribute$',
    # Single letters
    r'^Letter [A-Z]$', r'^Letter [A-Z] \(Latin\)$',
    # Word classifications  
    r'^.* Words$', r'^.* Words That (Start|Begin|End) With [A-Z]$',
    r'^\d+-?Letter Words.*$', r'^\d+ Letter Words.*$',
    r'^(Short|Long) Words.*$', r'^(Long|Short) [A-Z]$',
    r'^(Common|Rare|Positive|Negative) Words.*$',
    r'^Rarest Words.*$', r'^Rare Words.*$',
    r'^Words (Starting|That).*$', r'^[A-Z] Words$',
    r'^[A-Z] Letter Words.*$',
    r'^\d+-Letter Words.*$',
    # HTTP headers  
    r'^.* HTTP Header$', r'^.* HTTP Response Header$',
    r'^.* HTTP Request Header$', r'^.* HTTP Headers?$',
    r'^.* Header$', r'^.* Headers$',
    # HTTP status codes
    r'^\d{3} .*$', r'^\d{3} HTTP.*$',
    # Programming specifics
    r'^.* Attribute$', r'^.* Property$', r'^.* Method$',
    r'^.* Library$', r'^.* Module$', r'^.* Function$',
    r'^.* Package$', r'^.* Class$',
    # Browsers
    r'^.* Browser$', r'^.* Browser .*$',
    r'^Internet Explorer.*$', r'^Google Chrome$',
    r'^Mozilla Firefox$', r'^Microsoft Edge$',
    # CSS/JS specifics
    r'^.* CSS .*$', r'^.* JavaScript .*$',
    r'^CSS .*$', r'^.* CSS$',
    # Word pairs / language specifics
    r'^.* vs .*$', r'^.* and .*$',
    r'^.* Language$', r'^.* English$', r'^.* French$',
    r'^.* Dictionar(y|ies)$',
    # RFC specs
    r'^RFC \d+.*$',
    # Misc noise
    r'^.* Status Code$', r'^.* Code$',
    r'^.* Error$', r'^.* Warning$',
    r'^.* API$', r'^.* SDK$',
    r'^.* Format$', r'^.* Type$',
    r'^.* Role$', r'^.* State$',
    r'^.* Value$', r'^.* Values$',
    r'^.* Mode$', r'^.* Modes$',
    r'^.* Version$', r'^.* Versions$',
    r'^.* Option$', r'^.* Options$',
    r'^.* Parameter$', r'^.* Parameters$',
    r'^.* Flag$', r'^.* Flags$',
    r'^.* Setting$', r'^.* Settings$',
    r'^.* Config$', r'^.* Configuration$',
    r'^.* Data$', r'^.* Dataset$',
    r'^.* File$', r'^.* Files$',
    r'^.* Directory$', r'^.* Path$',
    r'^.* URL$', r'^.* URI$',
    r'^.* Domain$', r'^.* Subdomain$',
    r'^.* Server$', r'^.* Host$',
    r'^.* Port$', r'^.* Socket$',
    r'^.* Protocol$',
    r'^.* Proxy$', r'^.* Proxy .*$',
    r'^.* Certificate$', r'^.* Cert$',
    r'^.* Key$', r'^.* Token$',
    r'^.* Cookie$', r'^.* Session$',
    r'^.* Cache$', r'^.* Caching$',
    r'^.* CDN$', r'^.* CDN .*$',
    r'^.* Plugin$', r'^.* Extension$',
    r'^.* Widget$', r'^.* Component$',
    r'^.* Template$', r'^.* Theme$',
    r'^.* Layout$', r'^.* Design$',
    r'^.* Style$', r'^.* Styles$',
    r'^.* Color$', r'^.* Font$',
    r'^.* Image$', r'^.* Video$',
    r'^.* Audio$', r'^.* Media$',
    r'^.* Content$', r'^.* Text$',
    r'^.* String$', r'^.* Character$',
    r'^.* Number$', r'^.* Integer$',
    r'^.* Boolean$', r'^.* Array$',
    r'^.* Object$', r'^.* List$',
    r'^.* Map$', r'^.* Set$',
    r'^.* Queue$', r'^.* Stack$',
    r'^.* Tree$', r'^.* Graph$',
    r'^.* Node(js)?$', r'^.* Edge$',
    r'^.* Link$', r'^.* Path$',
    r'^.* Route$', r'^.* Redirect$',
    r'^.* Request$', r'^.* Response$',
    r'^.* Load$', r'^.* Reload$',
    r'^.* Refresh$', r'^.* Update$',
    r'^.* Create$', r'^.* Delete$',
    r'^.* Read$', r'^.* Write$',
    r'^.* Open$', r'^.* Close$',
    r'^.* Start$', r'^.* Stop$',
    r'^.* Begin$', r'^.* End$',
    r'^.* First$', r'^.* Last$',
    r'^.* Next$', r'^.* Previous$',
    r'^.* New$', r'^.* Old$',
    r'^.* Big$', r'^.* Small$',
    r'^.* High$', r'^.* Low$',
    r'^.* Fast$', r'^.* Slow$',
    r'^.* Good$', r'^.* Bad$',
    r'^.* Best$', r'^.* Worst$',
    r'^.* Top$', r'^.* Bottom$',
    r'^.* Left$', r'^.* Right$',
    r'^.* Up$', r'^.* Down$',
    r'^.* In$', r'^.* Out$',
    r'^.* On$', r'^.* Off$',
    r'^.* Yes$', r'^.* No$',
    r'^.* True$', r'^.* False$',
    r'^.* OK$', r'^.* Error$',
    r'^.* Success$', r'^.* Failure$',
]

# Patterns that suggest a framework/methodology entity
FRAMEWORK_PATTERNS = [
    r'(?i)\b(framework|methodology|approach|strategy|system|model|process|paradigm)\b',
    r'(?i)\b(seo|search engine optimization|search)\b',
    r'(?i)\b(topical|semantic|holistic|entity|knowledge)\b',
    r'(?i)\b(authority|ranking|relevance|quality)\b',
    r'(?i)\b(signal|factor|metric|score)\b',
    r'(?i)\b(content|marketing|digital|web)\b',
    r'(?i)\b(optimization|engine|algorithm)\b',
    r'(?i)\b(analysis|analytics|intelligence)\b',
    r'(?i)\b(network|graph|map|mapping)\b',
]

# Patterns for people
PERSON_PATTERNS = [
    r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # Two capitalized names
    r'^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+$',  # Initial form
    r'^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+$',  # Three names
]

# Patterns for tools/software
TOOL_PATTERNS = [
    r'(?i)^(google|bing|yandex|baidu|duckduckgo) ',
    r'(?i)^(nltk|wordnet|scrapy|pandas|numpy|tensorflow|pytorch|spacy|gensim|scikit)',
    r'(?i)^(wordpress|shopify|wix|squarespace|joomla|drupal|magento)',
    r'(?i)^(chrome|firefox|safari|edge|opera|brave) ',
    r'(?i)^(semrush|ahrefs|moz|majestic|screaming frog)',
    r'(?i)^(python|javascript|php|ruby|java|golang|rust) ',
    r'(?i) (api|sdk|cli|tool|platform|service|app|application)$',
]

# ── Deduplication ─────────────────────────────────────────────────

def normalize_entity(name: str) -> str:
    """Normalize entity name for deduplication."""
    n = name.strip()
    # Lowercase
    n = n.lower()
    # Remove special chars but keep spaces
    n = re.sub(r'[^\w\s\-&]', '', n)
    # Normalize whitespace
    n = re.sub(r'\s+', ' ', n).strip()
    # Remove common suffixes
    n = re.sub(r'\s*(course|guide|tutorial|handbook|manual|guidebook|ebook|pdf)$', '', n, flags=re.IGNORECASE)
    return n


def find_duplicates(entities: list[str]) -> dict:
    """Group entities by normalized form."""
    groups = defaultdict(list)
    for e in entities:
        norm = normalize_entity(e)
        groups[norm].append(e)
    return {k: v for k, v in groups.items() if len(v) > 1}


def pick_canonical(variants: list[str]) -> str:
    """Pick the best variant as canonical name."""
    # Prefer longest (usually most complete)
    variants_sorted = sorted(set(variants), key=len, reverse=True)
    # Prefer title case
    for v in variants_sorted:
        if v[0].isupper() and v == v.title():
            return v
    # Fallback to longest
    return variants_sorted[0]


# ── Type Classification ──────────────────────────────────────────

def classify_entity(name: str) -> str:
    """Classify entity into: framework, method, tool, person, noise, or concept."""
    
    # Check noise first
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            return "noise"
    
    # Check people
    for pattern in PERSON_PATTERNS:
        if re.match(pattern, name):
            # But not if it's a framework name that looks like a person
            if any(re.search(p, name, re.IGNORECASE) for p in FRAMEWORK_PATTERNS):
                break
            return "person"
    
    # Check tools
    for pattern in TOOL_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return "tool"
    
    # Check frameworks
    fw_score = 0
    for pattern in FRAMEWORK_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            fw_score += 1
    
    # Multi-word entities with framework patterns
    words = name.split()
    if len(words) >= 3 and fw_score >= 1:
        return "framework"
    elif len(words) == 2 and fw_score >= 1:
        return "framework"
    elif fw_score >= 2:
        return "framework"
    
    # Methods/techniques (named actions)
    if re.search(r'(?i)\b(analysis|testing|optimization|extraction|classification|clustering|mapping|tracking|monitoring|auditing|audit)$', name):
        return "method"
    
    # Default: concept
    return "concept"


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("═══ Phase 1: Graph Cleaning ═══\n")
    
    # Load data
    print("Loading data...")
    with open(ENTITIES_PATH) as f:
        entities = json.load(f)
    with open(RELATIONS_PATH) as f:
        relations = json.load(f)
    
    print(f"  Entities: {len(entities)} sets across {len(entities)} docs")
    print(f"  Relations: {len(relations)} sets")
    
    # Collect all entity names and compute statistics
    all_entity_names = []
    for doc_id, entry in entities.items():
        all_entity_names.extend(entry.get("entity_names", []))
    
    name_counts = Counter(all_entity_names)
    print(f"  Total entity mentions: {len(all_entity_names)}")
    print(f"  Unique entity names: {len(name_counts)}")
    
    # Classify each entity
    print("\nClassifying entities...")
    classifications = {}
    for name in name_counts:
        classifications[name] = classify_entity(name)
    
    type_counts = Counter(classifications.values())
    print(f"  Framework: {type_counts.get('framework', 0)}")
    print(f"  Method: {type_counts.get('method', 0)}")
    print(f"  Tool: {type_counts.get('tool', 0)}")
    print(f"  Person: {type_counts.get('person', 0)}")
    print(f"  Concept: {type_counts.get('concept', 0)}")
    print(f"  Noise: {type_counts.get('noise', 0)}")
    
    # Find duplicates
    print("\nDeduplicating...")
    unique_names = list(name_counts.keys())
    dupes = find_duplicates(unique_names)
    print(f"  Duplicate groups: {len(dupes)}")
    
    # Build canonical name mapping
    canonical_map = {}
    for norm, variants in dupes.items():
        canonical = pick_canonical(variants)
        for v in variants:
            canonical_map[v] = canonical
    
    # For non-duplicates, canonical = self
    for name in name_counts:
        if name not in canonical_map:
            canonical_map[name] = name
    
    # Build clean edge list
    print("\nBuilding clean edge list...")
    clean_edges = defaultdict(Counter)  # canonical_a -> {canonical_b: weight}
    
    for doc_id, entry in relations.items():
        pairs = entry.get("relation_pairs", [])
        for src, dst in pairs:
            # Map to canonical
            cs = canonical_map.get(src, src)
            cd = canonical_map.get(dst, dst)
            
            # Skip noise
            if classifications.get(cs) == "noise" or classifications.get(cd) == "noise":
                continue
            
            # Skip self-loops
            if cs == cd:
                continue
            
            # Weighted edge
            clean_edges[cs][cd] += 1
            clean_edges[cd][cs] += 1  # Undirected
    
    # Compute entity stats
    entity_stats = {}
    for name in name_counts:
        canonical = canonical_map[name]
        if canonical not in entity_stats:
            entity_stats[canonical] = {
                "canonical_name": canonical,
                "variants": [],
                "mention_count": 0,
                "doc_count": 0,
                "type": classifications.get(name, "concept"),
                "degree": len(clean_edges.get(canonical, {})),
                "weighted_degree": sum(clean_edges.get(canonical, {}).values()),
            }
        
        stats = entity_stats[canonical]
        if name != canonical:
            stats["variants"].append(name)
        stats["mention_count"] += name_counts[name]
    
    # Count docs per entity
    entity_docs = defaultdict(set)
    for doc_id, entry in entities.items():
        for name in entry.get("entity_names", []):
            canonical = canonical_map.get(name, name)
            entity_docs[canonical].add(doc_id)
    
    for canonical, docs in entity_docs.items():
        if canonical in entity_stats:
            entity_stats[canonical]["doc_count"] = len(docs)
    
    # Filter: keep only frameworks, methods, and high-signal concepts
    print("\nFiltering...")
    keep_entities = {}
    for name, stats in entity_stats.items():
        etype = stats["type"]
        degree = stats["degree"]
        mentions = stats["mention_count"]
        
        # Keep all frameworks and methods
        if etype in ("framework", "method"):
            keep_entities[name] = stats
        # Keep concepts with sufficient signal
        elif etype == "concept" and degree >= 3 and mentions >= 3:
            keep_entities[name] = stats
        # Keep key people
        elif etype == "person" and mentions >= 3:
            keep_entities[name] = stats
        # Keep key tools
        elif etype == "tool" and mentions >= 5:
            keep_entities[name] = stats
    
    print(f"  After filtering: {len(keep_entities)} entities (from {len(entity_stats)})")
    
    # Filter edges to kept entities only
    final_edges = []
    for src, targets in clean_edges.items():
        if src not in keep_entities:
            continue
        for dst, weight in targets.items():
            if dst not in keep_entities:
                continue
            if src < dst:  # Remove duplicate direction
                final_edges.append({
                    "source": src,
                    "target": dst,
                    "weight": weight,
                })
    
    print(f"  Final edges: {len(final_edges)}")
    
    # Build type breakdown of kept entities
    kept_types = Counter(s["type"] for s in keep_entities.values())
    print(f"\n  Kept by type:")
    for t, c in kept_types.most_common():
        print(f"    {t}: {c}")
    
    # Output clean graph
    output = {
        "metadata": {
            "phase": 1,
            "operation": "graph_cleaning",
            "date": datetime.now().isoformat(),
            "input_entities": len(name_counts),
            "input_edges": "[deduced from relations]",
            "filtered_entities": len(keep_entities),
            "filtered_edges": len(final_edges),
            "type_distribution": dict(kept_types),
        },
        "entities": keep_entities,
        "edges": final_edges,
    }
    
    outpath = f"{OUTDIR}/phase1_clean_graph.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    
    # Also write a summary
    print(f"\n═══ Top Frameworks by Signal ═══")
    frameworks = [(n, s) for n, s in keep_entities.items() if s["type"] == "framework"]
    frameworks.sort(key=lambda x: x[1]["weighted_degree"], reverse=True)
    for name, stats in frameworks[:30]:
        print(f"  {stats['weighted_degree']:4d}d {stats['mention_count']:4d}m {stats['doc_count']:3d}docs  {name}")
    
    print(f"\n✅ Phase 1 complete → {outpath}")


if __name__ == "__main__":
    main()
