"""
Nexus-style shared components for LightRAG servers.
- Query classifier (local / global / hybrid)
- Conflict-resolution system prompt injection
- Citation extraction from aquery_data results
"""
from __future__ import annotations

import re
import asyncio
import socket
import logging
from typing import Literal
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ── Shared API models (module-level to avoid Pydantic ForwardRef issues) ───

class NexusChatRequest(BaseModel):
    """Standard chat request for all Nexus notebooks."""
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    mode: str | None = Field(
        default=None,
        description="Override retrieval mode: 'local', 'global', or 'hybrid'",
    )


class NexusChatResponse(BaseModel):
    """Standard chat response for all Nexus notebooks."""
    reply: str
    session_id: str
    mode_used: str = "hybrid"
    citations: list[str] = Field(default_factory=list)


# ── Query classifier ──────────────────────────────────────────────────────
# Keywords that signal each retrieval mode. Order matters — more specific
# patterns first.

_LOCAL_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(?:what|who|where|when)\s+(?:is|are|was|were)\b", re.I),
    re.compile(r"\bdefine\b", re.I),
    re.compile(r"\btell\s+me\s+(?:about|more\s+about)\b", re.I),
    re.compile(r"\b(?:find|look\s+up|search\s+for)\b", re.I),
    re.compile(r"\b(?:phone|email|address|contact|license|brokerage)\b", re.I),
    re.compile(r"\b(?:mean|meaning|definition)\b", re.I),
    re.compile(r"\b(?:details?|specifics?)\s+(?:of|about|on)\b", re.I),
]

_GLOBAL_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(?:overview|summary|summarize|explain\s+(?:the\s+)?concept)", re.I),
    re.compile(r"\bhow\s+(?:does|do|can|should|would|to)\b", re.I),
    re.compile(r"\b(?:process|workflow|strategy|methodology|approach)", re.I),
    re.compile(r"\b(?:generally|overall|broadly|high.level|big.picture)", re.I),
    re.compile(r"\b(?:explain|describe|elaborate)\b", re.I),
    re.compile(r"\b(?:what\s+(?:is\s+the\s+)?(?:process|method|way|best\s+way))\b", re.I),
    re.compile(r"\b(?:guide|how.?to|tutorial|walkthrough|steps?)\b", re.I),
]

_HYBRID_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(?:vs\.?|versus|compared?\s+(?:to|with)|difference|differ)\b", re.I),
    re.compile(r"\b(?:pros?\s+(?:and|&)\s+cons?|advantages?\s+(?:and|&)\s+disadvantages?)\b", re.I),
    re.compile(r"\b(?:both|each|between|among|either|neither)\b", re.I),
    re.compile(r"\b(?:which\s+(?:one|is\s+better|should\s+I))\b", re.I),
    re.compile(r"\b(?:contextualize|relate|connect)\b", re.I),
]


def classify_query(query: str) -> Literal["local", "global", "hybrid"]:
    """Classify a query into the best retrieval mode.

    Priority: hybrid > local > global > default(hybrid)
    - hybrid: comparison / conflict / multi-entity questions
    - local:  specific named-entity or fact lookup
    - global: high-level overviews, processes, explanations
    """
    query_clean = query.strip().lower()

    # Hybrid patterns fire first — they're the most specific
    for pat in _HYBRID_PATTERNS:
        if pat.search(query_clean):
            logger.debug("classifier=hybrid reason=%s query=%.80s", pat.pattern, query_clean)
            return "hybrid"

    # Local patterns next
    for pat in _LOCAL_PATTERNS:
        if pat.search(query_clean):
            logger.debug("classifier=local reason=%s query=%.80s", pat.pattern, query_clean)
            return "local"

    # Global patterns
    for pat in _GLOBAL_PATTERNS:
        if pat.search(query_clean):
            logger.debug("classifier=global reason=%s query=%.80s", pat.pattern, query_clean)
            return "global"

    # Default: hybrid — safest fallback, covers both bases
    logger.debug("classifier=hybrid reason=default query=%.80s", query_clean)
    return "hybrid"


# ── Conflict resolution prompt ────────────────────────────────────────────

