"""Local stand-in for GET /api/homekindle/dashboard.png without HAOS."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .fixtures import DEFAULT_FIXTURES
from .http_view import dashboard_response
from .layout import packaged_layout_path
from .render import render_png

PATH = "/api/homekindle/dashboard.png"


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_HEAD(self) -> None:
        self._handle(write_body=False)

    def do_GET(self) -> None:
        self._handle(write_body=True)

    def _handle(self, *, write_body: bool) -> None:
        if self.path.split("?", 1)[0] != PATH:
            self.send_error(404)
            return
        layout = packaged_layout_path()
        if not layout.is_file():
            studio = Path(__file__).resolve().parents[3] / "gf-program" / "dashboards" / "kindle.yaml"
            layout = studio
        png = render_png(DEFAULT_FIXTURES, layout)
        status, headers, body = dashboard_response(png, self.headers.get("If-None-Match"))
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if write_body and body:
            self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8129) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), DashboardHandler)
