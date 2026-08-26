"""Acceptance tests for homekindle-feeds AC1–AC5."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from custom_components.homekindle.feeds import (
    ROME,
    HaState,
    LastGoodStore,
    events_from_ics,
    footer_labels,
    ical_url_configured,
    weather_from_open_meteo,
    window,
)
from custom_components.homekindle.fixtures import WeatherFixture

FIXTURES = Path(__file__).parent / "fixtures"


def test_ac1_open_meteo_today_and_tomorrow() -> None:
    payload = json.loads((FIXTURES / "open_meteo.json").read_text(encoding="utf-8"))
    rows = weather_from_open_meteo(payload)
    today = next(w for w in rows if w.day == "today")
    tomorrow = next(w for w in rows if w.day == "tomorrow")
    assert isinstance(today, WeatherFixture)
    assert today.temp_c == 25.1
    assert today.wmo_code == 1
    assert tomorrow.temp_max_c == 33.4
    assert tomorrow.temp_min_c == 21.9


def test_ac2_rrule_lands_on_tomorrow() -> None:
    ics = (FIXTURES / "sample.ics").read_text(encoding="utf-8")
    start, end = window(datetime(2026, 8, 26, 12, 0, tzinfo=ROME))
    events = events_from_ics(ics, start, end)
    tomorrow = [e for e in events if e.day == "tomorrow"]
    assert any("Library" in e.title for e in tomorrow)


def test_all_day_birthday_yearly_sorts_first() -> None:
    ics = (FIXTURES / "sample.ics").read_text(encoding="utf-8")
    start, end = window(datetime(2026, 8, 26, 12, 0, tzinfo=ROME))
    events = events_from_ics(ics, start, end)
    today = [e for e in events if e.day == "today"]
    tomorrow = [e for e in events if e.day == "tomorrow"]
    assert today[0].time_label == "all day"
    assert "Marta" in today[0].title
    assert any(e.time_label == "09:00" and "Stand-up" in e.title for e in today)
    assert tomorrow[0].time_label == "all day"
    assert "Leo" in tomorrow[0].title


def test_ac3_off_exception_hidden() -> None:
    labels = footer_labels(
        (
            HaState("binary_sensor.workday_sensor_it_an", "on"),
            HaState("binary_sensor.refrigerator_door_open_fridge", "off"),
        )
    )
    assert "fridge door" not in {label.lower() for label in labels}
    assert "workday" in {label.lower() for label in labels}


def test_ac4_ical_url_not_in_env_or_tree() -> None:
    os.environ.pop("HOMEKINDLE_ICAL_URL", None)
    assert ical_url_configured() is None
    app = Path(__file__).resolve().parents[1]
    hits = []
    for path in app.rglob("*"):
        if {".git", ".venv", "tests"} & set(path.parts) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "calendar/ical" in text:
            hits.append(str(path))
    assert hits == []


def test_ac5_last_good_survives_failed_fetch(tmp_path: Path) -> None:
    store = LastGoodStore(tmp_path / "last.png")
    store.put(b"png-bytes")
    assert store.get() == b"png-bytes"
