"""Pillow renderer for the Kindle PNG."""

from __future__ import annotations

from pathlib import Path

from .fixtures import DashboardFixtures


def render_png(fixtures: DashboardFixtures, layout_path: Path) -> bytes:
    raise NotImplementedError


def last_text_blobs() -> tuple[str, ...]:
    raise NotImplementedError
