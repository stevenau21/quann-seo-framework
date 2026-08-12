#!/usr/bin/env python3
"""
Phase 4 Remediation — Three-Track Unified Script
=================================================
Track 1: Flashcard explosion — flatten Phase 3 methods/evidence/concepts into atomic
         cards, batch-tag target_entity + action_directive via LLM, embed all cards.
Track 2: Span-level grounding — chunk source docs, embed, verify every claim against
         top-3 similar chunks → GROUNDED or UNVERIFIED.
Track 3: Soft overlapping community membership — embed entities, compute framework
         centroids, assign semantic + structural overlap scores.

Output: flashcards.json (with embeddings, verification, cross-memberships)
"""

import json
import time
import sys
import os
import hashlib
import re
from pathlib import Path
from collections import Counter, defaultdict

import requests
import numpy as np
import math

# ─── BM25 Implementation ────────────────────────────────────────────────
# Lightweight BM25 for hybrid retrieval — combines exact keyword overlap
# with vector similarity to solve the Synthesis vs. Direct-Quote Paradox.

class BM25Scorer:
    """BM25 scorer pre-built on a corpus of chunks."""
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.chunks = chunks
        self.N = len(chunks)

        # Tokenize each chunk
        self.tokenized = []
        self.doc_len = []
        for ch in chunks:
            tokens = re.findall(r'[a-zA-Z0-9]+', ch["text"].lower())
            self.tokenized.append(tokens)
            self.doc_len.append(len(tokens))

        self.avgdl = sum(self.doc_len) / max(1, self.N)

        # Compute IDF for all terms
        self.idf = {}
        df = defaultdict(int)
        for tokens in self.tokenized:
            for t in set(tokens):
                df[t] += 1
        for t, d in df.items():
            self.idf[t] = math.log((self.N - d + 0.5) / (d + 0.5) + 1.0)

    def score(self, query_text, doc_idx):
        """BM25 score for a query against document at doc_idx."""
        query_tokens = re.findall(r'[a-zA-Z0-9]+', query_text.lower())
        doc_tokens = self.tokenized[doc_idx]
        dl = self.doc_len[doc_idx]
        score = 0.0
        tf_map = {}
        for t in doc_tokens:
            tf_map[t] = tf_map.get(t, 0) + 1
        for qt in query_tokens:
            if qt not in self.idf:
                continue
            tf = tf_map.get(qt, 0)
            if tf == 0:
                continue
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * dl / max(1, self.avgdl))
            score += self.idf[qt] * numerator / denominator
        return score


# ─── Config ───────────────────────────────────────────────────────────
OLLAMA_BASE = "https://ollama.com/v1"
OLLAMA_CHAT = f"{OLLAMA_BASE}/chat/completions"
OLLAMA_EMBED = "http://192.168.4.148:11434/api/embed"
LLM_MODEL = "deepseek-v4-flash:cloud"
EMBED_MODEL = "nomic-embed-text"

# Load Ollama Cloud API key from Hermes env
import dotenv
_env_path = Path("/.hermes/.env")
if _env_path.exists():
    for _line in _env_path.read_text().split("\n"):
        if _line.startswith("OLLAMA_API_KEY="):
            _api_key = _line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    else:
        _api_key = os.environ.get("OLLAMA_API_KEY", "")
else:
    _api_key = os.environ.get("OLLAMA_API_KEY", "")
print(f"  API key loaded: {'yes' if _api_key else 'NO — check /.hermes/.env'}")

WORKDIR = Path("/home/steve/lightrag-apps/knowledge-synthesis/extractions/koray-gubur")
PHASE3_PATH = WORKDIR / "phase3_extractions_v4_deepseek.json"
PHASE2_PATH = WORKDIR / "phase2_communities.json"
PHASE1_PATH = WORKDIR / "phase1_clean_entities.json"
KV_DOCS_PATH = Path("/home/steve/lightrag-apps/koray-gubur/workspace/kv_store_full_docs.json")

OUTPUT_PATH = WORKDIR / "phase4_flashcards.json"
CHECKPOINT_PATH = WORKDIR / "phase4_checkpoint.json"

RATE_LIMIT = 0.5  # seconds between LLM calls
CHUNK_SIZE = 800   # chars per source doc chunk
CHUNK_OVERLAP = 150
TOP_K_SIMILAR = 3

