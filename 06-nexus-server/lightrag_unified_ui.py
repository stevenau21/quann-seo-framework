#!/usr/bin/env python3
"""Unified LightRAG UI proxy — one URL, all notebooks.
Serves a landing page at / with notebook cards. Each notebook's
LightRAG Web UI runs on its own port, proxied by this server.

Usage: python3 lightrag_unified_ui.py
Ports:  8010 = this proxy (public)
        8011 = quann-chat LightRAG UI
        8012 = seo-methodology LightRAG UI
"""

import asyncio, subprocess, signal, os, sys, time, socket
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────
PROXY_PORT = 8010
OLLAMA_HOST = "host.docker.internal"
OLLAMA_PORT = 11434
VENV = "/home/steve/lightrag-env"
PYTHON = f"{VENV}/bin/python3"
LIGHTRAG_SERVER = f"{VENV}/bin/lightrag-server"
ENV_DIR = Path("/tmp/lightrag-ui-envs")
RUNTIME_DIR = Path("/tmp/lightrag-ui-runtime")
HEALTH_TIMEOUT = 60  # seconds to wait for each UI to start

NOTEBOOKS = [
    {
        "name": "quann-chat",
        "title": "🏠 Quann Chat",
        "desc": "Quan Nguyen's real estate knowledge graph — 896 entities, 957 relations across quann.homes",
        "workspace": "/home/steve/lightrag-apps/quann-chat/workspace",
        "port": 8011,
        "llm_model": "gemma4:31b-cloud",
        "embed_model": "nomic-embed-text-v2-moe",
        "color": "#3b82f6",
    },
    {
        "name": "seo-methodology",
        "title": "🔍 SEO Methodology",
        "desc": "Entity-based SEO research from holisticseo.digital — structured semantic search, topical mapping",
        "workspace": "/home/steve/lightrag-apps/seo-methodology/workspace",
        "port": 8012,
        "llm_model": "deepseek-v4-pro:cloud",
        "embed_model": "nomic-embed-text-v2-moe",
        "color": "#10b981",
    },
]


# ── Landing HTML ────────────────────────────────────────────────────────────
LANDING = """<!DOCTYPE html>
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
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px;max-width:800px;width:100%}
.card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:28px 24px;cursor:pointer;transition:all .2s;text-decoration:none;color:inherit;display:block}
.card:hover{border-color:{color};transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,.3)}
.card h2{font-size:1.15rem;margin-bottom:8px}
.card p{color:#94a3b8;font-size:0.9rem;line-height:1.5}
.card .tag{display:inline-block;background:{color};color:#fff;padding:4px 10px;border-radius:6px;font-size:0.75rem;margin-top:12px}
.status-row{display:flex;align-items:center;gap:8px;margin-bottom:20px}
.dot{width:8px;height:8px;border-radius:50%}
.dot.green{background:#10b981}
.dot.red{background:#ef4444}
.dot.yellow{background:#f59e0b}
.status-text{font-size:0.85rem;color:#94a3b8}
</style>
</head>
<body>
<h1>🧠 LightRAG Knowledge Explorer</h1>
<p class="subtitle">Visual knowledge graphs, document search, entity exploration</p>
<div class="status-row" id="status"></div>
<div class="grid" id="cards"></div>
<script>
const NOTEBOOKS = {notebooks_json};

async function checkStatus() {
    const statusEl = document.getElementById('status');
    // Health check via the proxy's own /health endpoint
    try {
        const r = await fetch('/health', {signal: AbortSignal.timeout(3000)});
        if (r.ok) {
            const data = await r.json();
            const statuses = data.notebooks || {};
            const allUp = Object.values(statuses).every(s => s === 'up');
            const anyUp = Object.values(statuses).some(s => s === 'up');
            statusEl.innerHTML = allUp
                ? '<span class="dot green"></span><span class="status-text">All notebooks ready</span>'
                : anyUp
                ? '<span class="dot yellow"></span><span class="status-text">Some notebooks loading...</span>'
                : '<span class="dot red"></span><span class="status-text">Starting up — check back in a few seconds</span>';
            return;
        }
    } catch(e) {}
    statusEl.innerHTML = '<span class="dot yellow"></span><span class="status-text">Connecting...</span>';
}

// Render cards
document.getElementById('cards').innerHTML = NOTEBOOKS.map(n => `
    <a href="${n.link || '/ui/' + n.name + '/webui/'}" class="card" style="--color:${n.color}">`
        <h2>${n.title}</h2>
        <p>${n.desc}</p>
        <span class="tag" style="background:${n.color}">Open →</span>
    </a>
`).join('');

checkStatus();
setInterval(checkStatus, 5000);
</script>
</body>
</html>"""


