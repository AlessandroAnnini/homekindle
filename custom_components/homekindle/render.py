"""Pillow renderer for the Kindle PNG."""

from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .const import EMPTY_DAY, PNG_HEIGHT, PNG_WIDTH
from .feeds import ROME
from .fixtures import DashboardFixtures, EventFixture, WeatherFixture
from .layout import load_kindle_yaml
from .weather_icons import petroff_png

# 16-level e-ink stops (n * 17). Mid grays dither; keep text and rules dark.
INK = 0
GRAY = 4 * 17
RULE = 6 * 17
PAPER = 255
_FONTS = Path(__file__).resolve().parent / "fonts"
_TEXT: list[str] = []
_TIMELINE: dict[str, tuple[int, tuple[int, ...]]] = {}

# 8pt spacing grid (600 and 800 divide by 8). Boxes and gaps are the rhythm;
# glyphs sit inset from the box, not locked to a typographic baseline.
# Type scale 12 / 16 / 32. Paragraph 16, after heading 16, before section 32.
B = 8
PAD = 3 * B
BOX_META = 3 * B
BOX_WEATHER = 6 * B
BOX_EVENT = 4 * B
GAP_AFTER = 2 * B
GAP_BEFORE = 4 * B
Y_HEADING = PAD
Y_DATE = Y_HEADING + BOX_META
Y_ICON = Y_DATE + BOX_META + GAP_BEFORE
ICON = BOX_WEATHER
ICON_TEMP_GAP = 2 * B
Y_CONDITION = Y_ICON + ICON + GAP_AFTER
Y_EVENTS = Y_CONDITION + BOX_META + GAP_BEFORE
EVENT_STEP = BOX_EVENT
GUTTER = B
DOT_R = 2
FOOTER = 6 * B
LABEL_TRACK = 1
SZ_LABEL = 12
SZ_DATE = 12
SZ_TEMP = 32
SZ_COND = 12
SZ_TIME = 16
SZ_TITLE = 16
SZ_FOOT = 12


def last_text_blobs() -> tuple[str, ...]:
    return tuple(_TEXT)


def last_timeline() -> dict[str, tuple[int, tuple[int, ...]]]:
    return dict(_TIMELINE)


def _font(name: str, size: int) -> ImageFont.ImageFont:
    path = _FONTS / name
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        try:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
            )
        except OSError:
            return ImageFont.load_default()


def _label_font(size: int) -> ImageFont.ImageFont:
    return _font("IBMPlexSans-Regular.ttf", size)


def _body_font(size: int) -> ImageFont.ImageFont:
    return _font("AtkinsonHyperlegible-Regular.ttf", size)


def _bold_font(size: int) -> ImageFont.ImageFont:
    return _font("AtkinsonHyperlegible-Bold.ttf", size)


