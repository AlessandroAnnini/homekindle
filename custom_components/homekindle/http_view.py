"""Unauthenticated PNG view helpers (HA view wraps these)."""

from __future__ import annotations

import hashlib


def etag_for(png: bytes) -> str:
    digest = hashlib.sha256(png).hexdigest()[:16]
    return f'"{digest}"'


def dashboard_response(
    png: bytes, if_none_match: str | None
) -> tuple[int, dict[str, str], bytes]:
    tag = etag_for(png)
    incoming = (if_none_match or "").strip()
    if incoming and incoming == tag:
        return 304, {"ETag": tag}, b""
    return 200, {"Content-Type": "image/png", "ETag": tag}, png