# ── Helpers ─────────────────────────────────────────────────────────────────
def write_env(nb: dict) -> Path:
    """Write .env file for a notebook's lightrag-server instance."""
    env_dir = ENV_DIR / nb["name"]
    env_dir.mkdir(parents=True, exist_ok=True)
    env_path = env_dir / ".env"

    content = f"""WORKING_DIR={nb['workspace']}
HOST=0.0.0.0
PORT={nb['port']}
LLM_BINDING=ollama
LLM_BINDING_HOST=http://{OLLAMA_HOST}:{OLLAMA_PORT}
LLM_MODEL={nb['llm_model']}
EMBEDDING_BINDING=ollama
EMBEDDING_BINDING_HOST=http://{OLLAMA_HOST}:{OLLAMA_PORT}
EMBEDDING_MODEL={nb['embed_model']}
EMBEDDING_DIM=768
TOP_K=20
WEBUI_TITLE={nb['title']}
LOG_LEVEL=WARNING
MAX_ASYNC=4
MAX_TOKENS=***
TEMPERATURE=0.4
ENABLE_LLM_CACHE_FOR_EXTRACT=true
ADDON_PARAMS={{"example_number":1,"language":"English","entity_types":["organization","person","geo","event","category"]}}
"""
    env_path.write_text(content)
    return env_dir


def check_port(port: int) -> bool:
    """Check if a port is listening."""
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=1)
        s.close()
        return True
    except Exception:
        return False


# ── Proxy server ────────────────────────────────────────────────────────────
import urllib.request as urllib_req
from http.server import HTTPServer, BaseHTTPRequestHandler


