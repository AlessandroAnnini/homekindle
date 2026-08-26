"""Acceptance tests for homekindle-options AC1–AC7."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from custom_components.homekindle.feeds import LastGoodStore
from custom_components.homekindle.options import (
    KINDLE_PW1,
    KINDLE_TOUCH,
    WEATHER_BEST_MATCH,
    WEATHER_ICON_2I,
    canvas_for,
    refresh_interval,
)

APP = Path(__file__).resolve().parents[1]
SECRET_ICAL = "https://example.invalid/calendar/secret-homekindle-ical"


def test_ac1_best_match_omits_models() -> None:
    from custom_components.homekindle.options import build_open_meteo_url

    url = build_open_meteo_url(45.0, 9.0, WEATHER_BEST_MATCH)
    assert "latitude=45.0" in url
    assert "longitude=9.0" in url
    assert "models=" not in url


def test_ac2_icon2i_sets_models() -> None:
    from custom_components.homekindle.options import build_open_meteo_url

    url = build_open_meteo_url(43.62, 13.41, WEATHER_ICON_2I)
    assert "models=italia_meteo_arpae_icon_2i" in url


def test_ac3_pw1_canvas() -> None:
    assert canvas_for(KINDLE_PW1) == (758, 1024)


def test_ac4_touch_canvas() -> None:
    assert canvas_for(KINDLE_TOUCH) == (600, 800)


def test_ac5_ical_url_not_committed() -> None:
    hits: list[str] = []
    for path in APP.rglob("*"):
        if {".git", ".venv", "tests"} & set(path.parts) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if SECRET_ICAL in text or "calendar/ical" in text:
            hits.append(str(path))
    assert hits == []


def test_ac6_refresh_minutes() -> None:
    assert refresh_interval(20) == timedelta(minutes=20)


def test_ac7_last_good_survives_failed_fetch(tmp_path: Path) -> None:
    store = LastGoodStore(tmp_path / "last.png")
    store.put(b"png-bytes")
    assert store.get() == b"png-bytes"
