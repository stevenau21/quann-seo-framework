# quann.homes LightRAG Infrastructure Map
## Last updated: 2026-05-27

### Network Architecture

```
Windows Host (Ollama proxy) at 127.0.0.1:11434
    │  :cloud suffix → cloud APIs (DeepSeek, Gemma, etc.)
    │
    ▼ host.docker.internal:11434
WSL2 — Docker containers access Ollama via host.docker.internal
```

### Running Instances (as of 2026-05-27)

| Service | Port | LLM Model | Embedding | Gleaning | Status |
|---------|------|-----------|-----------|----------|--------|
| lightrag-ui (SEO Methodology) | 8012 | deepseek-v4-pro:cloud | nomic-embed-text-v2-moe | 0 | ✅ 394 docs |
| lightrag-client-knowledge | 8013 | gemma4:31b-cloud | — | — | ✅ |
| lightrag-koray-lectures | 8014 | gemma4:31b-cloud | nomic-embed-text:latest (768-dim) | 0 | ✅ testing |

### Model Compatibility for Entity Extraction

**Working:**
- `gemma4:31b-cloud` — 4-9s/chunk, correct format, 0% failure rate
- `deepseek-v4-flash:cloud` — 20-57s/chunk, 30% failure rate (token caps)

**Broken:**
- `deepseek-v4-pro:cloud` — outputs to `thinking` field, `content` is empty. Reasoning model incompatible with LightRAG.

**Embedding models:**
- `nomic-embed-text:latest` (768-dim) — stable, recommended
- `nomic-embed-text-v2-moe` — UNSTABLE, dimension drifted 1024→1536. Do not use for new workspaces.

### Systemd Management

```bash
# Service files at /etc/systemd/system/lightrag-*.service
# Overrides at /etc/systemd/system/lightrag-*.service.d/override.conf
# Env files at /tmp/lightrag-ui-envs/<name>/.env
# Workspaces at /home/steve/lightrag-apps/<name>/workspace/

# Start/stop pattern:
sudo systemctl stop lightrag-koray-lectures
sudo systemctl reset-failed lightrag-koray-lectures
sudo systemctl start lightrag-koray-lectures
```

### Critical Configuration Rules

1. **MAX_GLEANING=0** is sufficient for lecture/conceptual content. 8012 (394 docs) proves it.
2. **EMBEDDING_DIM must match model output.** nomic-embed-text:latest = 768.
3. **Never download local models.** All routing via :cloud suffix.
4. **Test with one document before batch ingestion.**
5. **Systemctl start can hang silently.** Always follow with `curl /health` to verify.
