# LightRAG Ingestion Failure Catalog & Pre-Flight Checklist

> **Why this exists:** Every architect ingestion will face the same failure modes. Documenting them once prevents rediscovery on each new notebook.
> **Linked from:** `knowledge-synthesis-architecture` → Architect Pipeline → Phase 1: Collection

---

## Failure Catalog (Root Cause Analysis)

### F1: httpx.ReadTimeout — Slow Extraction Model

**Symptom:** Backend logs show `httpx.ReadTimeout` on chunk extraction. Documents marked "failed" with `unknown_source`.

**Root cause:** Deep reasoning models (deepseek-v4-pro, claude-sonnet) take 60-120s per chunk. Large documents (50K chars) produce 60+ chunks. WSL2 TCP keepalive (10s) keeps idle connections alive but doesn't help when the LLM call itself times out.

**Chain:**
```
Large doc (50K chars) → 60+ chunks → LLM call per chunk (120s each) → 
httpx client timeout (default ~120s) → ReadTimeout → chunk fails → 
retry chain exhausted → doc marked "failed"
```

**Fix:**
1. Switch to fast extraction model BEFORE ingestion: `gemma4:31b-cloud` (30-60s per chunk)
2. Set `LLM_TIMEOUT=600` in .env (safety net)
3. Switch back to deep model AFTER all extraction completes
4. Never run extraction with reasoning-tier models

**Prevention:** Embed model check into pre-flight script.

### F2: WSL2 TCP Connection Drops

**Symptom:** Silent extraction failures — docs stuck in "pending" forever, zero "processed" after 10+ minutes.

**Root cause:** WSL2 virtual switch drops idle TCP connections after ~30s. LLM extraction calls to Windows-hosted Ollama (192.168.4.148:11434) take 15-60s, straddling the idle timeout boundary.

**Fix:**
```bash
sudo sysctl -w net.ipv4.tcp_keepalive_time=10
sudo sysctl -w net.ipv4.tcp_keepalive_intvl=5
sudo sysctl -w net.ipv4.tcp_keepalive_probes=3
```
Persist via `/etc/sysctl.d/99-wsl2-keepalive.conf`.

**Verification:** Run a long LLM call (200 tokens) before trusting the pipeline:
```bash
curl -s "http://192.168.4.148:11434/api/generate" -d '{
  "model": "gemma4:31b-cloud",
  "prompt": "Explain SEO in one paragraph.",
  "stream": false,
  "options": {"num_predict": 200}
}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('response','')),'chars')"
# Must return >100 chars
```

### F3: Permission Denied on Log File

**Symptom:** Backend crashes on start with `PermissionError: [Errno 13] Permission denied: '/tmp/lightrag-ui-envs/{name}/lightrag.log'`.

**Root cause:** `mkdir -p` with sudo creates the env directory as root. The backend runs as user `steve` and can't write logs.

**Fix:** `sudo chown -R steve:steve /tmp/lightrag-ui-envs/{name}/` after directory creation.

### F4: Systemd Stop Hangs During Active Processing

**Symptom:** `systemctl stop` times out after 90s. Backend stuck in `deactivating (stop-sigterm)`.

**Root cause:** Active LLM extraction pipeline holds open file handles and HTTP connections. SIGTERM is queued behind the extraction coroutine.

**Fix:**
```bash
sudo systemctl kill -s SIGKILL lightrag-{name}
sudo systemctl reset-failed lightrag-{name}
```
WSL2 systemd may reject SIGKILL to auxiliary processes — kill PID directly if needed: `sudo pkill -f "lightrag.*{port}"`.

### F5: Backend Crash Loops During Ingestion

**Symptom:** `sudo systemctl show lightrag-{name} -p NRestarts` shows > 10 restarts. Most docs stuck in "pending."

**Root cause:** Unstable backend (memory, model connection, or config issue) causes repeated crashes. Each restart resets the in-memory processing queue. Documents never get extracted.

**Fix:** Check `sudo journalctl -u lightrag-{name} --no-pager -n 50` for root cause. Fix stability before resuming ingestion.

### F6: Zombie Ports Blocking Restart

**Symptom:** Backend won't start. `ss -tlnp | grep {port}` shows a process still holding the port but it's a zombie from a previous crash.

**Fix:**
```bash
sudo pkill -f "lightrag.*{port}" 2>/dev/null
# or find PID and kill:
ss -tlnp | grep {port} | grep -oP 'pid=\K\d+' | xargs sudo kill -9
```

### F7: Embedding Model Mismatch

**Symptom:** Queries return garbage results. Graph seems healthy but retrieval is broken.

**Root cause:** Different embedding models used for insert vs query (e.g., nomic-embed-text:v1.5 for index, v2-moe for service). Vectors in incompatible coordinate spaces.

**Fix:** One embedding model per notebook, forever. Verify:
```bash
grep EMBEDDING_MODEL /tmp/lightrag-ui-envs/{name}/.env
```
Current standard: `nomic-embed-text-v2-moe` (768-dim).

### F8: Gleaning Wastes Token Budget

**Symptom:** 2x token cost per chunk, no quality improvement for structured content.

**Root cause:** LightRAG defaults `MAX_GLEANING=1`, which runs a second LLM pass ("what did I miss?") per chunk. For blog posts and structured content, this is pure waste.

