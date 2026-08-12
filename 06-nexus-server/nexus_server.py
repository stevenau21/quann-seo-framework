"""
nexus_server.py — Unified Nexus server with multiple notebooks on one port.
Replaces separate quann-chat/server.py and seo-methodology/server.py.

Architecture:
  GET  /health          → all notebooks status
  POST /chat            → quann-chat notebook (Quan's real estate KG)
  POST /seo             → seo-methodology notebook (SEO research KG)

Each notebook has its own LightRAG workspace, LLM, system prompt, and reranker.
All share the same nexus_shared engine (classifier, citations, conflict resolution).
"""
import sys, asyncio, logging, socket, time as _time
from pathlib import Path
from contextlib import asynccontextmanager

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/steve/lightrag-env/lib/python3.11/site-packages")
sys.path.insert(0, "/home/steve/lightrag-apps")

import requests, socket, os
from requests.adapters import HTTPAdapter

# ── Ollama Cloud API key ───────────────────────────────────────────────────
_OLLAMA_CLOUD_API_KEY: str | None = None
_OLLAMA_CLOUD_BASE = "https://ollama.com"

def _load_cloud_api_key():
    global _OLLAMA_CLOUD_API_KEY
    if _OLLAMA_CLOUD_API_KEY is not None:
        return
    # Try env var first, then /.hermes/.env file
    _OLLAMA_CLOUD_API_KEY = os.environ.get("OLLAMA_CLOUD_API_KEY") or os.environ.get("OLLAMA_API_KEY")
    if not _OLLAMA_CLOUD_API_KEY:
        env_paths = ["/.hermes/.env", "/home/steve/.hermes/.env"]
        for env_path in env_paths:
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OLLAMA_API_KEY=") or line.startswith("OLLAMA_CLOUD_API_KEY="):
                            _OLLAMA_CLOUD_API_KEY = line.split("=", 1)[1].strip()
                            break
                if _OLLAMA_CLOUD_API_KEY:
                    break
            except FileNotFoundError:
                continue
    if _OLLAMA_CLOUD_API_KEY:
        logger.info("Ollama Cloud API key loaded (%d chars)", len(_OLLAMA_CLOUD_API_KEY))
    else:
        logger.warning("No Ollama Cloud API key found — :cloud models will fail")

class TCPKeepAliveAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs.setdefault("socket_options", [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10),
            (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5),
            (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3),
        ])
        super().init_poolmanager(*args, **kwargs)

import nexus_shared
from nexus_shared import NotebookConfig, classify_query, extract_citations, make_rerank_func, start_reranker

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from pydantic import BaseModel, Field

logger = logging.getLogger("nexus-server")
logger.setLevel(logging.WARNING)

# ── Notebook definitions ───────────────────────────────────────────────────

CHAT_SYSTEM_PROMPT = """You are Quan Nguyen's real estate assistant on quann.homes.
You help home buyers, sellers, and investors in Texas — friendly, warm, professional.

## Key Facts
- Quan Nguyen, license #0774451, brokerage: REAL BROKERAGE
- Brand: Quann Home / The Quantum Team
- Phone: (832) 400-3152 | Email: quan@thequantumteam.net
- Based in Katy, TX — serves all of Texas (Houston, Austin, Dallas, Rio Grande Valley)

## How to respond
- Use emojis occasionally — keep it warm
- Use the CONTEXT below to answer questions about Quan's services, neighborhoods, processes
- If context doesn't cover something, be honest and suggest contacting Quan directly
- Keep responses concise but thorough (2-5 sentences usually)
- When someone asks about scheduling, direct them to click "Schedule a Call" on the site

""" + nexus_shared.CONFLICT_RESOLUTION_INSTRUCTION + """

## CONTEXT FROM QUANN.HOMES:
{context}"""

SEO_SYSTEM_PROMPT = """You are an expert SEO research assistant drawing from holisticseo.digital.
You answer in-depth questions about SEO methodology, content strategy, entity-based SEO,
topical maps, and technical SEO concepts.

## How to respond
- Be thorough but clear — explain concepts, don't just list definitions
- Connect ideas across different SEO disciplines when relevant
- Use concrete examples from the knowledge base
- Structure longer answers with clear sections when helpful
- If the context doesn't fully answer a question, be honest about the gap

""" + nexus_shared.CONFLICT_RESOLUTION_INSTRUCTION + """

## RESEARCH CONTEXT:
{context}"""

CLIENT_SYSTEM_PROMPT = """You are Quan Nguyen's client intelligence analyst.
You analyze meeting transcripts, buyer consultations, and client conversations
to help Quan understand what clients really care about — their fears, questions,
objections, and hidden concerns that don't appear in public marketing.

## How to respond
- Analyze client sentiment, recurring themes, and knowledge gaps
- Identify what clients ask about most but Quan hasn't written about
- Use the transcripts to surface patterns: common objections, emotional triggers, unmet needs
- Be specific — quote actual transcript segments (with timestamps) when relevant
- Help Quan bridge the gap between what clients care about and what he publishes

""" + nexus_shared.CONFLICT_RESOLUTION_INSTRUCTION + """

## TRANSCRIPT CONTEXT:
{context}"""