def _fit(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> str:
    if draw.textlength(text, font=font) <= max_w:
        return text
    ellip = "…"
    while text and draw.textlength(text + ellip, font=font) > max_w:
        text = text[:-1]
    return text + ellip if text else ellip


def _weather_for(fixtures: DashboardFixtures, day: str) -> WeatherFixture | None:
    return next((w for w in fixtures.weather if w.day == day), None)


def _event_key(event: EventFixture) -> tuple:
    return (0 if event.time_label == "all day" else 1, event.time_label, event.title)


def _events_for(fixtures: DashboardFixtures, day: str) -> tuple[EventFixture, ...]:
    return tuple(sorted((e for e in fixtures.events if e.day == day), key=_event_key))


def _temp_label(weather: WeatherFixture) -> str:
    if weather.temp_c is not None:
        return f"{round(weather.temp_c)}°"
    if weather.temp_max_c is not None and weather.temp_min_c is not None:
        return f"{round(weather.temp_max_c)}°/{round(weather.temp_min_c)}°"
    return "—"


def _px(value: int, scale: float) -> int:
    return round(value * scale)


def height_limit(scale: float) -> int:
    return int(PNG_HEIGHT * scale) - _px(FOOTER + GAP_AFTER, scale)


def _box_base(box_top: int, box_h: int, inset: int) -> int:
    return box_top + box_h - inset


def _time_col(draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont) -> int:
    return max(round(draw.textlength(sample, font=font)) for sample in ("00:00", "all day"))


def _ink_mid_from_baseline(font: ImageFont.ImageFont) -> int:
    """Offset from the baseline to the optical middle of a cap-height Latin line."""
    try:
        _left, top, _right, bottom = font.getbbox("H0", anchor="ls")
    except TypeError:
        return 0
    return (top + bottom) // 2


def _draw_tracked(
    draw: ImageDraw.ImageDraw,
    x: int,
    baseline: int,
    text: str,
    fill: int,
    font: ImageFont.ImageFont,
    tracking: int,
) -> None:
    cursor = x
    for char in text:
        draw.text((cursor, baseline), char, fill=fill, font=font, anchor="ls")
        cursor += round(draw.textlength(char, font=font)) + tracking


def _column(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    fixtures: DashboardFixtures,
    day: str,
    heading: str,
    x: int,
    col_w: int,
    max_events: int,
    scale: float,
    as_of,
) -> None:
    pad = _px(PAD, scale)
    gutter = _px(GUTTER, scale)
    inset = _px(B, scale)
    meta_h = _px(BOX_META, scale)
    weather_h = _px(BOX_WEATHER, scale)
    event_h = _px(BOX_EVENT, scale)
    label = heading.upper()
    heading_font = _label_font(max(11, _px(SZ_LABEL, scale)))
    _draw_tracked(
        draw,
        x + pad,
        _box_base(_px(Y_HEADING, scale), meta_h, inset),
        label,
        INK,
        heading_font,
        _px(LABEL_TRACK, scale),
    )
    _TEXT.append(label)
    day_date = as_of if day == "today" else as_of + timedelta(days=1)
    date_s = day_date.strftime("%d %b").upper()
    date_font = _label_font(max(10, _px(SZ_DATE, scale)))
    _draw_tracked(
        draw,
        x + pad,
        _box_base(_px(Y_DATE, scale), meta_h, inset),
        date_s,
        GRAY,
        date_font,
        _px(LABEL_TRACK, scale),
    )
    _TEXT.append(date_s)
    weather = _weather_for(fixtures, day)
    if weather:
        icon_n = _px(ICON, scale)
        icon_y = _px(Y_ICON, scale)
        image.paste(petroff_png(weather.wmo_code, icon_n), (x + pad, icon_y))
        temp = _temp_label(weather)
        temp_font = _bold_font(max(20, _px(SZ_TEMP, scale)))
        draw.text(
            (x + pad + icon_n + _px(ICON_TEMP_GAP, scale), _box_base(icon_y, weather_h, inset)),
            temp,
            fill=INK,
            font=temp_font,
            anchor="ls",
        )
        cond_font = _body_font(max(11, _px(SZ_COND, scale)))
        cond = _fit(draw, weather.condition, cond_font, col_w - pad * 2)
        draw.text(
            (x + pad, _box_base(_px(Y_CONDITION, scale), meta_h, inset)),
            cond,
            fill=GRAY,
            font=cond_font,
            anchor="ls",
        )
        _TEXT.extend([temp, weather.condition])
    events = _events_for(fixtures, day)[:max_events]
    y = _px(Y_EVENTS, scale)
    body = _body_font(max(12, _px(SZ_TITLE, scale)))
    time_font = _body_font(max(12, _px(SZ_TIME, scale)))
    step = _px(EVENT_STEP, scale)
    limit = height_limit(scale)
    if not events:
        draw.text(
            (x + pad, _box_base(y, event_h, inset)),
            EMPTY_DAY,
            fill=GRAY,
            font=body,
            anchor="ls",
        )
        _TEXT.append(EMPTY_DAY)
        return
    time_col = _time_col(draw, time_font)
    line_x = x + pad + time_col + gutter
    title_x = line_x + gutter
    title_max = x + col_w - pad - title_x
    rows: list[tuple[int, EventFixture, str]] = []
    for event in events:
        if y + step > limit:
            break
        title = _fit(draw, event.title, body, title_max)
        rows.append((y, event, title))
        y += step
    text_base = event_h - inset
    mark_mid = _ink_mid_from_baseline(body)
    centers = tuple(row_y + text_base + mark_mid for row_y, _event, _title in rows)
    if len(centers) >= 2:
        draw.line((line_x, centers[0], line_x, centers[-1]), fill=INK, width=1)
    radius = max(DOT_R, _px(DOT_R, scale))
    for cy, (_y, event, _t) in zip(centers, rows):
        box = (line_x - radius, cy - radius, line_x + radius, cy + radius)
        if event.time_label == "all day":
            draw.ellipse(box, fill=PAPER, outline=INK, width=1)
        else:
            draw.ellipse(box, fill=INK)
    time_right = line_x - gutter
    for row_y, event, title in rows:
        draw.text(
            (time_right, row_y + text_base),
            event.time_label,
            fill=GRAY,
            font=time_font,
            anchor="rs",
        )
        draw.text((title_x, row_y + text_base), title, fill=INK, font=body, anchor="ls")
        _TEXT.append(f"{event.time_label}  {event.title}")
    _TIMELINE[day] = (line_x, centers)


def render_png(
    fixtures: DashboardFixtures,
    layout_path: Path,
    size: tuple[int, int] | None = None,
) -> bytes:
    _TEXT.clear()
    _TIMELINE.clear()
    layout = load_kindle_yaml(layout_path)
    view = layout["views"][0]
    sections = view["sections"]
    width, height = size or (PNG_WIDTH, PNG_HEIGHT)
    scale = height / PNG_HEIGHT
    image = Image.new("L", (width, height), PAPER)
    draw = ImageDraw.Draw(image)
    pad = _px(PAD, scale)
    foot_y = height - _px(FOOTER, scale)
    draw.line((width // 2, pad, width // 2, foot_y), fill=RULE, width=1)
    draw.line((pad, foot_y, width - pad, foot_y), fill=RULE, width=1)

    today_max = 6
    tomorrow_max = 6
    for section in sections[:2]:
        for card in section.get("cards") or []:
            extra = card.get("homekindle") or {}
            if extra.get("day") == "today" and "max_events" in extra:
                today_max = int(extra["max_events"])
            if extra.get("day") == "tomorrow" and "max_events" in extra:
                tomorrow_max = int(extra["max_events"])

    as_of = fixtures.as_of or datetime.now(ROME).date()
    col_w = width // 2
    _column(image, draw, fixtures, "today", sections[0].get("title") or "Today", 0, col_w, today_max, scale, as_of)
    _column(
        image,
        draw,
        fixtures,
        "tomorrow",
        sections[1].get("title") or "Tomorrow",
        col_w,
        col_w,
        tomorrow_max,
        scale,
        as_of,
    )

    footer = [f"updated {fixtures.updated}"]
    if fixtures.workday:
        footer.append("workday")
    footer.extend(fixtures.exceptions)
    foot_font = _label_font(max(10, _px(SZ_FOOT, scale)))
    foot = _fit(draw, "  ·  ".join(footer), foot_font, width - pad * 2)
    draw.text(
        (pad, _box_base(foot_y + _px(2 * B, scale), _px(BOX_META, scale), _px(B, scale))),
        foot,
        fill=GRAY,
        font=foot_font,
        anchor="ls",
    )
    _TEXT.append("  ·  ".join(footer))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
