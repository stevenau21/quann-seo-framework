#!/usr/bin/env bash
set -euo pipefail
echo "=== Nexus LightRAG Setup ==="

# ── 1. Detect repo root ──
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# ── 2. Create venv if missing ──
if [ ! -d "lightrag-env" ]; then
    echo "[1/4] Creating Python venv..."
    python3 -m venv lightrag-env
fi

# ── 3. Install dependencies ──
echo "[2/4] Installing Python packages..."
./lightrag-env/bin/pip install -r requirements.txt --quiet

# ── 4. Check for workspace data ──
echo "[3/4] Checking workspaces..."
for bot in quann-chat seo-methodology; do
    ws="$REPO/$bot/workspace"
    if [ ! -f "$ws/vdb_chunks.json" ]; then
        echo "  ⚠ $bot: workspace empty (needs indexing)"
    else
        echo "  ✓ $bot: workspace ready"
    fi
done

# ── 5. Set up systemd services ──
echo "[4/4] Installing systemd units..."
for bot in quann-chat seo-methodology; do
    UNIT="/etc/systemd/system/$bot.service"
    sudo tee "$UNIT" > /dev/null << EOF
[Unit]
Description=$bot LightRAG Server
After=network.target

[Service]
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONUNBUFFERED=1
Type=simple
User=$(whoami)
WorkingDirectory=$REPO/$bot
Environment=PATH=$REPO/lightrag-env/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$REPO/lightrag-env/bin/python3 $REPO/$bot/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF
done
sudo systemctl daemon-reload
sudo systemctl enable --now quann-chat seo-methodology 2>/dev/null || echo "  (run 'sudo systemctl start quann-chat seo-methodology' to start)"

echo ""
echo "=== Setup complete! ==="
echo "  quann-chat:       http://localhost:8001/health"
echo "  seo-methodology:  http://localhost:8002/health"
echo ""
echo "=== LightRAG Built-in Web UI ==="
echo "  Launch: cd /tmp/lightrag-ui && source \$REPO/lightrag-env/bin/activate && lightrag-server"
echo "  Open:   http://localhost:8010/webui/"
echo "  Docs:   http://localhost:8010/docs"
echo "  (See REINSTALL.md Step 7-B for full instructions)"
echo ""
echo "To add a new bot: copy one of the server.py files and create a new config."
