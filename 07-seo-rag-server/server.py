"""
SEO RAG Chatbot — replaces Dify for quann.homes widget.
Multi-app: Holistic SEO Assistant + Quan Homes Chatbot
Embedding: nomic-embed-text-v2-moe (via Ollama)
Vector DB: Weaviate (reusing Dify's indexed data)
LLM: deepseek-v4-pro:cloud (via Ollama v1)
Storage: SQLite (sessions, blocklist, rate limits)
"""
import os, json, time, sqlite3, hashlib, asyncio
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

# ── CONFIG ──────────────────────────────────────────────────
OLLAMA_BASE = "https://ollama.quann.homes"
OLLAMA_CLOUD_BASE = "https://ollama.com"
WEAVIATE_HOST = "http://localhost:8080"
WEAVIATE_KEY = "WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih"
EMBED_MODEL = "nomic-embed-text-v2-moe"
CHAT_MODEL = "gemma4:31b-cloud"
DB_PATH = os.path.join(os.path.dirname(__file__), "seo_rag.db")
ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "hermes-admin-seo-rag-2026")
SESSION_TTL_HOURS = 24
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 10
MAX_CONTEXT_CHUNKS = 50
RRF_K = 60  # RRF smoothing constant
KEYWORD_SEARCH_CHUNKS = 100  # fetch more from BM25 for fusion
VECTOR_SEARCH_CHUNKS = 80    # fetch more from vector for fusion
DISTANCE_THRESHOLD = 0.35    # max cosine distance (lower = more relevant)

# ── APP DEFINITIONS ─────────────────────────────────────────
APPS = {
    "app-P0f44B7WF56gLXB1DexRWNfc": {
        "id": "holistic_seo",
        "name": "Holistic SEO Assistant",
        "weaviate_class": "Vector_index_c8b822da_da9e_4b7f_b7fb_005d7e23ebb3_Node",
        "system_prompt": """You are Holistic SEO Assistant, an expert SEO consultant trained on holisticseo.digital. Answer the user's question using ONLY the provided context below. If the context doesn't contain the answer, say "I don't have enough information about that in my knowledge base." but still try to provide general SEO guidance when relevant.

Keep answers concise and actionable. Use bullet points for lists. Cite specific sources when possible.

CONTEXT:
{context}""",
    },
    "app-2432fa8de1034c60917bcf437ef935c8": {
        "id": "quan_homes",
        "name": "Quan Homes Chatbot",
        "weaviate_class": "Vector_index_c7b711da_c9cb_4b7e_b6ea_004d6e12dba2_Node",
        "system_prompt": """You are Quan Homes AI Assistant, a helpful real estate chatbot for Quan Nguyen, a real estate agent in Katy, Texas. You help potential home buyers and sellers with questions about properties, the home buying process, and Quan's services.

Answer the user's question using the provided context. If the context doesn't have the answer, you can draw on your knowledge of real estate to be helpful. Always be professional, warm, and encouraging. If someone needs to speak with Quan directly, let them know you can arrange that.

Keep responses conversational and helpful. Use bullet points for lists.

CONTEXT:
{context}""",
    },
}

# ── DATABASE ─────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            app_id TEXT NOT NULL,
            ip_hash TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
        CREATE TABLE IF NOT EXISTS blocklist (
            ip_hash TEXT PRIMARY KEY,
            blocked_at TEXT NOT NULL,
            reason TEXT
        );
        CREATE TABLE IF NOT EXISTS rate_limits (
            ip_hash TEXT NOT NULL,
            minute_bucket TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            PRIMARY KEY (ip_hash, minute_bucket)
        );
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="SEO RAG", version="2.0", lifespan=lifespan)

# ── HELPERS ──────────────────────────────────────────────────
def hash_ip(ip: str) -> str:
    return hashlib.sha256(f"{ip}-seo-rag".encode()).hexdigest()[:16]

def get_app_config(token: str) -> dict | None:
    return APPS.get(token)

def check_blocked(ip_hash: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT 1 FROM blocklist WHERE ip_hash = ?", (ip_hash,)).fetchone()
    conn.close()
    return row is not None

def check_rate_limit(ip_hash: str) -> bool:
    now = datetime.now(timezone.utc)
    bucket = now.strftime("%Y-%m-%dT%H:%M")
    conn = get_db()
    row = conn.execute(
        "SELECT count FROM rate_limits WHERE ip_hash = ? AND minute_bucket = ?",
        (ip_hash, bucket)
    ).fetchone()
    if row:
        if row["count"] >= RATE_LIMIT_MAX:
            conn.close()
            return True
        conn.execute(
            "UPDATE rate_limits SET count = count + 1 WHERE ip_hash = ? AND minute_bucket = ?",
            (ip_hash, bucket)
        )
    else:
        conn.execute(
            "INSERT INTO rate_limits (ip_hash, minute_bucket, count) VALUES (?, ?, 1)",
            (ip_hash, bucket)
        )
    conn.commit()
    conn.close()
    return False

async def generate_embedding(text: str) -> list[float] | None:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": f"search_query: {text}"}
            )
            if r.status_code == 200:
                return r.json()["embedding"]
    except Exception as e:
        print(f"[EMBED] {e}")
    return None

