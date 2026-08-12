---
name: seo-rag-server
description: Custom FastAPI RAG chatbot server replacing Dify — serves both Holistic SEO Assistant and Quan Homes Chatbot via the same widget embed on quann.homes.
---

# SEO RAG Server

Replaces Dify's broken chatbot serving layer. Uses the same Weaviate vector DB (24,215 SEO segments + 444 Quan Homes segments) and Ollama cloud models.

## Architecture

```
Widget (quann.homes) → Cloudflare Tunnel → dify.quann.homes/v1 → nginx → host.docker.internal:5002 (FastAPI)
                                                                         ↓
                                                                  Weaviate (:8080) + Ollama Cloud
```

## Key Paths

| Path | Purpose |
|------|---------|
| `/home/steve/seo-rag/server.py` | Main FastAPI app |
| `/home/steve/seo-rag/.venv/` | Python venv |
| `/home/steve/seo-rag/seo_rag.db` | SQLite — sessions, blocklist, rate limits |
| `/home/steve/dify-seo-failures.json` | 209-entry failure log — DO NOT repeat any of these |
| `/home/steve/dify/docker/volumes/app/storage/` | Dify's old data (reference only) |

## Service

- **systemd unit**: `seo-rag` — enabled, auto-restart
- **Check**: `systemctl --user status seo-rag`
- **Logs**: `journalctl --user -u seo-rag -f`

## Apps & Tokens

| App | Token | Weaviate Class | Model |
|-----|-------|----------------|-------|
| Holistic SEO Assistant | `app-P0f44B7WF56gLXB1DexRWNfc` | `Vector_index_8cf14a7e` (24,215 segs) | `deepseek-v4-pro:cloud` |
| Quan Homes Chatbot | `app-2432fa8de1034c60917bcf437ef935c8` | `Vector_index_c7b711da` (444 segs) | `deepseek-v4-pro:cloud` |

## Dify Nginx Routing

Dify's nginx `conf.d` is volume-mounted. `/v1` routes to our server:
```
location /v1/ {
    proxy_pass http://host.docker.internal:5002;
    ...
}
```
To revert to Dify: restore `proxy_pass http://api:5001;`

## Embedding Model

- **Model**: `nomic-embed-text-v2-moe` (768-dim)
- **Pulled**: Must be present on Ollama (`ollama pull nomic-embed-text-v2-moe`)
- **Dify's original model**: exact match — vectors are compatible, no re-indexing needed

## Weaviate

- Container: `dify-weaviate-1` in `dify_default` network
- Port: `8080` exposed to host (added manually to compose)
- Access: `http://localhost:8080/v1/graphql`

## Dify Containers (STOPPED — do not restart)

- `dify-api-1`, `dify-worker-1`, `dify-worker_beat-1`, `dify-sandbox-1`, `dify-ssrf_proxy-1`, `dify-plugin_daemon-1`
- Kept: `dify-nginx-1`, `dify-weaviate-1`, `dify-db-1` (postgres), `dify-redis-1`

## Admin Endpoints (require `Auth: Bearer hermes-admin-seo-rag-2026`)

```
POST /v1/admin/block  {"ip": "1.2.3.4", "reason": "spam"}
GET  /v1/admin/stats
GET  /v1/admin/blocklist
DELETE /v1/admin/block/{ip}
```

## Features

- Rate limiting: 10 req/min per IP
- Session TTL: 24h
- IP blocklist with reason tracking
- Per-app system prompts
- Source citations in responses
- Conversation history within session

## Known Pitfalls

- **ALWAYS pull live data from Weaviate/RAG before planning SEO work** — never rely on skill doc metadata alone. The skill doc only stores architecture/config, NOT actual content topics. For anything content-related (topical maps, gap analysis, taxonomy), query Weaviate directly: `curl -s http://localhost:8080/v1/graphql -H "Authorization: Bearer $WEAVIATE_KEY" ...` and use the RAG endpoint at `http://localhost:5002/v1/chat-messages` with `MAX_CONTEXT_CHUNKS` bumped up or batched queries per topic area.

1. **Never use `nomic-embed-text:v1.5`** — wrong model, different vector space. Only `v2-moe`.
2. **Dify admin console** — `admin@quann.homes / Lawof1!!` fails with encryption mismatch. Don't retry.
3. **Weaviate port** — must be exposed in compose. If restart removes it, re-add.
4. **Cloud-stub models** — end with `:cloud`. Dify's plugin daemon rejects them (model_schema: null). Our server doesn't care.
5. **Dify tenant ID**: `18e666a4-1fc6-450c-a1d8-e94453b91257` (for DB lookups only)