CONFLICT_RESOLUTION_INSTRUCTION = """## Knowledge Conflict Resolution
When retrieved sources contain contradictory information:
1. **Prioritize the most recent timestamp.** If one source is dated later, it takes precedence.
2. **File path hierarchy.** Newer file paths (with recent dates or version numbers) override older paths.
3. **Explicitly flag conflicts.** If sources genuinely conflict and you cannot determine recency, state both positions and note the disagreement.
4. **Field-level citations.** Every factual claim must cite its source using the [ref:N] format, where N maps to the Sources section at the bottom of your response."""


# ── Reranker (shared) ───────────────────────────────────────────────────────
# mxbai-rerank-base-v1 via sentence_transformers CrossEncoder, CPU-only.
# Both servers use the same model cached locally at RERANKER_CACHE_DIR.

import os as _shared_os
import logging as _logging
import asyncio as _asyncio

_shared_logger = _logging.getLogger("nexus_shared")

RERANKER_CACHE_DIR = (
    "/home/steve/.cache/huggingface/hub/"
    "models--mixedbread-ai--mxbai-rerank-base-v1/snapshots/"
    "800f24c113213a187e65bde9db00c15a2bb12738"
)
RERANKER_LOAD_TIMEOUT = 30  # seconds


def load_reranker() -> object | None:
    """Load CrossEncoder reranker from local cache. Returns None on failure.

    Sets HF offline flags so no network call is attempted — must be pre-cached.
    """
    _shared_os.environ.setdefault("HF_HUB_OFFLINE", "1")
    _shared_os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    _shared_os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import CrossEncoder
    model = CrossEncoder(RERANKER_CACHE_DIR)
    _shared_logger.info("reranker_loaded shared")
    return model


def make_rerank_func(reranker: object | None, default_top_n: int = 5):
    """Create an async rerank function closure wired to a specific model instance.

    The returned function matches LightRAG's rerank_model_func signature
    (async, receives query + documents, returns list of scored dicts).

    Falls back to identity ordering if reranker is None or prediction fails.
    """
    async def _rerank(query: str, documents: list[str], top_n: int = default_top_n) -> list[dict]:
        if not documents:
            return []
        if reranker is None:
            indexed = [(i, 1.0) for i in range(len(documents))]
            return [{"index": idx, "relevance_score": score} for idx, score in indexed[:top_n]]

        try:
            loop = _asyncio.get_event_loop()
            pairs = [[query, doc] for doc in documents]
            scores = await loop.run_in_executor(
                None, lambda: reranker.predict(pairs, show_progress_bar=False),
            )
            ranked = sorted(
                [(i, float(scores[i])) for i in range(len(scores))],
                key=lambda x: x[1], reverse=True,
            )
            return [{"index": idx, "relevance_score": score} for idx, score in ranked[:top_n]]
        except Exception as e:
            _shared_logger.warning("reranker_failed falling_back error=%s", str(e)[:100])
            indexed = [(i, 1.0) for i in range(len(documents))]
            return [{"index": idx, "relevance_score": score} for idx, score in indexed[:top_n]]

    return _rerank


async def start_reranker() -> object | None:
    """Load the reranker with a timeout. Call during server startup."""
    try:
        loop = _asyncio.get_event_loop()
        model = await _asyncio.wait_for(
            loop.run_in_executor(None, load_reranker),
            timeout=RERANKER_LOAD_TIMEOUT,
        )
        return model
    except Exception as e:
        _shared_logger.warning("reranker_load_failed continuing_without error=%s", str(e)[:120])
        return None


# ── App Factory: one engine, many notebooks ────────────────────────────────
# Instead of duplicating server code, each bot is a thin config dict.
# create_app(config) builds a full FastAPI app with retrieval, reranking,
# CORS, health checks, and routes — all shared across services.

import time as _factory_time
from dataclasses import dataclass as _dataclass, field as _field
from pathlib import Path as _Path
from contextlib import asynccontextmanager as _asynccm

import numpy as _np
from fastapi import FastAPI as _FastAPI
from fastapi.middleware.cors import CORSMiddleware as _CORSMiddleware
from pydantic import BaseModel as _BaseModel, Field as _Field

# Lazy imports (only resolvable inside the app's venv)
_LightRAG = None
_QueryParam = None
_EmbeddingFunc = None
_lightrag_logger = None