async def bm25_search(text: str, weaviate_class: str, limit: int = 100) -> list[dict]:
    """Keyword search using Weaviate's native BM25 (bm25 operator)."""
    query = {
        "query": f"""
        {{ Get {{
            {weaviate_class}(
                bm25: {{ query: {json.dumps(text)} }}
                limit: {limit}
            ) {{
                text
                document_id
                doc_type
                _additional {{ score }}
            }}
        }} }}
        """
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{WEAVIATE_HOST}/v1/graphql",
                headers={
                    "Authorization": f"Bearer {WEAVIATE_KEY}",
                    "Content-Type": "application/json"
                },
                json=query
            )
            if r.status_code == 200:
                data = r.json()
                objs = data.get("data", {}).get("Get", {}).get(weaviate_class, [])
                return [
                    {
                        "text": o["text"],
                        "document_id": o.get("document_id", ""),
                        "doc_type": o.get("doc_type", ""),
                        "score": o["_additional"].get("score", 0)
                    }
                    for o in objs
                ]
    except Exception as e:
        print(f"[BM25] {e}")
    return []


async def vector_search(vector: list[float], weaviate_class: str, limit: int = 80) -> list[dict]:
    """Pure vector similarity search."""
    query = {
        "query": f"""
        {{ Get {{
            {weaviate_class}(
                limit: {limit}
                nearVector: {{ vector: {json.dumps(vector)} }}
            ) {{
                text
                document_id
                doc_type
                _additional {{ distance }}
            }}
        }} }}
        """
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{WEAVIATE_HOST}/v1/graphql",
                headers={
                    "Authorization": f"Bearer {WEAVIATE_KEY}",
                    "Content-Type": "application/json"
                },
                json=query
            )
            if r.status_code == 200:
                data = r.json()
                objs = data.get("data", {}).get("Get", {}).get(weaviate_class, [])
                return [
                    {
                        "text": o["text"],
                        "document_id": o.get("document_id", ""),
                        "doc_type": o.get("doc_type", ""),
                        "distance": o["_additional"]["distance"],
                        "score": 1.0 - o["_additional"]["distance"]  # convert to similarity
                    }
                    for o in objs
                ]
    except Exception as e:
        print(f"[VECTOR] {e}")
    return []


async def search_vectors(
    query_text: str, weaviate_class: str, top_k: int = MAX_CONTEXT_CHUNKS
) -> list[dict]:
    """
    Two-stage Retrieval with Reciprocal Rank Fusion (RRF).
    
    1. Run BM25 keyword search + vector similarity search in parallel
    2. Fuse results with RRF: score = sum(1 / (k + rank)) per chunk
    3. Deduplicate by text hash, sort by RRF score
    4. Return top_k results
    """
    # Generate embedding for vector search
    emb = await generate_embedding(query_text)
    
    if emb:
        # Run both searches in parallel
        bm25_results, vec_results = await asyncio.gather(
            bm25_search(query_text, weaviate_class, KEYWORD_SEARCH_CHUNKS),
            vector_search(emb, weaviate_class, VECTOR_SEARCH_CHUNKS),
            return_exceptions=True
        )
    else:
        # Fallback to keyword-only if embedding fails
        bm25_results = await bm25_search(query_text, weaviate_class, KEYWORD_SEARCH_CHUNKS)
        vec_results = []
    
    if isinstance(bm25_results, Exception):
        bm25_results = []
    if isinstance(vec_results, Exception):
        vec_results = []
    
    # RRF fusion: track best chunk per unique text
    rrf_scores = {}  # text_hash -> (rrf_score, full_chunk_dict)
    
    def text_hash(txt: str) -> str:
        return hashlib.md5(txt[:200].encode()).hexdigest()
    
    # Fuse BM25 results (rank-based)
    for rank, chunk in enumerate(bm25_results):
        h = text_hash(chunk["text"])
        rrf = 1.0 / (RRF_K + rank + 1)
        if h not in rrf_scores or rrf > rrf_scores[h][0]:
            rrf_scores[h] = (rrf, chunk)
    
    # Fuse vector results (rank-based)
    for rank, chunk in enumerate(vec_results):
        h = text_hash(chunk["text"])
        rrf = 1.0 / (RRF_K + rank + 1)
        if h not in rrf_scores or rrf > rrf_scores[h][0]:
            existing = rrf_scores.get(h, (0, chunk))
            rrf_scores[h] = (existing[0] + rrf, chunk)
    
    # Sort by RRF score, take top_k
    sorted_results = sorted(rrf_scores.values(), key=lambda x: x[0], reverse=True)
    final = [chunk for _, chunk in sorted_results[:top_k]]
    
    # Log retrieval stats
    print(f"[RRF] query='{query_text[:80]}' | BM25={len(bm25_results)} + vec={len(vec_results)} → {len(final)} unique (top_k={top_k})")
    if final:
        print(f"[RRF] top-3 RRF: {sorted_results[0][0]:.4f} | {sorted_results[1][0]:.4f} | {sorted_results[2][0]:.4f}" if len(sorted_results) >= 3 else f"[RRF] top RRF: {sorted_results[0][0]:.4f}")
    
    return final