ACTION_TAXONOMY = ["implement", "avoid", "optimize", "monitor", "understand", "cite"]

# ─── Helpers ───────────────────────────────────────────────────────────

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved {path}")

def save_checkpoint(data):
    save_json(CHECKPOINT_PATH, data)

def load_checkpoint():
    if CHECKPOINT_PATH.exists():
        return load_json(CHECKPOINT_PATH)
    return {}

def call_ollama_chat(prompt, temperature=0.3):
    """Single LLM chat call — returns raw text via Ollama Cloud API."""
    headers = {}
    if _api_key:
        headers["Authorization"] = f"Bearer {_api_key}"
    resp = requests.post(OLLAMA_CHAT, json={
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }, headers=headers, timeout=300)
    time.sleep(RATE_LIMIT)
    return resp.json()["choices"][0]["message"]["content"]

def call_ollama_embed(texts):
    """Embed a list of texts — returns list of vectors."""
    resp = requests.post(OLLAMA_EMBED, json={
        "model": EMBED_MODEL,
        "input": texts
    }, timeout=60)
    time.sleep(0.1)
    return resp.json()["embeddings"]

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)


# ════════════════════════════════════════════════════════════════════════
#  TRACK 1: FLASHCARD EXPLOSION
# ════════════════════════════════════════════════════════════════════════

def flatten_cards(phase3):
    """Flatten all methods, evidence, core_concepts, nuances into atomic cards."""
    cards = []
    extractions = phase3["extractions"]

    for framework_name, fw in extractions.items():
        if not isinstance(fw, dict):
            continue

        # Methods
        methods = fw.get("methods", [])
        if isinstance(methods, list):
            for i, method in enumerate(methods):
                cards.append({
                    "card_id": f"{framework_name}-method-{i:04d}",
                    "framework": framework_name,
                    "card_type": "method",
                    "raw_content": method,
                    "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                    "verification_status": "pending",
                })
        elif isinstance(methods, dict):
            for section, items in methods.items():
                for i, item in enumerate(items):
                    cards.append({
                        "card_id": f"{framework_name}-method-{section}-{i:04d}",
                        "framework": framework_name,
                        "card_type": "method",
                        "raw_content": item,
                        "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                        "verification_status": "pending",
                    })

        # Evidence
        evidence = fw.get("evidence", [])
        if isinstance(evidence, list):
            for i, ev in enumerate(evidence):
                cards.append({
                    "card_id": f"{framework_name}-evidence-{i:04d}",
                    "framework": framework_name,
                    "card_type": "evidence",
                    "raw_content": ev,
                    "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                    "verification_status": "pending",
                })
        elif isinstance(evidence, str) and evidence not in ("not covered in these documents", "not covered in these documents"):
            cards.append({
                "card_id": f"{framework_name}-evidence-0000",
                "framework": framework_name,
                "card_type": "evidence",
                "raw_content": evidence,
                "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                "verification_status": "pending",
            })

        # Core concepts
        for i, concept in enumerate(fw.get("core_concepts", [])):
            cards.append({
                "card_id": f"{framework_name}-concept-{i:04d}",
                "framework": framework_name,
                "card_type": "concept",
                "raw_content": concept,
                "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                "verification_status": "pending",
            })

        # Nuances
        nuances = fw.get("nuances", [])
        if isinstance(nuances, list):
            for i, nu in enumerate(nuances):
                cards.append({
                    "card_id": f"{framework_name}-nuance-{i:04d}",
                    "framework": framework_name,
                    "card_type": "nuance",
                    "raw_content": nu,
                    "source_doc": fw.get("_metadata", {}).get("docs_analyzed", "unknown"),
                    "verification_status": "pending",
                })

    return cards


