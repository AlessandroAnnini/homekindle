"""Build dashboard fixtures from recorded or live feeds."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from .feeds import (
    ROME,
    HaState,
    LastGoodStore,
    events_from_ics,
    footer_labels,
    ical_url_configured,
    weather_from_open_meteo,
    window,
    zone,
)
from .fixtures import DEFAULT_FIXTURES, DashboardFixtures
from .layout import packaged_layout_path
from .options import (
    CONF_ICAL_URL,
    CONF_KINDLE_MODEL,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_REFRESH_MINUTES,
    CONF_TIMEZONE,
    CONF_WEATHER_MODEL,
    DEFAULT_REFRESH_MINUTES,
    DEFAULT_TIMEZONE,
    KINDLE_TOUCH,
    WEATHER_ICON_2I,
    apply_home_location,
    build_open_meteo_url,
    canvas_for,
    fetch_text,
    refresh_interval,
)
from .render import render_png

STORE = LastGoodStore()
CURRENT_OPTIONS: dict | None = None
_CACHE: tuple[float, tuple, DashboardFixtures] | None = None


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
    as_of = (now or datetime.now(ROME)).astimezone(ROME).date()
    return DashboardFixtures(
        weather=weather,
        events=events,
        updated=datetime.now(ROME).strftime("%H:%M"),
        workday=True,
        exceptions=(),
        as_of=as_of,
    )


def _footer(states: tuple[HaState, ...], fallback_workday: bool) -> tuple[bool, tuple[str, ...]]:
    labels = footer_labels(states)
    workday = any(label.lower() == "workday" for label in labels)
    exceptions = tuple(label for label in labels if label.lower() != "workday")
    if not states:
        return fallback_workday, exceptions
    return workday, exceptions


def fixtures_from_live(
    options: dict,
    now: datetime | None = None,
    states: tuple[HaState, ...] = (),
) -> DashboardFixtures:
    global _CACHE
    merged = apply_home_location(options, None)
    tz_name = str(merged.get(CONF_TIMEZONE) or DEFAULT_TIMEZONE)
    ical = str(merged.get(CONF_ICAL_URL) or "").strip() or (ical_url_configured() or "")
    minutes = int(merged.get(CONF_REFRESH_MINUTES) or DEFAULT_REFRESH_MINUTES)
    key = (
        merged.get(CONF_LATITUDE),
        merged.get(CONF_LONGITUDE),
        merged.get(CONF_WEATHER_MODEL),
        tz_name,
        hash(ical),
    )
    stamp = time.monotonic()
    if (
        _CACHE
        and _CACHE[1] == key
        and stamp - _CACHE[0] < refresh_interval(minutes).total_seconds()
    ):
        cached = _CACHE[2]
        workday, exceptions = _footer(states, cached.workday)
        return DashboardFixtures(
            weather=cached.weather,
            events=cached.events,
            updated=cached.updated,
            workday=workday,
            exceptions=exceptions,
            as_of=cached.as_of,
        )

    url = build_open_meteo_url(
        float(merged[CONF_LATITUDE]),
        float(merged[CONF_LONGITUDE]),
        str(merged.get(CONF_WEATHER_MODEL) or WEATHER_ICON_2I),
        timezone=tz_name,
    )
    weather = weather_from_open_meteo(json.loads(fetch_text(url)))
    start, end = window(now, timezone=tz_name)
    events = events_from_ics(fetch_text(ical), start, end) if ical else ()
    tz = zone(tz_name)
    as_of = (now or datetime.now(tz)).astimezone(tz).date()
    workday, exceptions = _footer(states, True)
    fixtures = DashboardFixtures(
        weather=weather,
        events=events,
        updated=datetime.now(tz).strftime("%H:%M"),
        workday=workday,
        exceptions=exceptions,
        as_of=as_of,
    )
    _CACHE = (stamp, key, fixtures)
    return fixtures


def render_or_last_good(
    options: dict | None = None,
    states: tuple[HaState, ...] = (),
) -> bytes:
    layout = packaged_layout_path()
    chosen = options if options is not None else CURRENT_OPTIONS
    try:
        if chosen:
            fixtures = fixtures_from_live(chosen, states=states)
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