def _ensure_lightrag_imports():
    global _LightRAG, _QueryParam, _EmbeddingFunc, _lightrag_logger
    if _LightRAG is None:
        from lightrag import LightRAG as L, QueryParam as Q
        from lightrag.utils import EmbeddingFunc as E, logger as Lg
        _LightRAG = L; _QueryParam = Q; _EmbeddingFunc = E; _lightrag_logger = Lg


@_dataclass
class NotebookConfig:
    """A single notebook — one bot with its own data, model, and personality."""

    # ── Identity ──
    name: str  # e.g. "quann-chat"
    title: str  # e.g. "Quann Chat"
    version: str = "2.0.0"

    # ── Paths ──
    workspace: str = ""  # LightRAG workspace directory
    fallback_workspace: str = ""  # backup workspace for corruption recovery

    # ── Models ──
    llm_model: str = "gemma4:31b-cloud"
    embed_model: str = "nomic-embed-text-v2-moe"
    embed_dim: int = 768
    embed_max_tokens: int = 8192

    # ── Retrieval tuning ──
    top_k_retrieve: int = 20
    top_n_rerank: int = 5
    max_context_chars: int = 4000

    # ── LLM generation ──
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500

    # ── CORS ──
    allowed_origins: list[str] = _field(default_factory=lambda: [
        "https://quann.homes",
        "https://quanbot.quann.homes",
    ])
    route_path: str = "/chat"  # "/chat" or "/ask"
    route_method: str = "chat"  # "chat" or "ask" — which model field to use

    # ── Personality ──
    system_prompt_template: str = (
        "You are a helpful assistant.\n\n"
        "## CONTEXT:\n{context}"
    )

    # ── Ollama connection ──
    ollama_base_url: str = ""  # http://192.168.4.148:11434 — auto-resolved if empty

    # ── Limits ──
    embedding_func_max_async: int = 1
    llm_model_max_async: int = 2
    max_parallel_insert: int = 1

    # ── Features ──
    use_query_expansion: bool = True  # multi-angle retrieval (costs 1 extra LLM call)
    expansion_llm_model: str = ""  # separate model for query expansion (faster, cheaper). Empty = use llm_model.


