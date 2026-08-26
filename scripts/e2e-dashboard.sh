#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${ROOT}/.venv/bin/python"
PORT="${HOMEKINDLE_E2E_PORT:-8129}"
"$PY" "$ROOT/scripts/serve_local.py" "$PORT" >/tmp/gf-homekindle-e2e.log 2>&1 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; }
trap cleanup EXIT
ok=0
for _ in $(seq 1 25); do
  if curl -sf "http://127.0.0.1:${PORT}/api/homekindle/dashboard.png" -o /tmp/gf-homekindle.png; then
    ok=1
    break
  fi
  sleep 0.2
done
test "$ok" = "1"
test -s /tmp/gf-homekindle.png
"$PY" - <<'PY'
from io import BytesIO
from pathlib import Path
from PIL import Image
img = Image.open(BytesIO(Path("/tmp/gf-homekindle.png").read_bytes()))
assert img.size == (600, 800), img.size
assert img.mode == "L", img.mode
print("e2e png ok", img.size, img.mode)
PY
ETAG=$(curl -sD - -o /dev/null "http://127.0.0.1:${PORT}/api/homekindle/dashboard.png" | awk -F': ' 'tolower($1)=="etag"{gsub("\r","",$2); print $2}')
CODE=$(curl -s -o /dev/null -w '%{http_code}' -H "If-None-Match: ${ETAG}" "http://127.0.0.1:${PORT}/api/homekindle/dashboard.png")
test "$CODE" = "304"
echo "e2e 304 ok"