def build_tagging_prompt(cards_batch):
    """Build prompt for batch-tagging target_entity + action_directive."""
    items = "\n".join(f"[{i}] {c['raw_content'][:300]}" for i, c in enumerate(cards_batch))

    prompt = f"""You are tagging SEO/marketing knowledge claims. For each item below, extract exactly two fields:

1. **target_entity**: The primary entity/thing/concept the claim is about (1-5 words, proper noun if applicable).
   Examples: "PageRank", "FAQ Schema", "BERT", "Crawl Budget", "hreflang", "E-A-T"
2. **action_directive**: The implicit action this claim instructs. Pick ONE from:
   - "implement" — do this, set it up, create it
   - "avoid" — don't do this, it's harmful
   - "optimize" — improve, tune, enhance
   - "monitor" — watch, track, measure
   - "understand" — know this concept, learn this theory
   - "cite" — reference this source/patent/paper

CRITICAL: Return EXACTLY one JSON object for EVERY item listed below — no skips, no omissions.
If you cannot determine the target_entity from the claim, infer the primary noun phrase from the text.
Every claim has a target_entity. For short claims like "Use canonical URLs", the target_entity is "Canonical URLs".
For claims starting with "Implement X", the target_entity is "X".

Return a JSON array with one object per item:
[{{"i": 0, "target_entity": "...", "action_directive": "..."}}, ...]

Items:
{items}"""

    return prompt


