"""Unit tests for brief acceptance criteria AC1–AC5."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from custom_components.homekindle.const import EMPTY_DAY, PNG_HEIGHT, PNG_WIDTH
from custom_components.homekindle.fixtures import (
    DEFAULT_FIXTURES,
    DashboardFixtures,
    EventFixture,
)
from custom_components.homekindle.http_view import dashboard_response, etag_for
from custom_components.homekindle.layout import load_kindle_yaml
from custom_components.homekindle.render import render_png
from PIL import Image

STUDIO = Path(__file__).resolve().parents[2]
LAYOUT = STUDIO / "gf-program" / "dashboards" / "kindle.yaml"
APP = Path(__file__).resolve().parents[1]


def test_ac1_png_is_600x800_grayscale() -> None:
    png = render_png(DEFAULT_FIXTURES, LAYOUT)
    image = Image.open(BytesIO(png))
    assert image.size == (PNG_WIDTH, PNG_HEIGHT)
    assert image.mode == "L"


def test_ac2_etag_repeat_is_304() -> None:
    png = render_png(DEFAULT_FIXTURES, LAYOUT)
    status, headers, _body = dashboard_response(png, None)
    assert status == 200
    tag = headers.get("ETag") or etag_for(png)
    status2, _, body2 = dashboard_response(png, tag)
    assert status2 == 304
    assert body2 == b""


def test_ac3_empty_tomorrow_says_nothing_booked() -> None:
    fixtures = DashboardFixtures(
        weather=DEFAULT_FIXTURES.weather,
        events=(EventFixture("today", "09:00", "Stand-up"),),
        updated="22:45",
        workday=True,
        exceptions=(),
        todos=(),
    )
    png = render_png(fixtures, LAYOUT)
    image = Image.open(BytesIO(png))
    from custom_components.homekindle.render import last_text_blobs

    blobs = " ".join(last_text_blobs()).lower()
    assert EMPTY_DAY in blobs
    assert image.mode == "L"


def test_ac4_uses_lovelace_sections_yaml() -> None:
    data = load_kindle_yaml(LAYOUT)
    view = data["views"][0]
    assert view["type"] == "sections"
    assert view["max_columns"] == 2
    assert len(view["sections"]) == 3


def test_ac5_app_tree_has_no_secrets() -> None:
    forbidden = ("secret.google.com", "calendar.google.com/calendar/ical", "eyJhbGci")
    hits: list[str] = []
    for path in APP.rglob("*"):
        if path.suffix in {".pyc"} or {".git", ".venv", "tests"} & set(path.parts):
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden:
            if token in text:
                hits.append(f"{path}:{token}")
    assert hits == []