NOTEBOOKS = [
    NotebookConfig(
        name="quann-chat",
        title="Quann Chat",
        workspace="/home/steve/lightrag-apps/quann-chat/workspace",
        fallback_workspace="/home/steve/lightrag-apps/quann-chat/workspace_old",
        llm_model="gemma4:31b-cloud",
        top_k_retrieve=20,
        top_n_rerank=5,
        max_context_chars=4000,
        llm_temperature=0.7,
        llm_max_tokens=500,
        route_path="/chat",
        route_method="chat",
        system_prompt_template=CHAT_SYSTEM_PROMPT,
        embed_dim=768,
        embed_max_tokens=8192,
    ),
    NotebookConfig(
        name="seo-methodology",
        title="SEO Methodology",
        workspace="/home/steve/lightrag-apps/seo-methodology/workspace",
        fallback_workspace="/home/steve/lightrag-apps/seo-methodology/workspace_old",
        llm_model="deepseek-v4-pro:cloud",
        top_k_retrieve=40,
        top_n_rerank=5,
        max_context_chars=6000,
        llm_temperature=0.3,
        llm_max_tokens=1500,
        route_path="/seo",
        route_method="ask",
        system_prompt_template=SEO_SYSTEM_PROMPT,
        embed_dim=768,
        embed_max_tokens=8192,
        use_query_expansion=True,
        expansion_llm_model="gemma4:31b-cloud",
    ),
]

# ── Shared models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    mode: str | None = None  # local, global, hybrid

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    mode_used: str = "hybrid"
    citations: list[str] = Field(default_factory=list)

# ── Notebook runtime ───────────────────────────────────────────────────────

