"""Build dashboard fixtures from recorded or live feeds."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .feeds import (
    ROME,
    LastGoodStore,
    events_from_ics,
    footer_labels,
    weather_from_open_meteo,
    window,
)
from .fixtures import DEFAULT_FIXTURES, DashboardFixtures
from .layout import packaged_layout_path
from .render import render_png

STORE = LastGoodStore()


def recorded_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def fixtures_from_recorded(now: datetime | None = None) -> DashboardFixtures:
    folder = recorded_dir()
    meteo = folder / "open_meteo.json"
    ics = folder / "sample.ics"
    if not meteo.is_file() or not ics.is_file():
        return DEFAULT_FIXTURES
    weather = weather_from_open_meteo(json.loads(meteo.read_text(encoding="utf-8")))
    start, end = window(now)
    events = events_from_ics(ics.read_text(encoding="utf-8"), start, end)
    labels = footer_labels(())
    return DashboardFixtures(
        weather=weather,
        events=events,
        updated=datetime.now(ROME).strftime("%H:%M"),
        workday=True,
        exceptions=labels,
        todos=(),
    )


def render_or_last_good() -> bytes:
    layout = packaged_layout_path()
    try:
        png = render_png(fixtures_from_recorded(), layout)
    except Exception:
        cached = STORE.get()
        if cached:
            return cached
        raise
    STORE.put(png)
    return png
