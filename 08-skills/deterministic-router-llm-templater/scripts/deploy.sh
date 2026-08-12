#!/usr/bin/env bash
# deploy.sh — Safe deploy for QuanBot v3
# Usage: ./scripts/deploy.sh
#
# Hardening enforced:
#   1. Git pull latest
#   2. Purge ALL Python bytecode caches (__pycache__ + *.pyc)
#   3. Content smoke test on key strings before restart
#   4. systemd restart
#   5. Health + warm-up verification
#   6. Warm-up asserts response body contains expected personalized text

set -euo pipefail

PROJECT_DIR="/home/steve/quanbot-v3"
SERVICE="quanbot-v3"
PORT="8002"
WEBHOOK_PATH="/webhook/quanbot-v30"
HEALTH_URL="http://localhost:${PORT}/health"
WEBHOOK_URL="http://localhost:${PORT}${WEBHOOK_PATH}"

cd "$PROJECT_DIR"

echo "==> git pull"
git pull

echo "==> Purging Python bytecode caches"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "==> Smoke test: verifying personalized strings in source"
if ! grep -q "Quan's assistant" src/templater.py; then
    echo "ERROR: Missing 'Quan's assistant' in templater.py — abort deploy"
    exit 1
fi

echo "==> Restarting systemd service"
sudo systemctl daemon-reload
sudo systemctl restart "$SERVICE"

echo "==> Waiting for service health"
for i in {1..10}; do
    if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
        echo "   Health OK"
        break
    fi
    sleep 1
done

echo "==> Warm-up: greeting smoke test"
WARM_RESPONSE=$(curl -sf -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"subscriber_id\":\"warmup_$(date +%s)\",\"message\":\"hi\"}")

if echo "$WARM_RESPONSE" | grep -qi "assistant"; then
    echo "   Warm-up PASSED — response contains 'assistant'"
else
    echo "ERROR: Warm-up FAILED — response missing expected assistant greeting"
    echo "Raw response: $WARM_RESPONSE"
    exit 1
fi

echo "==> Deploy complete"
