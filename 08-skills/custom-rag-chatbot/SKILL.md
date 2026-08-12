---
name: custom-rag-chatbot
description: Build and deploy a custom RAG chatbot (FastAPI + Ollama + Weaviate) as a drop-in Dify replacement. Same widget embed code, same API format, zero Dify dependency.
category: integrations
---

# Custom RAG Chatbot (Dify Replacement)

Replace a broken Dify instance with a custom FastAPI RAG server that reuses Dify's existing Weaviate vector data. The widget embed code on the website stays identical — only the backend changes.

## When to use

- Dify is broken (plugin daemon issues, `model_schema: null`, inaccessible admin console)
- You need to keep the same widget embed code and API token format
- Vector data is already indexed in Weaviate (or other vector DB)
- Cloud LLM + local embedding models via Ollama

## Architecture

```
Widget (quann.homes)
  → POST /v1/chat-messages (Bearer app-xxx)
    → FastAPI server (Docker, dify_default network)
      → embed query (nomic-embed-text-v2-moe via Ollama)
      → search Weaviate (nearVector)
      → call LLM (deepseek-v4-pro:cloud via Ollama v1)
      → return Dify-format JSON response
```

## Critical pitfalls

### 1. Embedding model compatibility is unforgiving
`nomic-embed-text:v1.5` and `nomic-embed-text-v2-moe` produce **incompatible vectors**. Distance scores will be ~1.0 (orthogonal) if models don't match. Always use the exact model that indexed the data. Check with: `docker exec dify-db_postgres-1 psql -U postgres -d dify -c "SELECT embedding_model FROM datasets;"`

### 2. Weaviate port is NOT exposed by default
Dify's Weaviate has no port mapping — it's Docker-internal only. From WSL, you cannot reach `localhost:8080` or the container IP.

**Solution A (Docker-based)**: Run the RAG server inside a Docker container on the same compose network (`dify_default`), where `weaviate:8080` resolves natively.

**Solution B (systemd/host-based — preferred for production)**: Add port mapping to Weaviate in the compose file, then restart:
```yaml
weaviate:
  restart: always
  ports:
    - "8080:8080"   # add these 2 lines
  volumes:
```
Restart with the correct project name:
```bash
docker compose -p dify --profile weaviate up -d weaviate
```
Then the RAG server can reach `http://localhost:8080` from WSL.

### 2b. Docker compose project name matters
Dify's original stack was started as project `dify`. Running `docker compose up` without `-p dify` creates a new project (`docker`) with a duplicate Weaviate container — NOT the one with your data. Always use `-p dify` when operating on the original stack.

### 3. Cloud-stub models return `model_schema: null`
Dify's plugin daemon validates models against their schema. Cloud-stub Ollama models (`:cloud` suffix) return empty schema, so all providers (ollama, openai_api_compatible) fail. This is the root cause of Dify being unfixable — don't waste time trying.

### 4. API token format must match
Dify widget uses `Authorization: Bearer app-<token>`. Our server must accept those exact tokens. Map them to internal app IDs:
```python
API_TOKENS = {
    "app-P0f44B7WF56gLXB1DexRWNfc": "holistic_seo",
    "app-2432fa8de1034c60917bcf437ef935c8": "quan_homes",
}
```

### 5. Ollama v1 endpoint needs API key
Cloud-hosted Ollama requires Bearer auth: `Authorization: Bearer gg4L2rt6kzjJA8kk` on the `/v1/chat/completions` endpoint.

## Deployment

### Option A: systemd service (recommended for production)

1. Create venv: `python3 -m venv /home/steve/seo-rag/.venv && .venv/bin/pip install fastapi uvicorn httpx`
2. Install service: `sudo cp seo-rag.service /etc/systemd/system/ && sudo systemctl enable --now seo-rag`
3. Verify: `curl http://localhost:5002/health`
4. Wire nginx: replace Dify's `/v1` upstream with `host.docker.internal:5002`

### Option B: Docker container

1. Build: `docker build -t seo-rag .` (from `/home/steve/seo-rag/`)
2. Run on dify network: `docker run -d --name seo-rag --network dify_default -p 5002:5002 seo-rag`
3. Health check: `curl http://localhost:5002/health`
4. Test: `curl -X POST http://localhost:5002/v1/chat-messages ...`
5. Wire nginx: replace Dify upstream with `http://seo-rag:5002` (Docker hostname)

### Nginx proxy wiring

Dify's nginx routes `/v1` → `api:5001`. Change to point at our server:
```nginx
location /v1 {
    proxy_pass http://host.docker.internal:5002;  # systemd
    # or: proxy_pass http://seo-rag:5002;         # Docker
    include proxy.conf;
}
```
Reload: `docker exec dify-nginx-1 nginx -s reload`

**Warning**: This is runtime-only. If Dify's nginx container restarts, the change is lost. Either patch the compose file or add a startup script. For now, use a one-liner after any Dify restart:
```bash
docker exec dify-nginx-1 sed -i 's|seo-rag:5002|host.docker.internal:5002|' /etc/nginx/conf.d/default.conf && docker exec dify-nginx-1 nginx -s reload
```

## Key files

- `/home/steve/seo-rag/server.py` — Full FastAPI server with Dify-compatible API
- `/home/steve/seo-rag/Dockerfile` — Minimal Python 3.11-slim container
- `/home/steve/seo-rag/seo_rag.db` — SQLite DB (auto-created) for sessions, blocklist, rate limits
- `/home/steve/dify-install/docker/docker-compose.yaml` — Dify compose (Weaviate at line 1182)

## Weaviate collections (reused from Dify)

- `Vector_index_c8b822da_da9e_4b7f_b7fb_005d7e23ebb3_Node` — Holistic SEO Knowledge Base (24,215 segments)
- `Vector_index_c7b711da_c9cb_4b7e_b6ea_004d6e12dba2_Node` — Quan Homes Knowledge (444 segments)

Access via GraphQL with `nearVector`:
```graphql
{ Get { Vector_index_c8b822da_da9e_4b7f_b7fb_005d7e23ebb3_Node(
  limit: 5
  nearVector: { vector: [...] }
) { text document_id doc_type _additional { distance } } } }
```

## Verified pipeline results

Query: "What are on-page SEO ranking factors?"
- Top hit distance: 0.3997 (excellent relevance)
- All 5 results: on-page SEO topics, no false positives
- LLM answer: specific factors from context, with source citations