class ProxyHandler(BaseHTTPRequestHandler):
    """Reverse proxy: /ui/<notebook>/* → localhost:<port>/*"""

    notebook_map = {}  # {name: port} — set at startup

    def log_message(self, format, *args):
        pass  # silent

    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")

    def do_PUT(self):
        self._proxy("PUT")

    def do_DELETE(self):
        self._proxy("DELETE")

    def _proxy(self, method):
        path = self.path

        # Landing page
        if path == "/" or path == "/index.html":
            notebook_data = [
                {"name": nb["name"], "title": nb["title"], "desc": nb["desc"],
                 "port": nb["port"], "color": nb["color"], "link": nb.get("link", "/ui/" + nb["name"] + "/webui/")}
                for nb in NOTEBOOKS
            ]
            html = LANDING
            # Replace {notebooks_json} with actual JSON
            import json as _json
            html = html.replace("{notebooks_json}", _json.dumps(notebook_data))
            html = html.replace("{color}", "#3b82f6")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # Health
        if path == "/health":
            statuses = {}
            for nb in NOTEBOOKS:
                try:
                    r = urllib_req.urlopen(f"http://127.0.0.1:{nb['port']}/health", timeout=3)
                    statuses[nb["name"]] = "up" if r.status == 200 else "error"
                except Exception:
                    statuses[nb["name"]] = "down"
            import json as _json
            body = _json.dumps({"status": "healthy", "notebooks": statuses}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        # Proxy /ui/<notebook>/<rest...> → <notebook_port>/<rest...>
        parts = path.lstrip("/").split("/", 2)
        if len(parts) >= 2 and parts[0] == "ui":
            notebook_name = parts[1]
            remaining = parts[2] if len(parts) > 2 else ""

            if notebook_name not in self.notebook_map:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Notebook not found")
                return

            port = self.notebook_map[notebook_name]
            target_url = f"http://127.0.0.1:{port}/{remaining}"

            # Read request body for POST/PUT
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else None

            try:
                req = urllib_req.Request(target_url, data=body, method=method)
                # Copy relevant headers
                for h in ["Content-Type", "Accept", "Authorization"]:
                    if h in self.headers:
                        req.add_header(h, self.headers[h])

                resp = urllib_req.urlopen(req, timeout=120)
                resp_data = resp.read()
                resp_headers = dict(resp.getheaders())

                # Rewrite asset paths in HTML responses from /webui/ → /ui/<notebook>/webui/
                content_type = resp_headers.get("Content-Type", "")
                if "text/html" in content_type or "/webui" in path:
                    html = resp_data.decode("utf-8", errors="replace")
                    # Rewrite root-relative /webui paths AND root-relative API paths
                    html = html.replace('"/webui/', f'"/ui/{notebook_name}/webui/')
                    html = html.replace("'/webui/", f"'/ui/{notebook_name}/webui/")
                    # Also fix favicon
                    html = html.replace('href="favicon.png"', f'href="/ui/{notebook_name}/webui/favicon.png"')
                    resp_data = html.encode("utf-8")

                self.send_response(resp.status)
                for h, v in resp_headers.items():
                    if h.lower() not in ("transfer-encoding", "connection", "content-length"):
                        self.send_header(h, v)
                self.send_header("Content-Length", str(len(resp_data)))
                self.end_headers()
                self.wfile.write(resp_data)
            except Exception as e:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(f"Proxy error: {e}".encode())
            return

        # Root-relative API: WebUI JS calls /graph/label/popular, /documents/status_counts, etc.
        # Extract notebook from Referer header (e.g., ".../ui/quann-chat/webui/...")
        referer = self.headers.get("Referer", "")
        import re
        m = re.search(r'/ui/([a-z0-9_-]+)/', referer)
        if m and m.group(1) in self.notebook_map:
            notebook_name = m.group(1)
            port = self.notebook_map[notebook_name]
            target_url = f"http://127.0.0.1:{port}/{path.lstrip('/')}"

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length else None

            try:
                req = urllib_req.Request(target_url, data=body, method=method)
                for h in ["Content-Type", "Accept", "Authorization"]:
                    if h in self.headers:
                        req.add_header(h, self.headers[h])

                resp = urllib_req.urlopen(req, timeout=120)
                resp_data = resp.read()
                resp_headers = dict(resp.getheaders())

                self.send_response(resp.status)
                for h, v in resp_headers.items():
                    if h.lower() not in ("transfer-encoding", "connection", "content-length"):
                        self.send_header(h, v)
                self.send_header("Content-Length", str(len(resp_data)))
                self.end_headers()
                self.wfile.write(resp_data)
            except Exception:
                self.send_response(502)
                self.end_headers()
                self.wfile.write(b"Backend error")
            return

        # Fallback: redirect to landing
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    import json

    # Split notebooks: auto-launched (lightrag-server) vs external (systemd/Nexus)
    local_nbs = [nb for nb in NOTEBOOKS if not nb.get("external")]

    # 1. Write .env files (only for local lightrag-server notebooks)
    print("→ Writing .env files...")
    for nb in local_nbs:
        env_dir = write_env(nb)
        print(f"  {nb['name']}: {env_dir}/.env")

    # 2. Launch lightrag-server for each local notebook
    print("→ Launching LightRAG UI servers...")
    processes = {}
    for nb in local_nbs:
        log_file = RUNTIME_DIR / f"{nb['name']}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        env_dir = ENV_DIR / nb["name"]

        proc = subprocess.Popen(
            [LIGHTRAG_SERVER],
            cwd=str(env_dir),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            stdout=open(str(log_file), "w"),
            stderr=subprocess.STDOUT,
        )
        processes[nb["name"]] = proc
        print(f"  {nb['name']}: pid={proc.pid} port={nb['port']}")

    # 3. Wait for all to be ready
    print(f"→ Waiting for servers to be ready (timeout={HEALTH_TIMEOUT}s)...")
    deadline = time.time() + HEALTH_TIMEOUT
    ready = set()
    while time.time() < deadline and len(ready) < len(local_nbs):
        for nb in local_nbs:
            if nb["name"] not in ready and check_port(nb["port"]):
                # Verify health endpoint
                try:
                    r = urllib_req.urlopen(f"http://127.0.0.1:{nb['port']}/health", timeout=3)
                    if r.status == 200:
                        ready.add(nb["name"])
                        print(f"  ✅ {nb['name']} ready on port {nb['port']}")
                except Exception:
                    pass
        time.sleep(2)

    missing = set(nb["name"] for nb in local_nbs) - ready
    if missing:
        print(f"  ⚠️ Timed out waiting for: {missing}")

    # 4. Start proxy — register ALL notebooks (including external) for routing
    print(f"→ Starting proxy on port {PROXY_PORT}...")
    ProxyHandler.notebook_map = {nb["name"]: nb["port"] for nb in NOTEBOOKS}
    server = HTTPServer(("0.0.0.0", PROXY_PORT), ProxyHandler)
    print(f"  ✅ Proxy listening on http://0.0.0.0:{PROXY_PORT}")
    print(f"  → Quann Chat: /ui/quann-chat/webui/")
    print(f"  → SEO:         /ui/seo-methodology/webui/")

    # Check external notebooks
    for nb in NOTEBOOKS:
        if nb.get("external"):
            if check_port(nb["port"]):
                print(f"  ✅ {nb['name']} (external) ready on port {nb['port']}")
            else:
                print(f"  ⚠️ {nb['name']} (external) NOT reachable on port {nb['port']}")

    # Cleanup on shutdown
    def shutdown(sig, frame):
        print("\n→ Shutting down...")
        server.shutdown()
        for name, proc in processes.items():
            print(f"  Stopping {name} (pid={proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    server.serve_forever()


if __name__ == "__main__":
    main()
