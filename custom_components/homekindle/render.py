"""Pillow renderer for the Kindle PNG."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .const import EMPTY_DAY, PNG_HEIGHT, PNG_WIDTH
from .fixtures import DashboardFixtures, EventFixture, WeatherFixture
from .layout import load_kindle_yaml

INK = 0
GRAY = 85
MUTED = 170
PAPER = 255
_TEXT: list[str] = []


def last_text_blobs() -> tuple[str, ...]:
    return tuple(_TEXT)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
        )
    except OSError:
        return ImageFont.load_default()


def _weather_for(fixtures: DashboardFixtures, day: str) -> WeatherFixture | None:
    return next((w for w in fixtures.weather if w.day == day), None)


def _events_for(fixtures: DashboardFixtures, day: str) -> tuple[EventFixture, ...]:
    return tuple(e for e in fixtures.events if e.day == day)


def _temp_label(weather: WeatherFixture) -> str:
    if weather.temp_c is not None:
        return f"{round(weather.temp_c)}°"
    if weather.temp_max_c is not None and weather.temp_min_c is not None:
        return f"{round(weather.temp_max_c)}°/{round(weather.temp_min_c)}°"
    return "—"


def _draw_icon(draw: ImageDraw.ImageDraw, x: int, y: int, wmo: int) -> None:
    # Simple Petroff-like marks until SVG assets land.
    if wmo in {0, 1}:
        draw.ellipse((x, y, x + 28, y + 28), outline=INK, width=2)
        for i in range(8):
            draw.point((x + 14 + int(20 * (i % 2)), y + 14), fill=INK)
    else:
        draw.arc((x, y + 8, x + 32, y + 28), 200, 340, fill=INK, width=2)


def _column(
    draw: ImageDraw.ImageDraw,
    fixtures: DashboardFixtures,
    day: str,
    heading: str,
    x: int,
    max_events: int,
) -> None:
    label = heading.upper()
    draw.text((x + 16, 24), label, fill=INK, font=_font(16))
    _TEXT.append(label)
    weather = _weather_for(fixtures, day)
    if weather:
        _draw_icon(draw, x + 16, 64, weather.wmo_code)
        temp = _temp_label(weather)
        draw.text((x + 56, 64), temp, fill=INK, font=_font(36))
        draw.text((x + 16, 116), weather.condition, fill=GRAY, font=_font(16))
        _TEXT.extend([temp, weather.condition])
    events = _events_for(fixtures, day)[:max_events]
    y = 170
    if not events:
        draw.text((x + 16, y), EMPTY_DAY, fill=GRAY, font=_font(16))
        _TEXT.append(EMPTY_DAY)
        return
    for event in events:
        line = f"{event.time_label}  {event.title}"
        draw.text((x + 16, y), line, fill=INK, font=_font(16))
        _TEXT.append(line)
        y += 28


def render_png(fixtures: DashboardFixtures, layout_path: Path) -> bytes:
    _TEXT.clear()
    layout = load_kindle_yaml(layout_path)
    view = layout["views"][0]
    sections = view["sections"]
    image = Image.new("L", (PNG_WIDTH, PNG_HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    draw.line((PNG_WIDTH // 2, 16, PNG_WIDTH // 2, PNG_HEIGHT - 56), fill=MUTED, width=1)
    draw.line((16, PNG_HEIGHT - 52, PNG_WIDTH - 16, PNG_HEIGHT - 52), fill=MUTED, width=1)

    today_max = 6
    tomorrow_max = 6
    for section in sections[:2]:
        for card in section.get("cards") or []:
            extra = card.get("homekindle") or {}
            if extra.get("day") == "today" and "max_events" in extra:
                today_max = int(extra["max_events"])
            if extra.get("day") == "tomorrow" and "max_events" in extra:
                tomorrow_max = int(extra["max_events"])

    _column(draw, fixtures, "today", sections[0].get("title") or "Today", 0, today_max)
    _column(
        draw, fixtures, "tomorrow", sections[1].get("title") or "Tomorrow",
        PNG_WIDTH // 2, tomorrow_max,
    )

    footer = [f"updated {fixtures.updated}"]
    if fixtures.workday:
        footer.append("workday")
    footer.extend(fixtures.exceptions)
    footer.extend(fixtures.todos)
    foot = "  ·  ".join(footer)
    draw.text((16, PNG_HEIGHT - 36), foot, fill=GRAY, font=_font(14))
    _TEXT.append(foot)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