def parse_tagging_response(response_text):
    """Extract JSON array from LLM response."""
    # Try direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try extracting JSON array with balanced brackets
    # Non-greedy first, then try smarter extraction
    start = response_text.find('[')
    if start >= 0:
        # Find the matching ] by counting brackets
        depth = 0
        end = -1
        for i in range(start, len(response_text)):
            if response_text[i] == '[':
                depth += 1
            elif response_text[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end > start:
            try:
                return json.loads(response_text[start:end+1])
            except json.JSONDecodeError:
                pass

    print(f"  ⚠ Could not parse tagging response: {response_text[:200]}")
    return []


def run_track1_tagging(cards):
    """Batch-tag all cards with target_entity + action_directive via LLM."""
    checkpoint = load_checkpoint()
    tagged_count = checkpoint.get("tagged_count", 0)

    if tagged_count >= len(cards):
        print(f"  ✓ All {len(cards)} cards already tagged (checkpoint)")
        return cards

    BATCH = 30
    total_batches = (len(cards) + BATCH - 1) // BATCH

    for batch_idx in range(tagged_count // BATCH, total_batches):
        start = batch_idx * BATCH
        end = min(start + BATCH, len(cards))
        batch = cards[start:end]

        print(f"  Tagging batch {batch_idx + 1}/{total_batches} (cards {start}-{end})...")

        prompt = build_tagging_prompt(batch)
        try:
            response = call_ollama_chat(prompt)
            tags = parse_tagging_response(response)

            for tag in tags:
                idx = tag.get("i", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["target_entity"] = tag.get("target_entity", "")
                    batch[idx]["action_directive"] = tag.get("action_directive", "understand")

            # PATCH 2b: Smart fallback for items the LLM skips
            # Infer target_entity from raw_content instead of blanking it
            for idx_in_batch, item in enumerate(batch):
                if "target_entity" not in item or not item.get("target_entity"):
                    # Infer from the claim text — extract first noun phrase
                    text = item["raw_content"]
                    # Try numbered prefix removal: "1. Topic: rest" → "Topic"
                    cleaned = re.sub(r'^[\d]+[.)]\s*', '', text).strip()
                    # Try colon prefix: "Topic: rest" → "Topic"
                    if ':' in cleaned:
                        cleaned = cleaned.split(':')[0].strip()
                    # Cap at 5 words, take the meaningful part
                    words = cleaned.split()[:5]
                    entity = ' '.join(words) if words else 'Unknown'
                    item["target_entity"] = entity
                    item["action_directive"] = "understand"
                    print(f"    Inferring tag for card [{idx_in_batch}]: '{entity}' from '{text[:80]}...'")

            checkpoint["tagged_count"] = end
            save_checkpoint(checkpoint)

        except Exception as e:
            print(f"  ⚠ Batch {batch_idx} failed: {e}")
            # Fill with defaults so we can continue
            for item in batch:
                item["target_entity"] = ""
                item["action_directive"] = "understand"
            checkpoint["tagged_count"] = end
            save_checkpoint(checkpoint)

    return cards


def embed_cards(cards):
    """Embed all cards in batches."""
    checkpoint = load_checkpoint()
    embed_count = checkpoint.get("embed_count", 0)

    if embed_count >= len(cards):
        print(f"  ✓ All {len(cards)} cards already embedded (checkpoint)")
        return cards

    BATCH = 50
    # Load framework definitions for semantic enrichment of embedding text.
    # With scoped search, these definitions only add signal (not cross-framework noise)
    # because cards only search within their own framework's documents.
    fw_defns = {}
    try:
        with open(PHASE3_PATH) as f:
            _p3 = json.load(f)
        _extr = _p3.get("extractions", _p3) if isinstance(_p3, dict) else {}
        for _fw_name, _fw_data in _extr.items():
            if isinstance(_fw_data, dict):
                defn = _fw_data.get("definition", "")
                # Use first 150 chars of definition — enough for semantic anchoring
                fw_defns[_fw_name] = defn[:150] if defn else ""
    except Exception:
        pass

    texts = []
    for c in cards:
        defn = fw_defns.get(c["framework"], "")
        if defn:
            texts.append(f"{c['framework']} | {c['card_type']}: {c['raw_content']} | context: {defn}")
        else:
            texts.append(f"{c['framework']} | {c['card_type']}: {c['raw_content']}")
    all_embeddings = []

    # Load previously embedded
    for c in cards[:embed_count]:
        if "embedding" in c:
            all_embeddings.append(c["embedding"])

    for batch_idx in range(embed_count // BATCH, (len(cards) + BATCH - 1) // BATCH):
        start = batch_idx * BATCH
        end = min(start + BATCH, len(cards))
        batch_texts = texts[start:end]

        print(f"  Embedding batch {batch_idx + 1} ({start}-{end})...")

        try:
            embeddings = call_ollama_embed(batch_texts)
            for i, emb in enumerate(embeddings):
                cards[start + i]["embedding"] = emb
            checkpoint["embed_count"] = end
            save_checkpoint(checkpoint)
        except Exception as e:
            print(f"  ⚠ Embed batch {batch_idx} failed: {e}")

    return cards


# ════════════════════════════════════════════════════════════════════════
#  TRACK 2: SPAN-LEVEL GROUNDING
# ════════════════════════════════════════════════════════════════════════

def chunk_source_docs(kv_docs):
    """Split source documents into overlapping chunks."""
    chunks = []
    for doc_id, doc_data in kv_docs.items():
        content = doc_data.get("content", "") if isinstance(doc_data, dict) else str(doc_data)
        if not content or len(content) < 50:
            continue

        # Simple word-based chunking
        words = content.split()
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_words = words[i:i + CHUNK_SIZE]
            chunk_text = " ".join(chunk_words)
            if len(chunk_text) > 30:
                chunks.append({
                    "chunk_id": f"{doc_id}-chunk-{i // (CHUNK_SIZE - CHUNK_OVERLAP):04d}",
                    "doc_id": doc_id,
                    "text": chunk_text,
                    "start_pos": i,
                })

    print(f"  Chunked into {len(chunks)} chunks from {len(kv_docs)} docs")
    return chunks


def embed_chunks(chunks):
    """Embed all source doc chunks."""
    checkpoint = load_checkpoint()
    embed_count = checkpoint.get("chunk_embed_count", 0)

    if embed_count >= len(chunks):
        print(f"  ✓ All {len(chunks)} chunks already embedded (checkpoint)")
        return chunks

    BATCH = 50
    texts = [c["text"][:1000] for c in chunks]

    for batch_idx in range(embed_count // BATCH, (len(chunks) + BATCH - 1) // BATCH):
        start = batch_idx * BATCH
        end = min(start + BATCH, len(chunks))
        batch_texts = texts[start:end]

        print(f"  Embedding chunks {start}-{end}/{len(chunks)}...")

        try:
            embeddings = call_ollama_embed(batch_texts)
            for i, emb in enumerate(embeddings):
                chunks[start + i]["embedding"] = emb
            checkpoint["chunk_embed_count"] = end
            save_checkpoint(checkpoint)
        except Exception as e:
            print(f"  ⚠ Chunk embed batch {batch_idx} failed: {e}")

    return chunks


def verify_cards_against_chunks(cards, chunks, fw_doc_ids=None, top_k=5):
    """For each card, find top-k chunks via HYBRID BM25+vector scoring, scoped to framework's doc_ids.
    
    Then verify via batch LLM using MULTI-CHUNK AGGREGATE evaluation:
    the claim is GROUNDED if the combination of the provided chunks explicitly states
    all components of the claim — even if no single chunk contains it verbatim.
    
    Args:
        cards: list of flashcard dicts (each has 'framework', 'embedding')
        chunks: list of chunk dicts (each has 'doc_id', 'embedding', 'text')
        fw_doc_ids: dict mapping framework_name → set of doc_ids to scope search to
        top_k: number of chunks to retrieve per card (default 5 for multi-chunk eval)
    """
    checkpoint = load_checkpoint()
    verify_count = checkpoint.get("verify_count", 0)

    if verify_count >= len(cards):
        print(f"  ✓ All {len(cards)} cards already verified (checkpoint)")
        return cards

    # Pre-build doc_id → chunks index for O(1) lookup
    chunks_by_doc = defaultdict(list)
    for chunk in chunks:
        chunks_by_doc[chunk["doc_id"]].append(chunk)

    # Pre-build BM25 scorer per framework for hybrid retrieval
    # One BM25 index per framework so keyword scoring is scoped too
    bm25_by_framework = {}
    if fw_doc_ids:
        for fw_name, doc_ids in fw_doc_ids.items():
            fw_chunks = []
            for did in doc_ids:
                fw_chunks.extend(chunks_by_doc.get(did, []))
            if fw_chunks:
                bm25_by_framework[fw_name] = BM25Scorer(fw_chunks)
        print(f"  Built BM25 indices for {len(bm25_by_framework)} frameworks")

    # Pre-compute for speed
    BATCH = 20
    total_batches = (len(cards) + BATCH - 1) // BATCH

    for batch_idx in range(verify_count // BATCH, total_batches):
        start = batch_idx * BATCH
        end = min(start + BATCH, len(cards))
        batch_cards = cards[start:end]

        print(f"  Verifying batch {batch_idx + 1}/{total_batches} (cards {start}-{end})...")

        # For each card, HYBRID BM25 + vector retrieval
        card_chunk_matches = []
        for card in batch_cards:
            if "embedding" not in card:
                card_chunk_matches.append([])
                continue

            card_emb = np.array(card["embedding"])
            fw = card.get("framework", "")

            # Collect candidate chunks scoped to framework
            candidates = []
            candidate_sims = []

            if fw_doc_ids and fw in fw_doc_ids:
                for doc_id in fw_doc_ids[fw]:
                    candidates.extend(chunks_by_doc.get(doc_id, []))
            else:
                candidates = chunks

            if not candidates:
                card_chunk_matches.append([])
                continue

            # Vector similarities
            for chunk in candidates:
                if "embedding" not in chunk:
                    continue
                chunk_emb = np.array(chunk["embedding"])
                sim = cosine_similarity(card_emb, chunk_emb)
                candidate_sims.append(sim)

            # Normalize vector scores to [0,1] for hybrid combination
            vec_scores = np.array(candidate_sims) if candidate_sims else np.array([0.0])
            vec_min, vec_max = np.min(vec_scores), np.max(vec_scores)
            if vec_max - vec_min > 1e-10:
                vec_norm = (vec_scores - vec_min) / (vec_max - vec_min)
            else:
                vec_norm = np.where(vec_scores > 0, 1.0, 0.0)

            # BM25 scores (scoped to framework's BM25 index if available)
            bm25_scorer = bm25_by_framework.get(fw)
            bm25_scores = np.zeros(len(candidates))
            if bm25_scorer:
                for ci, chunk in enumerate(candidates):
                    bm25_scores[ci] = bm25_scorer.score(card["raw_content"], ci)

            # Normalize BM25
            bm_min, bm_max = np.min(bm25_scores), np.max(bm25_scores)
            if bm_max - bm_min > 1e-10:
                bm_norm = (bm25_scores - bm_min) / (bm_max - bm_min)
            else:
                bm_norm = np.where(bm25_scores > 0, 1.0, 0.0)

            # Hybrid score: 0.5 vector + 0.5 BM25
            hybrid_scores = 0.5 * vec_norm + 0.5 * bm_norm

            # Sort by hybrid score, take top_k
            ranked = sorted(enumerate(hybrid_scores), key=lambda x: x[1], reverse=True)
            top_chunks = [candidates[ci] for ci, _ in ranked[:top_k] if ci < len(candidates)]
            card_chunk_matches.append(top_chunks)

        # Build MULTI-CHUNK AGGREGATE verification prompt
        items_text = []
        for i, (card, matches) in enumerate(zip(batch_cards, card_chunk_matches)):
            claim = card["raw_content"][:300]
            chunks_text = "\n---\n".join(
                f"Chunk [{j}] (doc={c.get('doc_id','?')[:30]}): {c['text'][:350]}"
                for j, c in enumerate(matches)
            )
            items_text.append(f"Claim [{i}]: {claim}\n\nRelevant source chunks (evaluate COLLECTIVELY):\n{chunks_text}")

        separator = "\n\n===\n\n"
        prompt = f"""You are verifying SEO/marketing claims against source documents using MULTI-CHUNK AGGREGATE evaluation.

CRITICAL INSTRUCTION: Phase 3 synthesized claims by combining information from multiple paragraphs. Therefore, you must evaluate whether the AGGREGATE of the provided chunks — taken together — explicitly supports all components of the claim. A claim is GROUNDED if the substance of each component can be found across the chunks, even if no single chunk contains the verbatim statement.

Rules:
- Look for component parts across chunks: "identify entities" in Chunk A + "build attributes" in Chunk B = claim about "identify entities AND attributes" is GROUNDED.
- Do NOT lower the standard — every component must be explicitly stated somewhere.
- Do NOT accept inference or implication — the text must clearly state each part.
- If any component of the claim is missing from all chunks combined, mark UNVERIFIED.

For each claim, return ONE entry:
- "GROUNDED" — components are found across chunks (cite brief quotes + chunk indices for each)
- "UNVERIFIED" — one or more components are missing

Return a JSON array: [{{"i": 0, "status": "GROUNDED", "span": "Chunk[1]: 'topical map with entities' + Chunk[2]: 'add attributes'"}}, ...]

{separator.join(items_text)}"""

        try:
            response = call_ollama_chat(prompt)
            verifications = parse_tagging_response(response)

            for v in verifications:
                idx = v.get("i", -1)
                if 0 <= idx < len(batch_cards):
                    batch_cards[idx]["verification_status"] = v.get("status", "UNVERIFIED")
                    batch_cards[idx]["source_span"] = v.get("span", "")

            # Fill defaults
            for item in batch_cards:
                if "source_span" not in item:
                    item["source_span"] = ""
                if item.get("verification_status") == "pending":
                    item["verification_status"] = "UNVERIFIED"

            checkpoint["verify_count"] = end
            save_checkpoint(checkpoint)

        except Exception as e:
            print(f"  ⚠ Verify batch {batch_idx} failed: {e}")
            for item in batch_cards:
                item["verification_status"] = "UNVERIFIED"
                item["source_span"] = ""
            checkpoint["verify_count"] = end
            save_checkpoint(checkpoint)

    return cards


# ════════════════════════════════════════════════════════════════════════
#  TRACK 3: SOFT OVERLAPPING COMMUNITY MEMBERSHIP
# ════════════════════════════════════════════════════════════════════════

def get_framework_entities(phase2):
    """Build framework→entity mapping from Phase 2 communities."""
    # Phase 2 has 375 raw communities. We need to map them to our 12 frameworks.
    # Since they're Louvain communities, each entity belongs to exactly one community.
    # We build an entity→community_id map.

    entity_to_community = {}
    community_entities = defaultdict(list)

    for comm in phase2["communities"]:
        cid = comm["community_id"]
        for entity in comm.get("all_entities", []):
            entity_to_community[entity] = cid
            community_entities[cid].append(entity)

    return entity_to_community, community_entities


def compute_framework_centroids(entity_embeddings, community_entities):
    """Compute centroid vector for each community."""
    centroids = {}
    for cid, entities in community_entities.items():
        vectors = []
        for e in entities:
            if e in entity_embeddings:
                vectors.append(np.array(entity_embeddings[e]))
        if vectors:
            centroids[cid] = np.mean(vectors, axis=0)
    return centroids


def compute_soft_membership(cards, entity_embeddings, entity_to_community, centroids, community_entities):
    """For each card's target_entity, compute cross-framework membership scores."""
    checkpoint = load_checkpoint()
    if checkpoint.get("soft_membership_done"):
        print("  ✓ Soft membership already computed (checkpoint)")
        return cards

    # Build entity→framework mapping (community_id → framework name)
    # We need to figure out which community maps to which framework
    # Strategy: use the card's framework field to vote on community→framework mapping
    framework_votes = defaultdict(lambda: defaultdict(int))

    for card in cards:
        entity = card.get("target_entity", "")
        fw = card.get("framework", "")
        if entity and entity in entity_to_community:
            cid = entity_to_community[entity]
            framework_votes[cid][fw] += 1

    # Map each community to its dominant framework
    community_to_framework = {}
    for cid, votes in framework_votes.items():
        dominant = max(votes, key=votes.get)
        community_to_framework[cid] = dominant

    # Now compute cross-memberships
    entity_to_framework = {}
    for entity, cid in entity_to_community.items():
        entity_to_framework[entity] = community_to_framework.get(cid, f"community_{cid}")

    # For each card, compute soft membership to all 12 frameworks
    # Semantic: cosine similarity of entity embedding to each framework centroid
    # Structural (simplified): based on community overlap

    for card in cards:
        entity = card.get("target_entity", "")
        fw = card.get("framework", "")
        memberships = []

        if entity in entity_embeddings:
            entity_vec = np.array(entity_embeddings[entity])

            for cid, centroid in centroids.items():
                target_fw = community_to_framework.get(cid, f"community_{cid}")
                entity_cid = entity_to_community.get(entity)

                # Skip: same community OR same framework (self-comparison)
                if cid == entity_cid or target_fw == fw:
                    continue

                sem_sim = float(cosine_similarity(entity_vec, centroid))

                # Structural: Jaccard overlap between entity's community and target community
                # Louvain partitions are disjoint, but entity names may appear in multiple
                # community all_entities lists from LightRAG extraction
                struct_score = 0.0
                if entity_cid and entity_cid in community_entities and cid in community_entities:
                    source_set = set(community_entities[entity_cid])
                    target_set = set(community_entities[cid])
                    intersection = len(source_set & target_set)
                    union = len(source_set | target_set)
                    if union > 0:
                        struct_score = intersection / union  # Jaccard similarity

                # Combined score (weighted 0.6 semantic, 0.4 structural)
                combined = 0.6 * sem_sim + 0.4 * struct_score

                if combined > 0.3:  # Threshold for meaningful membership
                    memberships.append({
                        "framework": target_fw,
                        "semantic_similarity": round(sem_sim, 4),
                        "structural_overlap": round(struct_score, 4),
                        "combined_score": round(combined, 4),
                    })

        memberships.sort(key=lambda x: x["combined_score"], reverse=True)
        card["cross_framework_memberships"] = memberships[:5]  # Top 5

    checkpoint["soft_membership_done"] = True
    save_checkpoint(checkpoint)
    return cards


# ════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Phase 4 Remediation — Three-Track Pipeline")
    print("=" * 60)

    # ── Load inputs ──
    print("\n📂 Loading input files...")
    phase3 = load_json(PHASE3_PATH)
    phase2 = load_json(PHASE2_PATH)

    if KV_DOCS_PATH.exists():
        kv_docs = load_json(KV_DOCS_PATH)
        print(f"  ✓ Loaded {len(kv_docs)} source documents")
    else:
        print("  ⚠ kv_store_full_docs.json not found — Track 2 will be skipped")
        kv_docs = {}

    # ── Track 1: Flatten + Tag + Embed ──
    print("\n🏷️  TRACK 1: Flashcard Explosion")

    cards = flatten_cards(phase3)
    print(f"  Flattened {len(cards)} atomic cards")
    print(f"    Types: {dict(Counter(c['card_type'] for c in cards))}")

    print("\n  Step 1a: Batch-tagging target_entity + action_directive...")
    cards = run_track1_tagging(cards)
    tagged = sum(1 for c in cards if c.get("target_entity"))
    print(f"  Tagged: {tagged}/{len(cards)} cards")

    print("\n  Step 1b: Embedding all cards...")
    cards = embed_cards(cards)
    embedded = sum(1 for c in cards if c.get("embedding"))
    print(f"  Embedded: {embedded}/{len(cards)} cards")

    # ── Track 2: Span Grounding ──
    if kv_docs:
        print("\n🔍 TRACK 2: Span-Level Grounding")

        print("  Step 2a: Chunking source documents...")
        chunks = chunk_source_docs(kv_docs)

        print("  Step 2b: Embedding chunks...")
        chunks = embed_chunks(chunks)

        print("  Step 2c: Building framework→doc_ids lookup from Phase 3...")
        framework_doc_ids = {}
        for fw_name, fw_data in phase3.get("extractions", {}).items():
            if isinstance(fw_data, dict):
                doc_ids = fw_data.get("_metadata", {}).get("doc_ids", [])
                if doc_ids:
                    framework_doc_ids[fw_name] = set(doc_ids)
        scope_count = sum(1 for c in cards if c["framework"] in framework_doc_ids)
        print(f"  Framework→doc_ids mapped: {len(framework_doc_ids)} frameworks, {scope_count}/{len(cards)} cards scoped")

        print("  Step 2d: Verifying cards against SCOPED chunks...")
        cards = verify_cards_against_chunks(cards, chunks, framework_doc_ids)

        statuses = Counter(c.get("verification_status") for c in cards)
        print(f"  Verification: {dict(statuses)}")
    else:
        print("\n⏭️  TRACK 2: SKIPPED (no source documents)")

    # ── Track 3: Soft Membership ──
    print("\n🔗 TRACK 3: Soft Overlapping Community Membership")

    print("  Step 3a: Building entity→community mapping...")
    entity_to_community, community_entities = get_framework_entities(phase2)

    # Get entity embeddings — embed with RICH AGGREGATE CONTEXT, not bare names
    print("  Step 3b: Building entity context aggregates...")
    # Build entity → aggregate context from all cards that reference it
    entity_contexts = defaultdict(list)
    for card in cards:
        entity = card.get("target_entity", "")
        if entity:
            entity_contexts[entity].append(f"[{card['framework']}/{card['card_type']}]: {card['raw_content'][:200]}")

    print("  Step 3c: Embedding entities with rich context...")
    all_entities = list(entity_to_community.keys())
    entity_embeddings = {}

    BATCH = 50
    for i in range(0, len(all_entities), BATCH):
        batch = all_entities[i:i + BATCH]
        # Use aggregate context if available, else entity name
        batch_texts = []
        for e in batch:
            if e in entity_contexts:
                aggregate = f"Entity: {e}\n" + "\n".join(entity_contexts[e][:5])
                batch_texts.append(aggregate)
            else:
                batch_texts.append(e)
        print(f"    Embedding entities {i}-{i + len(batch)}/{len(all_entities)}...")
        try:
            embs = call_ollama_embed(batch_texts)
            for entity, emb in zip(batch, embs):
                entity_embeddings[entity] = emb
        except Exception as e:
            print(f"    ⚠ Entity embed batch {i} failed: {e}")

    print(f"  Embedded {len(entity_embeddings)} entities")

    print("  Step 3c: Computing framework centroids...")
    centroids = compute_framework_centroids(entity_embeddings, community_entities)
    print(f"  Computed {len(centroids)} centroids")

    print("  Step 3d: Computing soft cross-framework memberships...")
    cards = compute_soft_membership(
        cards, entity_embeddings, entity_to_community,
        centroids, community_entities
    )

    cards_with_membership = sum(
        1 for c in cards if c.get("cross_framework_memberships")
    )
    print(f"  Cards with cross-memberships: {cards_with_membership}/{len(cards)}")

    # ── Finalize ──
    print("\n📊 Building final output...")

    # Strip embeddings for cleaner output (they're huge arrays)
    # Keep them but validate
    output = {
        "metadata": {
            "phase": 4,
            "tracks": ["flashcard_explosion", "span_grounding", "soft_membership"],
            "total_cards": len(cards),
            "card_types": dict(Counter(c["card_type"] for c in cards)),
            "frameworks": sorted(set(c["framework"] for c in cards)),
            "verification": dict(Counter(c.get("verification_status", "pending") for c in cards)),
            "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": LLM_MODEL,
            "embed_model": EMBED_MODEL,
        },
        "cards": cards,
    }

    save_json(OUTPUT_PATH, output)

    # ── Summary ──
    print("\n" + "=" * 60)
    print("✅ PHASE 4 COMPLETE")
    print("=" * 60)
    print(f"  Total cards: {len(cards)}")
    print(f"  Tagged (target_entity): {tagged}/{len(cards)}")
    print(f"  Embedded: {embedded}/{len(cards)}")
    print(f"  Verified: {statuses if kv_docs else 'N/A'}")
    print(f"  Cross-memberships: {cards_with_membership}")
    print(f"  Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
