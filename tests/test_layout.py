"""Extra renderer / layout coverage beyond AC IDs."""

from __future__ import annotations

from io import BytesIO

from custom_components.homekindle.fixtures import (
    DEFAULT_FIXTURES,
    DashboardFixtures,
    EventFixture,
)
from custom_components.homekindle.layout import load_kindle_yaml, packaged_layout_path
from custom_components.homekindle.render import (
    BOX_EVENT,
    DOT_R,
    EVENT_STEP,
    INK,
    PAD,
    PAPER,
    Y_CONDITION,
    Y_DATE,
    Y_EVENTS,
    Y_HEADING,
    Y_ICON,
    B,
    SZ_TITLE,
    _bold_font,
    _ink_mid_from_baseline,
    last_text_blobs,
    last_timeline,
    render_png,
)
from custom_components.homekindle.weather_icons import petroff_name
from PIL import Image


def test_packaged_yaml_has_footer_span() -> None:
    data = load_kindle_yaml(packaged_layout_path())
    footer = data["views"][0]["sections"][2]
    assert footer.get("column_span") == 2
    cards = footer.get("cards") or []
    assert not any(card.get("type") == "todo-list" for card in cards)
    blob = str(data)
    assert "shopping" not in blob
    assert "todo.shopping_list" not in blob


def test_footer_includes_updated_and_exception() -> None:
    render_png(DEFAULT_FIXTURES, packaged_layout_path())
    blob = " ".join(last_text_blobs()).lower()
    assert "updated 22:45" in blob
    assert "fridge door" in blob
    assert "shopping" not in blob


def test_wmo_maps_to_petroff() -> None:
    assert petroff_name(0) == "skc"
    assert petroff_name(1) == "few"
    assert petroff_name(3) == "ovc"
    assert petroff_name(61) == "ra"
    assert petroff_name(95) == "tsra"


def test_event_timeline_line_and_dots() -> None:
    fixtures = DashboardFixtures(
        weather=DEFAULT_FIXTURES.weather,
        events=(
            EventFixture("today", "09:00", "Stand-up"),
            EventFixture("today", "10:30", "Review"),
            EventFixture("today", "14:00", "Library"),
        ),
        updated="22:45",
        workday=True,
        exceptions=(),
    )
    png = render_png(fixtures, packaged_layout_path())
    image = Image.open(BytesIO(png))
    line_x, centers = last_timeline()["today"]
    assert len(centers) == 3
    assert centers[1] - centers[0] == centers[2] - centers[1]
    for cy in centers:
        assert image.getpixel((line_x, cy)) == INK
        assert image.getpixel((line_x - 1, cy)) == INK
        assert image.getpixel((line_x + 1, cy)) == INK
    mid = (centers[0] + centers[1]) // 2
    assert image.getpixel((line_x, mid)) == INK
    assert image.getpixel((line_x - 6, mid)) == PAPER
    assert centers[1] - centers[0] == EVENT_STEP
    assert "tomorrow" not in last_timeline()


def test_timeline_inset_matches_across_columns() -> None:
    fixtures = DashboardFixtures(
        weather=DEFAULT_FIXTURES.weather,
        events=(
            EventFixture("today", "09:00", "Stand-up"),
            EventFixture("today", "14:00", "Library"),
            EventFixture("tomorrow", "10:30", "Review"),
            EventFixture("tomorrow", "18:00", "Dinner"),
        ),
        updated="22:45",
        workday=True,
        exceptions=(),
    )
    render_png(fixtures, packaged_layout_path())
    today_x, _ = last_timeline()["today"]
    tomorrow_x, _ = last_timeline()["tomorrow"]
    assert today_x - 0 == tomorrow_x - 300
    assert today_x > PAD


def test_all_day_fits_and_sorts_first() -> None:
    fixtures = DashboardFixtures(
        weather=DEFAULT_FIXTURES.weather,
        events=(
            EventFixture("today", "09:00", "Stand-up"),
            EventFixture("today", "all day", "Marta's birthday"),
            EventFixture("tomorrow", "all day", "Leo's birthday"),
            EventFixture("tomorrow", "10:00", "Library"),
        ),
        updated="22:45",
        workday=True,
        exceptions=(),
    )
    png = render_png(fixtures, packaged_layout_path())
    image = Image.open(BytesIO(png))
    blob = " ".join(last_text_blobs())
    assert blob.index("Marta's birthday") < blob.index("Stand-up")
    assert "all day" in blob
    line_x, centers = last_timeline()["today"]
    assert len(centers) == 2
    # "all day" sits left of the line and stays on the canvas
    assert 0 <= line_x - PAD < 90
    assert image.getpixel((line_x, centers[0])) == PAPER
    assert image.getpixel((line_x, centers[0] - DOT_R)) == INK
    mid = (centers[0] + centers[1]) // 2
    assert image.getpixel((line_x, mid)) == INK
    assert image.getpixel((line_x, centers[1])) == INK


def test_vertical_rhythm_uses_eight_pt_spacing() -> None:
    assert PAD % B == 0
    for y in (Y_HEADING, Y_DATE, Y_ICON, Y_CONDITION, Y_EVENTS, EVENT_STEP):
        assert y % B == 0
    fixtures = DashboardFixtures(
        weather=DEFAULT_FIXTURES.weather,
        events=(
            EventFixture("today", "all day", "Marta's birthday"),
            EventFixture("today", "09:00", "Stand-up"),
            EventFixture("today", "14:00", "Library"),
        ),
        updated="22:45",
        workday=True,
        exceptions=(),
    )
    render_png(fixtures, packaged_layout_path())
    _line_x, centers = last_timeline()["today"]
    assert centers
    mid = BOX_EVENT - B + _ink_mid_from_baseline(_bold_font(SZ_TITLE))
    assert all(cy == Y_EVENTS + i * EVENT_STEP + mid for i, cy in enumerate(centers))
    assert centers[1] - centers[0] == EVENT_STEP
