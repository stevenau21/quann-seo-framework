# LightRAG Infrastructure Rules — quann.homes Server
## Last updated: 2026-05-27

### ⛔ NEVER DO THESE (hard blocks)
- **NEVER download local Ollama models.** All models route through `:cloud` suffix.
- **NEVER set MAX_GLEANING > 0.** Causes extraction timeouts on large documents.
- **NEVER use `nomic-embed-text-v2-moe`.** Vector dimension drift (1024→1536) breaks workspaces.
- **NEVER wipe an existing workspace without explicit user permission.** Data loss is irreversible.

---

## 1. Network Architecture

```
┌─────────────────────────────────────────────────┐
│ Windows Host (Ollama proxy)                      │
│ 127.0.0.1:11434                                  │
│                                                   │
│ ollama serve routes :cloud models → cloud APIs   │
│ ─────────────────────────────────────────────── │
│ deepseek-v4-pro:cloud  → Ollama Cloud            │
│ deepseek-v4-flash:cloud → Ollama Cloud            │
│ nomic-embed-text:latest → Local (768-dim)        │
└──────────────┬──────────────────────────────────┘
               │ host.docker.internal:11434
               │
┌──────────────▼──────────────────────────────────┐
│ WSL2 (this machine)                              │
│                                                   │
│ Docker containers access Windows Ollama via:      │
│   http://host.docker.internal:11434               │
│                                                   │
│ LightRAG instances (each in own Docker):          │
│   Port 8012 — koray-gubur (394 docs, WORKING)    │
│   Port 8014 — koray-lectures (88 transcripts)     │
│   Port 8002 — Nexus chatbot (not LightRAG)        │
└──────────────────────────────────────────────────┘
```

---

## 2. Model Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| LLM_BINDING | ollama | |
| LLM_BINDING_HOST | http://host.docker.internal:11434 | Windows Ollama proxy |
| LLM_MODEL | deepseek-v4-pro:cloud | `:cloud` suffix triggers cloud routing |
| EMBEDDING_BINDING | ollama | |
| EMBEDDING_BINDING_HOST | http://host.docker.internal:11434 | |
| EMBEDDING_MODEL | nomic-embed-text:latest | **NOT** v2-moe |
| EMBEDDING_DIM | 768 | Must match model output |
| MAX_GLEANING | 0 | **Critical** — prevents timeout |
| MAX_ASYNC | 4 | Parallel extraction workers |

---

## 3. Service Management

### lightrag-koray-gubur (8012) — REFERENCE
```bash
# Service file
/etc/systemd/system/lightrag-koray-gubur.service
# Override (sets MAX_GLEANING=0)
/etc/systemd/system/lightrag-koray-gubur.service.d/override.conf
# Workspace
/home/steve/lightrag-apps/koray-gubur/workspace/
# Env
/tmp/lightrag-ui-envs/koray-gubur/.env
```

### lightrag-koray-lectures (8014) — TARGET
```bash
# Service (systemd-managed Docker)
sudo systemctl [start|stop|restart] lightrag-koray-lectures
# Workspace
/home/steve/lightrag-apps/koray-lectures/workspace/
# Env
/tmp/lightrag-ui-envs/koray-lectures/.env
# Health check
curl http://localhost:8014/health
# Document insertion
curl -X POST http://localhost:8014/documents/text \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "file_path": "test.txt"}'
```

---

## 4. Troubleshooting

### Service hung on start
```bash
# Kill any zombie processes
sudo pkill -9 -f "lightrag.*8014"
# Check Docker container
docker ps -a | grep koray-lectures
docker logs <container_id> --tail 50
# Reset systemd and restart
sudo systemctl reset-failed lightrag-koray-lectures
sudo systemctl start lightrag-koray-lectures
```

### "Embedding dimension mismatch"
→ Wrong embedding model. Ensure `.env` has `nomic-embed-text:latest` + `EMBEDDING_DIM=768`.

### Timeout during extraction
→ `MAX_GLEANING` is not 0. Check `.env` and service override.

### "No response from provider"
→ Ollama Cloud API may be down or rate-limited. Check `docker logs` for the container.

---

## 5. Workspace & Data Safety

- **Workspaces contain kv_store and graph data.** Wiping loses all indexed knowledge.
- Batch ingestion scripts insert via `/documents/text` endpoint.
- Doc status tracked in `workspace/kv_store_doc_status.json`.
- Always verify ingestion with a test document before batch processing.
