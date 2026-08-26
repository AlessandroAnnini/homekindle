"""Acceptance tests for homekindle-options AC1–AC7."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from custom_components.homekindle.feeds import LastGoodStore
from custom_components.homekindle.options import (
    CONF_ICAL_URL,
    CONF_KINDLE_MODEL,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_REFRESH_MINUTES,
    CONF_USE_HA_HOME,
    CONF_WEATHER_MODEL,
    FORM_FIELDS,
    KINDLE_PW1,
    KINDLE_TOUCH,
    WEATHER_BEST_MATCH,
    WEATHER_ICON_2I,
    apply_home_location,
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


def test_form_field_order() -> None:
    assert FORM_FIELDS == (
        CONF_USE_HA_HOME,
        CONF_LATITUDE,
        CONF_LONGITUDE,
        CONF_KINDLE_MODEL,
        CONF_WEATHER_MODEL,
        CONF_ICAL_URL,
        CONF_REFRESH_MINUTES,
    )


def test_use_ha_home_fills_coordinates() -> None:
    merged = apply_home_location({CONF_USE_HA_HOME: True}, (45.0, 9.0))
    assert merged[CONF_LATITUDE] == 45.0
    assert merged[CONF_LONGITUDE] == 9.0


def test_defaults_include_coordinates() -> None:
    from custom_components.homekindle.options import DEFAULTS

    assert DEFAULTS[CONF_LATITUDE] == 43.62
    assert DEFAULTS[CONF_LONGITUDE] == 13.41


def test_fetch_text_rejects_redirect(monkeypatch) -> None:
    from custom_components.homekindle import options as opt

    def fake_open(_request, timeout=20):
        raise ValueError("refusing HTTP redirect to https://evil.example")

    monkeypatch.setattr(
        opt,
        "build_opener",
        lambda *_a, **_k: type("O", (), {"open": staticmethod(fake_open)})(),
    )
    try:
        opt.fetch_text("https://example.invalid/cal")
    except ValueError as exc:
        assert "redirect" in str(exc)
    else:
        raise AssertionError("expected redirect refusal")


def test_fetch_text_rejects_file_scheme() -> None:
    from custom_components.homekindle.options import fetch_text

    try:
        fetch_text("file:///etc/passwd")
    except ValueError as exc:
        assert "non-http" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_ac7_last_good_survives_failed_fetch(tmp_path: Path) -> None:
    store = LastGoodStore(tmp_path / "last.png")
    store.put(b"png-bytes")
    assert store.get() == b"png-bytes"
