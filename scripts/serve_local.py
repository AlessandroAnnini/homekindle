"""Run the fixture PNG stand-in: GET /api/homekindle/dashboard.png"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from custom_components.homekindle.local_server import serve

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8129
    httpd = serve(port=port)
    print(f"listening 127.0.0.1:{port}", flush=True)
    httpd.serve_forever()