async def call_llm(messages: list[dict]) -> str:
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/v1/chat/completions",
                json={
                    "model": CHAT_MODEL,
                    "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
                    "temperature": 0.3,
                    "max_tokens": 64000,
                    "stream": False
                },
                headers={}
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[LLM] {e}")
    return "Sorry, I'm having trouble connecting. Please try again in a moment."

def build_system_prompt(template: str, chunks: list[dict]) -> str:
    context_text = "\n\n".join([
        f"[Relevance: {c.get('score', 1 - c.get('distance', 0.5)):.0%}] {c['text']}"
        for c in chunks
    ])
    return template.format(context=context_text)

def get_session_history(session_id: str, limit: int = 10) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def save_message(session_id: str, role: str, content: str):
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()

# ── API ENDPOINTS ────────────────────────────────────────────
@app.post("/v1/chat-messages")
async def chat_messages(request: Request):
    # Auth
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "")
    app_config = get_app_config(token)
    if not app_config:
        raise HTTPException(status_code=401, detail="Invalid API token")

    # IP tracking + security
    ip = request.client.host if request.client else "unknown"
    ip_hash = hash_ip(ip)
    if check_blocked(ip_hash):
        raise HTTPException(status_code=403, detail="Access denied")
    if check_rate_limit(ip_hash):
        raise HTTPException(status_code=429, detail="Too many requests")

    # Parse body
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    query = body.get("query", "").strip()
    conversation_id = body.get("conversation_id", "")
    user = body.get("user", "anonymous")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    # Session
    session_id = conversation_id or hashlib.sha256(
        f"{ip_hash}:{app_config['id']}:{time.time()}".encode()
    ).hexdigest()[:24]

    conn = get_db()
    existing = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if not existing:
        now = datetime.now(timezone.utc)
        conn.execute(
            "INSERT INTO sessions (id, app_id, ip_hash, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, app_config["id"], ip_hash, now.isoformat(),
             (now + timedelta(hours=SESSION_TTL_HOURS)).isoformat())
        )
        conn.commit()
    conn.close()

    # Search with RRF (handles embedding internally)
    chunks = await search_vectors(query, app_config["weaviate_class"])

    # Build messages
    system_prompt = build_system_prompt(app_config["system_prompt"], chunks)
    history = get_session_history(session_id)
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": query}
    ]

    save_message(session_id, "user", query)
    answer = await call_llm(messages)
    save_message(session_id, "assistant", answer)

    return JSONResponse({
        "answer": answer,
        "conversation_id": session_id,
        "retriever_resources": [
            {"document_id": c.get("document_id", ""), "content": c["text"][:200]}
            for c in chunks[:3]
        ]
    })

@app.get("/health")
async def health():
    return {"status": "ok", "apps": list(APPS.keys()), "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/v1/admin/block")
async def block_ip(request: Request):
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {ADMIN_KEY}":
        raise HTTPException(status_code=401, detail="Admin access required")

    body = await request.json()
    ip = body.get("ip", "")
    reason = body.get("reason", "manual block")
    if not ip:
        raise HTTPException(status_code=400, detail="IP required")

    ip_hash = hash_ip(ip)
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO blocklist (ip_hash, blocked_at, reason) VALUES (?, ?, ?)",
        (ip_hash, datetime.now(timezone.utc).isoformat(), reason)
    )
    conn.commit()
    conn.close()
    return {"status": "blocked", "ip": ip, "ip_hash": ip_hash}

@app.get("/v1/admin/stats")
async def stats(request: Request):
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {ADMIN_KEY}":
        raise HTTPException(status_code=401, detail="Admin access required")

    conn = get_db()
    active_sessions = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE expires_at > ?",
        (datetime.now(timezone.utc).isoformat(),)
    ).fetchone()[0]
    total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    blocked_ips = conn.execute("SELECT COUNT(*) FROM blocklist").fetchone()[0]
    conn.close()
    return {
        "active_sessions": active_sessions,
        "total_messages": total_messages,
        "blocked_ips": blocked_ips
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