class NotebookRuntime:
    """Holds a single notebook's RAG instance, reranker, and Ollama client."""

    def __init__(self, config: NotebookConfig):
        self.config = config
        self.rag = None
        self.reranker = None
        self.rerank_func = None
        self._resolve_ollama()

    def _resolve_ollama(self):
        _load_cloud_api_key()
        if not self.config.ollama_base_url:
            try:
                host = socket.gethostbyname("host.docker.internal")
            except Exception:
                host = "192.168.4.148"
            self.config.ollama_base_url = f"http://{host}:11434"
        self._session = requests.Session()
        self._session.mount("http://", TCPKeepAliveAdapter())
        # Cloud session (for :cloud models)
        self._cloud_session = requests.Session()

    async def start(self):
        from lightrag import LightRAG, QueryParam
        from lightrag.utils import EmbeddingFunc

        self.reranker = await start_reranker()
        self.rerank_func = make_rerank_func(self.reranker, default_top_n=self.config.top_n_rerank)

        ws = Path(self.config.workspace)
        fallback = Path(self.config.fallback_workspace) if self.config.fallback_workspace else None
        vdb = ws / "vdb_chunks.json"
        if not vdb.exists() or vdb.stat().st_size < 1000:
            logger.warning("%s: workspace corrupted/empty vdb=%s", self.config.name, vdb.exists())
            if fallback and fallback.exists() and (fallback / "vdb_chunks.json").exists():
                logger.warning("%s: falling back to old workspace", self.config.name)
                ws = fallback

        ws.mkdir(parents=True, exist_ok=True)

        self.rag = LightRAG(
            working_dir=str(ws),
            llm_model_func=self._kw_llm,
            embedding_func=EmbeddingFunc(
                embedding_dim=self.config.embed_dim,
                max_token_size=self.config.embed_max_tokens,
                func=self._embed_texts,
            ),
            rerank_model_func=self.rerank_func,
            embedding_func_max_async=self.config.embedding_func_max_async,
            llm_model_max_async=self.config.llm_model_max_async,
            max_parallel_insert=self.config.max_parallel_insert,
        )
        await self.rag.initialize_storages()
        logger.info("%s: ready workspace=%s reranker=%s", self.config.name, ws, self.reranker is not None)

    async def stop(self):
        self.rag = None
        self.reranker = None
        self.rerank_func = None

    async def _kw_llm(self, prompt, system_prompt=None, history_messages=None, **kwargs):
        """LightRAG keyword extraction — calls real LLM just for extract_keywords_only."""
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, self._ollama_sync, "/v1/chat/completions", {
                "model": "gemma4:31b-cloud",
                "temperature": 0.1,
                "max_tokens": 100,
                "messages": [
                    {"role": "system", "content": system_prompt or "Extract keywords as JSON."},
                    {"role": "user", "content": prompt},
                ],
            }, 30)
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return '{"high_level_keywords":[],"low_level_keywords":[]}'

    async def _embed_texts(self, texts: list[str]):
        import numpy as np
        embeddings = []
        loop = asyncio.get_event_loop()
        for text in texts:
            data = await loop.run_in_executor(None, self._ollama_sync, "/api/embeddings",
                {"model": self.config.embed_model, "prompt": f"search_query: {text}"}, 60)
            embeddings.append(data["embedding"])
        return np.array(embeddings, dtype=np.float32)

    def _ollama_sync(self, path: str, body: dict, timeout: int = 90) -> dict:
        import json
        # Detect :cloud suffix models → route through Ollama Cloud API
        model = body.get("model", "")
        is_cloud = model.endswith(":cloud")

        if is_cloud and _OLLAMA_CLOUD_API_KEY:
            # Strip :cloud suffix for the cloud API
            body = {**body, "model": model.replace(":cloud", "")}
            url = f"{_OLLAMA_CLOUD_BASE}{path}"
            session = self._cloud_session
            headers = {
                "Authorization": f"Bearer {_OLLAMA_CLOUD_API_KEY}",
                "Content-Type": "application/json",
            }
        else:
            url = f"{self.config.ollama_base_url}{path}"
            session = self._session
            headers = {"Connection": "close"}
            if is_cloud:
                logger.warning("Cloud model %s requested but no API key available", model)

        for attempt in range(3):
            try:
                r = session.post(url, json=body, headers=headers, timeout=timeout)
                if r.status_code >= 400:
                    raise Exception(f"HTTP {r.status_code}: {r.text[:200]}")
                return r.json()
            except Exception as e:
                if attempt == 2:
                    raise
                _time.sleep(1)

    async def _expand_query(self, query: str) -> list[str]:
        """Generate 3 varied rewrites of the query using the LLM for multi-angle retrieval."""
        import json
        loop = asyncio.get_event_loop()
        prompt = f"""Rewrite the following question into 3 different, more detailed variations.
Search queries should cover different angles/interpretations. Output ONLY a JSON array of strings, no explanation.

Original: "{query}"

Output format: ["variation 1", "variation 2", "variation 3"]"""
        try:
            data = await loop.run_in_executor(None, self._ollama_sync, "/v1/chat/completions", {
                "model": self.config.expansion_llm_model or self.config.llm_model,
                "temperature": 0.2,
                "max_tokens": 120,
                "messages": [
                    {"role": "system", "content": "You are a query expansion engine. Output ONLY a JSON array."},
                    {"role": "user", "content": prompt},
                ],
            }, 60)
            raw = data["choices"][0]["message"]["content"].strip()
            # Extract JSON array from response (handles markdown fences)
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            variations = json.loads(raw)
            if isinstance(variations, list) and len(variations) >= 1:
                return variations[:3]
        except Exception:
            pass
        return []  # Fallback: no expansion

    async def retrieve(self, query: str, mode: str | None = None) -> dict:
        from lightrag import QueryParam
        if self.rag is None:
            return {"context_text": "", "citations": [], "mode_used": "hybrid"}

        mode_used = mode or classify_query(query)

        # ── Query expansion: search from multiple angles ──
        if self.config.use_query_expansion:
            expansions = await self._expand_query(query)
        else:
            expansions = []
        all_queries = [query] + expansions
        seen_sources = set()
        all_context_parts = []
        all_citations = []

        try:
            for q in all_queries:
                data_result = await self.rag.aquery_data(q, param=QueryParam(
                    mode=mode_used, top_k=self.config.top_k_retrieve, only_need_context=False))

                if data_result.get("status") != "success":
                    continue

                context_text, citations = extract_citations(data_result)
                # Deduplicate by source URL
                for citation in citations:
                    if citation not in seen_sources:
                        seen_sources.add(citation)
                        all_citations.append(citation)

                # Split into chunks and deduplicate roughly by content similarity
                chunks = [c.strip() for c in context_text.split("\n\n") if c.strip()]
                for chunk in chunks:
                    # Simple dedup: skip if first 60 chars already seen
                    short = chunk[:60].lower()
                    already = any(p[:60].lower() == short for p in all_context_parts)
                    if not already:
                        all_context_parts.append(chunk)

            context_text = "\n\n".join(all_context_parts)
            if len(context_text) > self.config.max_context_chars:
                cutoff = context_text.rfind("\n", 0, self.config.max_context_chars)
                context_text = context_text[:cutoff] if cutoff > 200 else context_text[:self.config.max_context_chars]

            return {"context_text": context_text, "citations": all_citations, "mode_used": mode_used}
        except Exception:
            return {"context_text": "", "citations": [], "mode_used": mode_used}

    async def generate(self, user_msg: str, context_text: str) -> str:
        system = self.config.system_prompt_template.format(
            context=context_text or "No additional context available.")
        loop = asyncio.get_event_loop()
        for attempt in range(3):
            try:
                data = await loop.run_in_executor(None, self._ollama_sync, "/v1/chat/completions", {
                    "model": self.config.llm_model,
                    "temperature": self.config.llm_temperature,
                    "max_tokens": self.config.llm_max_tokens,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_msg},
                    ],
                }, 90)
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.warning("%s: generate attempt %d failed: %s",
                    self.config.name, attempt + 1, str(e)[:200])
                if attempt == 2:
                    return "I'm having a moment — please try again!"
                await asyncio.sleep(2)
        return ""

