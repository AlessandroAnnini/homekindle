"""Unauthenticated PNG view helpers (HA view wraps these)."""

from __future__ import annotations


def etag_for(png: bytes) -> str:
    raise NotImplementedError


def dashboard_response(png: bytes, if_none_match: str | None) -> tuple[int, dict[str, str], bytes]:
    raise NotImplementedError