def create_app(config: NotebookConfig):
    """Build a full FastAPI app from a notebook config.

    Returns the app object ready for uvicorn.run(). Thin server.py files
    just call this and run.
    """
    _ensure_lightrag_imports()
    _lightrag_logger.setLevel(logging.ERROR)

    _app_logger = logging.getLogger(config.name)
    _app_logger.setLevel(logging.WARNING)

    # ── Resolve Ollama base URL ──
    if not config.ollama_base_url:
        try:
            host = socket.gethostbyname("host.docker.internal")
        except Exception:
            host = "192.168.4.148"
        config.ollama_base_url = f"http://{host}:11434"
    _app_logger.info("ollama_base=%s", config.ollama_base_url)

    # ── State ──
    _rag = None
    _reranker = None
    _rerank_func_local = None

    # ── HTTP client (sync, fresh socket per call) ──
    def _ollama_request(path: str, body: dict, timeout: int = 90) -> dict:
        import http.client
        import json
        payload = json.dumps(body).encode("utf-8")
        last_err = None
        for attempt in range(3):
            conn = None
            try:
                conn = http.client.HTTPConnection(
                    config.ollama_base_url.split("://")[1].split(":")[0],
                    int(config.ollama_base_url.split(":")[-1]),
                    timeout=timeout,
                )
                conn.connect()
                try:
                    conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
                    conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                    conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                except OSError:
                    pass
                conn.request("POST", path, body=payload, headers={
                    "Content-Type": "application/json",
                    "Connection": "close",
                })
                resp = conn.getresponse()
                raw = resp.read()
                if resp.status >= 400:
                    raise Exception(f"HTTP {resp.status}: {raw[:200]}")
                return json.loads(raw)
            except Exception as e:
                last_err = e
                if attempt < 2:
                    _factory_time.sleep(1)
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
        raise last_err

    # ── Embedding ──
    async def _embed_texts(texts: list[str]) -> _np.ndarray:
        embeddings = []
        loop = asyncio.get_event_loop()
        for text in texts:
            for attempt in range(3):
                try:
                    data = await loop.run_in_executor(
                        None,
                        lambda t=text: _ollama_request(
                            "/api/embeddings",
                            {"model": config.embed_model, "prompt": f"search_query: {t}"},
                            timeout=60,
                        ),
                    )
                    embeddings.append(data["embedding"])
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1)
        return _np.array(embeddings, dtype=_np.float32)

    # ── LLM no-op ──
    async def _noop_llm(prompt, system_prompt=None, history_messages=None, **kwargs):
        return '{"high_level_keywords": [], "low_level_keywords": []}'

    # ── Retrieval ──
    async def _nexus_retrieve(query: str, mode: str | None = None) -> dict:
        nonlocal _rag
        if _rag is None:
            return {"context_text": "", "citations": [], "mode_used": "hybrid", "raw_data": None}

        mode_used = mode or classify_query(query)
        _app_logger.info("nexus_retrieve mode=%s query=%.80s", mode_used, query)

        try:
            data_result = await _rag.aquery_data(
                query,
                param=_QueryParam(
                    mode=mode_used,
                    top_k=config.top_k_retrieve,
                    only_need_context=False,
                ),
            )

            if data_result.get("status") != "success":
                _app_logger.warning("aquery_data_failed status=%s", data_result.get("status"))
                return {"context_text": "", "citations": [], "mode_used": mode_used, "raw_data": None}

            context_text, citations = extract_citations(data_result)

            if len(context_text) > config.max_context_chars:
                cutoff = context_text.rfind("\n", 0, config.max_context_chars)
                context_text = context_text[:cutoff] if cutoff > 200 else context_text[:config.max_context_chars]

            return {
                "context_text": context_text,
                "citations": citations,
                "mode_used": mode_used,
                "raw_data": data_result.get("data"),
            }

        except Exception as e:
            _app_logger.error("nexus_retrieve_error: %s", e)
            try:
                result = await _rag.aquery(
                    query,
                    param=_QueryParam(mode=mode_used, only_need_context=True, top_k=config.top_k_retrieve),
                )
                context_text = (result or "")[:config.max_context_chars] if result else ""
                return {"context_text": context_text, "citations": [], "mode_used": mode_used, "raw_data": None}
            except Exception as e2:
                _app_logger.error("fallback_retrieval_error: %s", e2)
                return {"context_text": "", "citations": [], "mode_used": mode_used, "raw_data": None}

    # ── LLM call ──
    async def _call_llm(system: str, user_msg: str) -> str:
        loop = asyncio.get_event_loop()
        for attempt in range(3):
            try:
                data = await loop.run_in_executor(
                    None,
                    lambda: _ollama_request(
                        "/v1/chat/completions",
                        {
                            "model": config.llm_model,
                            "temperature": config.llm_temperature,
                            "max_tokens": config.llm_max_tokens,
                            "messages": [
                                {"role": "system", "content": system},
                                {"role": "user", "content": user_msg},
                            ],
                        },
                        timeout=90,
                    ),
                )
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                _app_logger.warning("ollama_attempt=%d/3 error=%s", attempt + 1, str(e)[:120])
                if attempt == 2:
                    raise
                await asyncio.sleep(2)
        return ""

    # ── Lifespan ──
    @_asynccm
    async def _lifespan(app: _FastAPI):
        nonlocal _rag, _reranker, _rerank_func_local

        _reranker = await start_reranker()
        _rerank_func_local = make_rerank_func(_reranker, default_top_n=config.top_n_rerank)

        ws = _Path(config.workspace)
        fallback = _Path(config.fallback_workspace) if config.fallback_workspace else None
        vdb = ws / "vdb_chunks.json"
        if not vdb.exists() or vdb.stat().st_size < 1000:
            _app_logger.warning("workspace_corrupted_or_empty vdb=%s", vdb.exists())
            if fallback and fallback.exists() and (fallback / "vdb_chunks.json").exists():
                _app_logger.warning("falling_back_to_old_workspace")
                ws = fallback
            else:
                _app_logger.error("no_valid_workspace — starting empty")
        ws.mkdir(parents=True, exist_ok=True)

        _rag = _LightRAG(
            working_dir=str(ws),
            llm_model_func=_noop_llm,
            embedding_func=_EmbeddingFunc(
                embedding_dim=config.embed_dim,
                max_token_size=config.embed_max_tokens,
                func=_embed_texts,
            ),
            rerank_model_func=_rerank_func_local,
            embedding_func_max_async=config.embedding_func_max_async,
            llm_model_max_async=config.llm_model_max_async,
            max_parallel_insert=config.max_parallel_insert,
            entity_extract_max_gleaning=0,
        )
        await _rag.initialize_storages()
        _app_logger.info("rag_ready workspace=%s reranker=%s", ws, _reranker is not None)
        yield
        _rag = None
        _reranker = None
        _app_logger.info("shutdown")

    # ── App ──
    app = _FastAPI(title=config.title, version=config.version, lifespan=_lifespan)

    app.add_middleware(
        _CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    async def _health():
        return {
            "status": "healthy",
            "service": config.name,
            "version": config.version,
            "rag_ready": _rag is not None,
            "reranker_loaded": _reranker is not None,
        }

    @app.post(config.route_path, response_model=NexusChatResponse)
    async def _route(body: NexusChatRequest):
        start = _factory_time.monotonic()
        msg = body.message.strip()
        session_id = body.session_id or f"{config.name}-{int(_factory_time.time() * 1000)}"
        if not msg:
            return NexusChatResponse(reply="", session_id=session_id, mode_used="hybrid")

        result = await _nexus_retrieve(msg, mode=body.mode)
        context_text = result["context_text"]
        citations = result["citations"]
        mode_used = result["mode_used"]

        system = config.system_prompt_template.format(
            context=context_text or "No additional context available."
        )

        try:
            reply = await _call_llm(system, msg)
        except Exception:
            reply = "I'm having a moment — please try again!"

        if not reply:
            reply = "Let me know how I can help you!"

        elapsed = (_factory_time.monotonic() - start) * 1000
        _app_logger.info("%s session=%s mode=%s reply=%d citations=%d ms=%.0f",
                         config.route_method, session_id, mode_used, len(reply), len(citations), elapsed)
        return NexusChatResponse(reply=reply, session_id=session_id, mode_used=mode_used, citations=citations)

    return app


# ── Citation extraction ────────────────────────────────────────────────────

def extract_citations(data_result: dict) -> tuple[str, list[str]]:
    """Extract context text and formatted citation list from aquery_data result.

    Args:
        data_result: The 'data' dict from aquery_data() — contains entities,
                     relationships, chunks, and references.

    Returns:
        (context_text, citations) where:
          - context_text: formatted context string for the LLM prompt
          - citations: list of "[ref:N] file_path" strings
    """
    data = data_result.get("data", {})
    references = data.get("references", [])
    entities = data.get("entities", [])
    relationships = data.get("relationships", [])
    chunks = data.get("chunks", [])

    # Build reference_id → citation index mapping
    ref_map: dict[str, str] = {}
    for i, ref in enumerate(references):
        ref_id = ref.get("reference_id", "")
        file_path = ref.get("file_path", "unknown")
        ref_map[ref_id] = f"[ref:{i + 1}] {file_path}"

    # Build context lines with inline citation markers
    context_parts: list[str] = []

    if entities:
        context_parts.append("### Entities")
        for e in entities:
            ref_id = e.get("reference_id", "")
            citation = ref_map.get(ref_id, "")
            context_parts.append(
                f"- {e.get('entity_name', '?')} ({e.get('entity_type', 'unknown')}): "
                f"{e.get('description', '')} {citation}"
            )

    if relationships:
        context_parts.append("\n### Relationships")
        for r in relationships:
            ref_id = r.get("reference_id", "")
            citation = ref_map.get(ref_id, "")
            context_parts.append(
                f"- {r.get('src_id', '?')} → {r.get('tgt_id', '?')}: "
                f"{r.get('description', '')} (weight: {r.get('weight', 0):.2f}) {citation}"
            )

    if chunks:
        context_parts.append("\n### Source Chunks")
        for i, c in enumerate(chunks, 1):
            ref_id = c.get("reference_id", "")
            citation = ref_map.get(ref_id, "")
            context_parts.append(
                f"[Chunk {i}] {c.get('content', '')} {citation}"
            )

    context_text = "\n".join(context_parts) if context_parts else ""

    # Build final citation list
    citations = [ref_map.get(ref.get("reference_id", ""), "") for ref in references]
    citations = [c for c in citations if c]  # filter empties

    return context_text, citations