**Fix:** Set `MAX_GLEANING=0` via systemd override:
```bash
sudo mkdir -p /etc/systemd/system/lightrag-{name}.service.d
sudo tee /etc/systemd/system/lightrag-{name}.service.d/override.conf << 'EOF'
[Service]
Environment=MAX_GLEANING=0
EOF
```

### F9: File Path = unknown_source

**Symptom:** All failed docs show `unknown_source` in logs. Can't map back to original URLs.

**Root cause:** LightRAG's `/documents/text` API stores `file_path` from the `url` field in the request. If the URL isn't provided or is empty, it defaults to `unknown_source`.

**Fix:** Always pass real URL as `url` parameter in POST to `/documents/text`.

---

## Pre-Flight Checklist (Run BEFORE Any Architect Ingestion)

### 1. Environment Check
```bash
# WSL2 keepalive active?
sysctl net.ipv4.tcp_keepalive_time | grep -q "10" && echo "✅ keepalive" || echo "❌ FIX keepalive"

# Ollama reachable?
curl -s --max-time 5 http://192.168.4.148:11434/api/tags | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ {len(d.get(\"models\",[]))} models')" 2>/dev/null || echo "❌ Ollama DOWN"
```

### 2. Model Check
```bash
# Extraction model must be fast (gemma4, not deepseek/claude)
grep LLM_MODEL /tmp/lightrag-ui-envs/{name}/.env | grep -q "gemma4" && echo "✅ fast extraction model" || echo "❌ WRONG MODEL — switch to gemma4:31b-cloud"

# Timeout must be high
grep -q "LLM_TIMEOUT=600" /tmp/lightrag-ui-envs/{name}/.env && echo "✅ timeout 600s" || echo "❌ ADD LLM_TIMEOUT=600"

# Gleaning must be OFF
grep -q "MAX_GLEANING=0" /etc/systemd/system/lightrag-{name}.service.d/override.conf 2>/dev/null && echo "✅ gleaning off" || echo "❌ ADD MAX_GLEANING=0 override"

# Embedding model must match standard
grep -q "nomic-embed-text-v2-moe" /tmp/lightrag-ui-envs/{name}/.env && echo "✅ embedding model standard" || echo "❌ WRONG EMBEDDING MODEL"
```

### 3. Backend Health
```bash
# Service alive?
sudo systemctl is-active lightrag-{name} | grep -q "active" && echo "✅ backend running" || echo "❌ START backend"

# No crash loops?
RESTARTS=$(sudo systemctl show lightrag-{name} -p NRestarts | cut -d= -f2)
[ "$RESTARTS" -lt 5 ] && echo "✅ stable ($RESTARTS restarts)" || echo "❌ UNSTABLE — $RESTARTS restarts, investigate"

# Port available?
curl -s http://127.0.0.1:{port}/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'✅ {d.get(\"status\")}')" 2>/dev/null || echo "❌ BACKEND UNREACHABLE"

# Permissions correct?
sudo -u steve test -w /tmp/lightrag-ui-envs/{name}/ && echo "✅ writeable" || echo "❌ FIX PERMISSIONS"
```

### 4. Document State
```bash
# Clean slate or intentional continuation?
curl -s http://127.0.0.1:{port}/documents/status_counts | python3 -c "
import json,sys
d=json.load(sys.stdin)['status_counts']
total = d['pending']+d['processing']+d['processed']+d['failed']
print(f'Existing docs: {total} | Pending: {d[\"pending\"]} | Processed: {d[\"processed\"]} | Failed: {d[\"failed\"]}')
"
```

### 5. Ingestion Script Check
- [ ] Uses real URLs as `file_path`
- [ ] Batched (5 per cycle) with scan after each batch
- [ ] Polls `status_counts` and waits for processing before next batch
- [ ] Rate-limited (0.3s between inserts)
- [ ] Saves state file after each batch for crash recovery
- [ ] Logs to file for post-mortem

### 6. Monitoring
```bash
# 10-min health check cron for the duration
cronjob(action='create', name='{architect} Ingestion Monitor',
    schedule='*/10 * * * *', repeat=18, deliver='origin',
    enabled_toolsets=['terminal', 'web'],
    prompt='Check backend health, doc status counts, Ollama reachability. If processed count unchanged for 30 min, trigger re-scan. Report failures.')
```

---

## Recovery Procedures

### Recovering Failed Documents
```python
# Reset failed docs to pending so they get retried on next scan
import json
with open('workspace/kv_store_doc_status.json') as f:
    status = json.load(f)

recovered = 0
for k, v in status.items():
    if v.get('status') == 'failed':
        v['status'] = 'pending'
        recovered += 1

with open('workspace/kv_store_doc_status.json', 'w') as f:
    json.dump(status, f, indent=2)

print(f"Recovered {recovered} docs to pending")
```

Then trigger a scan: `curl -X POST http://127.0.0.1:{port}/documents/scan`

---

## Post-Ingestion Actions

1. **Verify completion:** `curl http://127.0.0.1:{port}/documents/status_counts` — zero pending
2. **Switch to deep model** for reasoning if needed:
   ```bash
   sudo sed -i 's/LLM_MODEL=.*/LLM_MODEL=deepseek-v4-pro:cloud/' /tmp/lightrag-ui-envs/{name}/.env
   sudo systemctl restart lightrag-{name}
   ```
3. **Save state snapshot** for incremental updates later
4. **Log ingestion stats:** total docs, success rate, duration, errors encountered
