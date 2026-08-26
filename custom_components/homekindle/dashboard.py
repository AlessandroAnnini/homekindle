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
from .options import (
    CONF_ICAL_URL,
    CONF_KINDLE_MODEL,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_WEATHER_MODEL,
    KINDLE_TOUCH,
    WEATHER_ICON_2I,
    build_open_meteo_url,
    canvas_for,
    fetch_text,
)
from .render import render_png

STORE = LastGoodStore()
CURRENT_OPTIONS: dict | None = None


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


def fixtures_from_live(options: dict, now: datetime | None = None) -> DashboardFixtures:
    url = build_open_meteo_url(
        float(options[CONF_LATITUDE]),
        float(options[CONF_LONGITUDE]),
        str(options.get(CONF_WEATHER_MODEL) or WEATHER_ICON_2I),
    )
    weather = weather_from_open_meteo(json.loads(fetch_text(url)))
    start, end = window(now)
    ical = str(options.get(CONF_ICAL_URL) or "").strip()
    events = events_from_ics(fetch_text(ical), start, end) if ical else ()
    labels = footer_labels(())
    return DashboardFixtures(
        weather=weather,
        events=events,
        updated=datetime.now(ROME).strftime("%H:%M"),
        workday=True,
        exceptions=labels,
        todos=(),
    )


def render_or_last_good(options: dict | None = None) -> bytes:
    layout = packaged_layout_path()
    chosen = options if options is not None else CURRENT_OPTIONS
    try:
        if chosen:
            fixtures = fixtures_from_live(chosen)
            size = canvas_for(str(chosen.get(CONF_KINDLE_MODEL) or KINDLE_TOUCH))
            png = render_png(fixtures, layout, size=size)
        else:
            png = render_png(fixtures_from_recorded(), layout)
    except Exception:
        cached = STORE.get()
        if cached:
            return cached
        raise
    STORE.put(png)
    return png