# ── App ─────────────────────────────────────────────────────────────────────

_all_runtimes: dict[str, NotebookRuntime] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    for nb in NOTEBOOKS:
        rt = NotebookRuntime(nb)
        await rt.start()
        _all_runtimes[nb.name] = rt
    logger.info("all notebooks ready: %s", list(_all_runtimes.keys()))
    yield
    for rt in _all_runtimes.values():
        await rt.stop()
    _all_runtimes.clear()

app = FastAPI(title="Nexus Server", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quann.homes", "https://quanbot.quann.homes",
                   "https://rag.quann.homes", "https://chat.quann.homes"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# ── Landing page ────────────────────────────────────────────────────────────

CHAT_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus RAG — Quann Homes</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #1e293b; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; }
        .header h1 { font-size: 1.2rem; color: #f8fafc; }
        .header nav { display: flex; gap: 4px; }
        .tab { padding: 8px 16px; border-radius: 6px; border: none; background: #334155; color: #94a3b8; cursor: pointer; font-size: 0.9rem; transition: all .2s; }
        .tab.active { background: #3b82f6; color: #fff; }
        .tab:hover:not(.active) { background: #475569; color: #e2e8f0; }
        .docs-link { color: #38bdf8; text-decoration: none; font-size: 0.85rem; margin-left: 12px; }
        .messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
        .msg { max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; font-size: 0.95rem; }
        .msg.user { align-self: flex-end; background: #3b82f6; color: #fff; }
        .msg.assistant { align-self: flex-start; background: #1e293b; color: #e2e8f0; border: 1px solid #334155; }
        .msg .mode-tag { font-size: 0.7rem; opacity: 0.6; margin-bottom: 4px; }
        .msg .citations { margin-top: 8px; font-size: 0.8rem; opacity: 0.5; }
        .thinking { align-self: flex-start; background: #1e293b; color: #94a3b8; padding: 12px 16px; border-radius: 12px; font-style: italic; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 0.8; } }
        .input-area { background: #1e293b; padding: 16px 20px; border-top: 1px solid #334155; display: flex; gap: 8px; }
        .input-area input { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 0.95rem; outline: none; }
        .input-area input:focus { border-color: #3b82f6; }
        .input-area button { padding: 12px 24px; border-radius: 8px; border: none; background: #3b82f6; color: #fff; font-size: 0.95rem; cursor: pointer; transition: background .2s; }
        .input-area button:hover { background: #2563eb; }
        .input-area button:disabled { background: #334155; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Nexus RAG</h1>
        <nav>
            <button class="tab active" onclick="switchNotebook('chat')">🏠 Quann Chat</button>
            <button class="tab" onclick="switchNotebook('seo')">🔍 SEO Methodology</button>
            <button class="tab" onclick="switchNotebook('client')">🗣️ Client Knowledge</button>
            <a href="/docs" class="docs-link">API Docs</a>
            <a href="/explore" class="docs-link">🧠 Explore</a>
        </nav>
    </div>
    <div class="messages" id="messages"></div>
    <div class="input-area">
        <input id="userInput" type="text" placeholder="Ask something..." onkeydown="if(event.key==='Enter')send()" autofocus>
        <button id="sendBtn" onclick="send()">Send</button>
    </div>
    <script>
        let currentNotebook = 'chat';
        let sessionId = 'web-' + Date.now();

        function switchNotebook(nb) {
            currentNotebook = nb;
            document.querySelectorAll('.tab').forEach(t => {
                const names = {'chat': 'Quann', 'seo': 'SEO', 'client': 'Client'};
                t.classList.toggle('active', t.textContent.includes(names[nb]));
            });
            document.getElementById('userInput').focus();
            const msgs = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'msg assistant';
            div.style.opacity = '0.6';
            div.style.fontSize = '0.85rem';
            const welcome = {
                'chat': '🔄 Switched to Quann Chat — ask about Quan, real estate, Texas home buying.',
                'seo': '🔄 Switched to SEO Methodology — ask about entity-based SEO, topical maps, content strategy.',
                'client': '🔄 Switched to Client Knowledge — ask about buyer consultations, client concerns, meeting transcripts.'
            };
            div.textContent = welcome[nb];
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }

        async function send() {
            const input = document.getElementById('userInput');
            const btn = document.getElementById('sendBtn');
            const msg = input.value.trim();
            if (!msg) return;

            // Show user message
            const msgs = document.getElementById('messages');
            const userDiv = document.createElement('div');
            userDiv.className = 'msg user';
            userDiv.textContent = msg;
            msgs.appendChild(userDiv);

            // Show thinking
            const thinkDiv = document.createElement('div');
            thinkDiv.className = 'thinking';
            thinkDiv.textContent = 'Thinking...';
            msgs.appendChild(thinkDiv);
            msgs.scrollTop = msgs.scrollHeight;

            input.value = '';
            btn.disabled = true;

            try {
                const endpoints = {'chat': '/chat', 'seo': '/seo', 'client': '/client'};
                const endpoint = endpoints[currentNotebook];
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, session_id: sessionId})
                });
                const data = await res.json();

                // Remove thinking
                thinkDiv.remove();

                // Show response
                const aiDiv = document.createElement('div');
                aiDiv.className = 'msg assistant';
                let html = '<div class="mode-tag">mode: ' + data.mode_used + '</div>';
                html += data.reply.replace(/\\n/g, '<br>');
                if (data.citations && data.citations.length > 0) {
                    html += '<div class="citations">📎 ' + data.citations.length + ' citations</div>';
                }
                aiDiv.innerHTML = html;
                msgs.appendChild(aiDiv);
                msgs.scrollTop = msgs.scrollHeight;
            } catch (e) {
                thinkDiv.remove();
                const errDiv = document.createElement('div');
                errDiv.className = 'msg assistant';
                errDiv.style.color = '#f87171';
                errDiv.textContent = '⚠️ Error: ' + e.message;
                msgs.appendChild(errDiv);
            }
            btn.disabled = false;
            document.getElementById('userInput').focus();
        }
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def landing():
    return CHAT_UI_HTML

@app.get("/client", response_class=HTMLResponse)
async def client_page():
    return HTMLResponse(CHAT_UI_HTML.replace("currentNotebook = 'chat'", "currentNotebook = 'client'").replace(
        '<button class="tab active" onclick="switchNotebook(\'chat\')">🏠 Quann Chat</button>',
        '<button class="tab" onclick="switchNotebook(\'chat\')">🏠 Quann Chat</button>'
    ).replace(
        '<button class="tab" onclick="switchNotebook(\'client\')">🗣️ Client Knowledge</button>',
        '<button class="tab active" onclick="switchNotebook(\'client\')">🗣️ Client Knowledge</button>'
    ))

@app.get("/health")
async def health():
    # Collect doc status per notebook from WebUI backends
    nb_info = {}
    for name, rt in _all_runtimes.items():
        info = {
            "rag_ready": rt.rag is not None,
            "reranker_loaded": rt.reranker is not None,
            "workspace": rt.config.workspace,
            "llm": rt.config.llm_model,
            "doc_status": None,
        }
        # Read doc status directly from workspace JSON.
        # kv_store_doc_status.json path: {workspace}/kv_store_doc_status.json
        try:
            import json, os
            status_path = os.path.join(rt.config.workspace, "kv_store_doc_status.json")
            if os.path.exists(status_path):
                with open(status_path) as f:
                    raw = json.load(f)
                # Accept both dict values and JSON-string wrappers
                statuses = {}
                for v in raw.values():
                    if isinstance(v, str):
                        try:
                            v = json.loads(v)
                        except Exception:
                            continue
                    if isinstance(v, dict):
                        s = v.get("status", "?")
                        statuses[s] = statuses.get(s, 0) + 1
                if statuses:
                    info["doc_status"] = statuses
                    # Add 'all' count for the UI
                    info["doc_status"]["all"] = sum(statuses.values())
        except Exception:
            pass
        nb_info[name] = info

    return {
        "status": "healthy",
        "version": "3.0.0",
        "notebooks": nb_info,
    }

async def _handle_chat(rt: NotebookRuntime, body: ChatRequest):
    start = _time.monotonic()
    msg = body.message.strip()
    session_id = body.session_id or f"{rt.config.name}-{int(_time.time() * 1000)}"
    if not msg:
        return ChatResponse(reply="", session_id=session_id, mode_used="hybrid")

    result = await rt.retrieve(msg, mode=body.mode)
    reply = await rt.generate(msg, result["context_text"])
    elapsed = (_time.monotonic() - start) * 1000
    logger.info("%s session=%s mode=%s reply=%d citations=%d ms=%.0f",
                 rt.config.name, session_id, result["mode_used"], len(reply), len(result["citations"]), elapsed)
    return ChatResponse(reply=reply or "Let me know how I can help you!",
                        session_id=session_id,
                        mode_used=result["mode_used"],
                        citations=result["citations"])

@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    return await _handle_chat(_all_runtimes["quann-chat"], body)

@app.post("/seo", response_model=ChatResponse)
async def seo(body: ChatRequest):
    return await _handle_chat(_all_runtimes["seo-methodology"], body)


# ── LightRAG Explorer proxy ────────────────────────────────────────────────
# Direct proxy to individual LightRAG WebUI instances (ports 8011, 8012).
# No middleman — Nexus handles HTML rewriting and Referer-based API routing.

import httpx, re
_ui_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0))
_EXCLUDED_HEADERS = {"host", "transfer-encoding", "content-encoding", "content-length"}

# Notebook WebUI ports
_NB_PORTS = {"quann-chat": 8011, "seo-methodology": 8012}

# Explorer landing page HTML
EXPLORE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LightRAG Explorer — Quann Homes</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:40px 20px}
h1{font-size:2rem;margin-bottom:8px;color:#f8fafc}
.subtitle{color:#94a3b8;margin-bottom:40px;font-size:1.05rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px;max-width:900px;width:100%}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:28px 24px;text-decoration:none;color:inherit;display:block;transition:all .2s}
.card:hover{transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,.3)}
.card.qc:hover{border-color:#3b82f6}
.card.seo:hover{border-color:#10b981}
.card h2{font-size:1.15rem;margin-bottom:8px}
.card p.desc{color:#94a3b8;font-size:0.9rem;line-height:1.5;margin-bottom:14px}
.tag{display:inline-block;padding:4px 10px;border-radius:6px;font-size:0.75rem;color:#fff}
.tag.qc{background:#3b82f6}
.tag.seo{background:#10b981}
.status-row{display:flex;align-items:center;gap:8px;margin-bottom:20px}
.dot{width:8px;height:8px;border-radius:50%}
.dot.green{background:#10b981}
.dot.red{background:#ef4444}
.dot.yellow{background:#f59e0b}
.dot.blue{background:#3b82f6}
.status-text{font-size:0.85rem;color:#94a3b8}
.progress-section{margin-top:12px;border-top:1px solid #334155;padding-top:12px}
.progress-label{font-size:0.75rem;color:#64748b;margin-bottom:6px}
.progress-bar-bg{height:6px;background:#334155;border-radius:3px;overflow:hidden;margin-bottom:4px}
.progress-bar-fill{height:100%;border-radius:3px;transition:width .5s ease}
.progress-bar-fill.processing{background:#3b82f6}
.progress-bar-fill.done{background:#10b981}
.progress-stats{font-size:0.7rem;color:#64748b;display:flex;gap:10px}
.progress-stats span{white-space:nowrap}
.warn{color:#f59e0b;font-size:0.75rem;margin-top:8px}
</style>
</head>
<body>
<h1>🧠 LightRAG Knowledge Explorer</h1>
<p class="subtitle">Visual knowledge graphs, document search, entity exploration</p>
<div class="status-row" id="status"><span class="dot yellow"></span><span class="status-text">Checking notebooks...</span></div>
<div class="grid">
    <a href="/ui/quann-chat/webui/" class="card qc" id="card-qc">
        <div style="display:flex;justify-content:space-between;align-items:start">
            <h2>🏠 Quann Chat</h2>
            <span class="tag qc">Open →</span>
        </div>
        <p class="desc">Quan Nguyen's real estate knowledge graph — entities, relations across quann.homes</p>
        <div class="progress-section" id="progress-qc" style="display:none">
            <div class="progress-label">Document Processing</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill processing" id="bar-qc" style="width:0%"></div></div>
            <div class="progress-stats" id="stats-qc"></div>
        </div>
    </a>
    <a href="/ui/seo-methodology/webui/" class="card seo" id="card-seo">
        <div style="display:flex;justify-content:space-between;align-items:start">
            <h2>🔍 SEO Methodology</h2>
            <span class="tag seo">Open →</span>
        </div>
        <p class="desc">Entity-based SEO research from holisticseo.digital — semantic search, topical mapping</p>
        <div class="progress-section" id="progress-seo" style="display:none">
            <div class="progress-label">Document Processing</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill processing" id="bar-seo" style="width:0%"></div></div>
            <div class="progress-stats" id="stats-seo"></div>
        </div>
    </a>
    <a href="/client" class="card" style="--hover-color:#8b5cf6" id="card-client">
        <div style="display:flex;justify-content:space-between;align-items:start">
            <h2>🗣️ Client Knowledge</h2>
            <span class="tag" style="background:#8b5cf6">Open →</span>
        </div>
        <p class="desc">Meeting transcripts, buyer consultations — what clients really ask about</p>
        <div class="progress-section" id="progress-client" style="display:none">
            <div class="progress-label">Document Processing</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill processing" id="bar-client" style="width:0%"></div></div>
            <div class="progress-stats" id="stats-client"></div>
        </div>
    </a>
</div>
<script>
async function checkStatus() {
    const s = document.getElementById('status');
    try {
        const r = await fetch('/health');
        const d = await r.json();
        const nbs = d.notebooks || {};

        let allReady = true;
        for (const [name, info] of Object.entries(nbs)) {
            const id = name === 'seo-methodology' ? 'seo' : 'qc';
            const progress = document.getElementById('progress-' + id);
            const bar = document.getElementById('bar-' + id);
            const stats = document.getElementById('stats-' + id);

            if (!progress || !bar || !stats) continue;

            const ds = info.doc_status;
            if (ds) {
                const total = ds.all || 0;
                const done = ds.processed || 0;
                const processing = ds.processing || 0;
                const pending = ds.pending || 0;
                const failed = ds.failed || 0;

                if (total > 0) {
                    progress.style.display = 'block';
                    const pct = Math.round((done / total) * 100);
                    bar.style.width = pct + '%';
                    bar.className = 'progress-bar-fill ' + (pct === 100 ? 'done' : 'processing');

                    let statHtml = '<span>📄 ' + total + ' docs</span>';
                    statHtml += '<span>✅ ' + done + ' done</span>';
                    if (processing > 0) statHtml += '<span>⚙️ ' + processing + ' extracting</span>';
                    if (pending > 0) statHtml += '<span>⏳ ' + pending + ' queued</span>';
                    if (failed > 0) statHtml += '<span>❌ ' + failed + ' failed</span>';
                    stats.innerHTML = statHtml;

                    if (pct < 100) allReady = false;
                }
            }
        }

        if (allReady && nbs['quann-chat'] && nbs['quann-chat'].rag_ready) {
            s.innerHTML = '<span class="dot green"></span><span class="status-text">All notebooks ready ✅</span>';
        } else if (!allReady) {
            s.innerHTML = '<span class="dot blue"></span><span class="status-text">Processing documents... ⚙️</span>';
        } else {
            s.innerHTML = '<span class="dot yellow"></span><span class="status-text">Some notebooks loading...</span>';
        }
    } catch(e) {
        s.innerHTML = '<span class="dot yellow"></span><span class="status-text">Checking...</span>';
    }
}
checkStatus();
setInterval(checkStatus, 5000); // Refresh every 5s
</script>
</body>
</html>"""


@app.get("/explore", response_class=HTMLResponse)
async def explore_landing():
    return EXPLORE_HTML


def _detect_notebook(request: Request) -> str | None:
    """Detect which notebook the request is for.
    Priority: cookie > URL path > Referer header."""
    # Cookie (survives SPA navigation)
    cookie_nb = request.cookies.get("lightrag_nb")
    if cookie_nb and cookie_nb in _NB_PORTS:
        return cookie_nb
    # Check if URL path already contains notebook
    m = re.search(r'^/ui/([a-z0-9_-]+)/', request.url.path)
    if m:
        return m.group(1)
    # Fallback to Referer header
    referer = request.headers.get("Referer", "")
    m = re.search(r'/ui/([a-z0-9_-]+)/', referer)
    if m:
        return m.group(1)
    return None


@app.api_route("/ui/{nb_name}/webui", methods=["GET"])
async def ui_webui_root(nb_name: str, request: Request):
    """Redirect /ui/{nb}/webui → /ui/{nb}/webui/ auto-selecting top popular label."""
    port = _NB_PORTS.get(nb_name)
    top_label = ""
    if port:
        try:
            r = await _ui_client.get(f"http://127.0.0.1:{port}/graph/label/popular?limit=1", timeout=5)
            labels = r.json()
            if isinstance(labels, list) and labels:
                top_label = labels[0]
        except Exception:
            pass
    url = f"/ui/{nb_name}/webui/"
    if top_label:
        url += f"?label={top_label}"
    resp = RedirectResponse(url=url, status_code=302)
    resp.set_cookie("lightrag_nb", nb_name, path="/", samesite="lax", httponly=False)
    return resp


@app.api_route("/ui/{nb_name}/webui/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def ui_webui_proxy(nb_name: str, path: str, request: Request):
    """Proxy /ui/{nb}/webui/* → 127.0.0.1:{port}/webui/*"""
    if nb_name not in _NB_PORTS:
        return HTMLResponse("Notebook not found", status_code=404)
    return await _proxy_to_nb(nb_name, f"webui/{path}", request)


# Cache of top popular label per notebook (for label=* replacement)
_top_labels: dict[str, str] = {}


async def _get_top_label(nb_name: str) -> str | None:
    """Get the top popular label for a notebook, cached."""
    if nb_name in _top_labels:
        return _top_labels[nb_name]
    port = _NB_PORTS.get(nb_name)
    if not port:
        return None
    try:
        r = await _ui_client.get(f"http://127.0.0.1:{port}/graph/label/popular?limit=1", timeout=5)
        labels = r.json()
        if isinstance(labels, list) and labels:
            _top_labels[nb_name] = labels[0]
            return labels[0]
    except Exception:
        pass
    return None


# Catch root-relative API calls from WebUI JS (e.g., /graph/label/popular, /documents/status_counts)
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all_proxy(path: str, request: Request):
    nb = _detect_notebook(request)
    if not nb or nb not in _NB_PORTS:
        return HTMLResponse("Not found", status_code=404)
    # Replace label=* and hardcoded fallback labels (entity/relationship/document/concept)
    # with top popular label to avoid overwhelming mobile Sigma.js and empty results.
    # These fallbacks come from MM.initializeWithDefaults in the SPA when
    # /graph/label/popular fails — they're LightRAG element types, not real labels.
    # Handles both literal and URL-encoded (JS encodeURIComponent).
    query = request.url.query
    if path == "graphs" and query:
        import urllib.parse
        params = urllib.parse.parse_qs(query)
        label_val = params.get("label", [None])[0]
        if label_val in ("*", "entity", "relationship", "document", "concept"):
            top = await _get_top_label(nb)
            if top:
                params["label"] = [top]
                query = urllib.parse.urlencode(params, doseq=True)
    return await _proxy_to_nb_q(nb, path, query, request)


async def _proxy_to_nb_q(nb_name: str, subpath: str, query_str: str, request: Request):
    """Like _proxy_to_nb but with explicit query string override."""
    port = _NB_PORTS[nb_name]
    url = f"http://127.0.0.1:{port}/{subpath}"
    if query_str:
        url += f"?{query_str}"
    
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in _EXCLUDED_HEADERS}
    body = await request.body() if request.method in ("POST", "PUT", "PATCH") else None
    
    try:
        resp = await _ui_client.request(request.method, url, headers=headers, content=body or None)
        content = resp.content
        ct = resp.headers.get("content-type", "")
        if "text/html" in ct:
            html = content.decode("utf-8", errors="replace")
            html = html.replace('"/webui/', f'"/ui/{nb_name}/webui/')
            html = html.replace("'/webui/", f"'/ui/{nb_name}/webui/")
            html = html.replace('href="favicon.png"', f'href="/ui/{nb_name}/webui/favicon.png"')
            content = html.encode("utf-8")
        
        r_headers = {k: v for k, v in resp.headers.items()
                     if k.lower() not in _EXCLUDED_HEADERS}
        r_headers["content-length"] = str(len(content))
        r_headers["access-control-allow-origin"] = "*"
        r_headers["access-control-allow-methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        r_headers["access-control-allow-headers"] = "*"
        resp_obj = Response(content=content, status_code=resp.status_code, headers=r_headers)
        resp_obj.set_cookie("lightrag_nb", nb_name, path="/", samesite="lax", httponly=False, max_age=86400)
        return resp_obj
    except Exception:
        return HTMLResponse("<h2>WebUI backend unavailable</h2><p>Try again in a moment.</p>", status_code=502)


@app.api_route("/ui/{nb_name}/webui/{path:path}", methods=["OPTIONS"])
async def ui_webui_options(nb_name: str, path: str):
    """Handle CORS preflight for WebUI assets."""
    return Response(status_code=204, headers={
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "access-control-allow-headers": "*",
    })


async def _proxy_to_nb(nb_name: str, subpath: str, request: Request):
    """Forward to a notebook's LightRAG WebUI backend."""
    port = _NB_PORTS[nb_name]
    url = f"http://127.0.0.1:{port}/{subpath}"
    if request.url.query:
        url += f"?{request.url.query}"

    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in _EXCLUDED_HEADERS}

    body = await request.body() if request.method in ("POST", "PUT", "PATCH") else None

    try:
        resp = await _ui_client.request(request.method, url, headers=headers, content=body or None)
        content = resp.content

        # Rewrite /webui/ → /ui/{nb}/webui/ in HTML responses
        ct = resp.headers.get("content-type", "")
        if "text/html" in ct:
            html = content.decode("utf-8", errors="replace")
            html = html.replace('"/webui/', f'"/ui/{nb_name}/webui/')
            html = html.replace("'/webui/", f"'/ui/{nb_name}/webui/")
            html = html.replace('href="favicon.png"', f'href="/ui/{nb_name}/webui/favicon.png"')
            content = html.encode("utf-8")

        r_headers = {k: v for k, v in resp.headers.items()
                     if k.lower() not in _EXCLUDED_HEADERS}
        r_headers["content-length"] = str(len(content))
        r_headers["access-control-allow-origin"] = "*"
        r_headers["access-control-allow-methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        r_headers["access-control-allow-headers"] = "*"
        resp_obj = Response(content=content, status_code=resp.status_code, headers=r_headers)
        # Set notebook cookie so root-relative API calls from the SPA can be routed
        resp_obj.set_cookie("lightrag_nb", nb_name, path="/", samesite="lax", httponly=False, max_age=86400)
        return resp_obj
    except Exception:
        return HTMLResponse("<h2>WebUI backend unavailable</h2><p>Try again in a moment.</p>", status_code=502)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("nexus_server:app", host="0.0.0.0", port=8001, log_level="warning")
