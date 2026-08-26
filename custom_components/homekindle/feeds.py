"""Live weather, calendar, and footer builders. Secrets stay in env / HA."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar
from recurring_ical_events import of

from .fixtures import EventFixture, WeatherFixture

ROME = ZoneInfo("Europe/Rome")
ICAL_ENV = "HOMEKINDLE_ICAL_URL"
ALWAYS_SHOW = ("binary_sensor.workday_sensor_it_an",)
EXCEPTIONS = (
    ("binary_sensor.refrigerator_door_open_fridge", "fridge door"),
    ("binary_sensor.maltempo_serrande", "storm shutters"),
    ("input_boolean.qualcuno_dorme", "someone sleeping"),
    ("input_boolean.ospiti", "guests"),
    ("input_boolean.vacanza", "holiday"),
)
WMO_TEXT = {
    0: "clear",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "rime fog",
    51: "light drizzle",
    53: "drizzle",
    55: "dense drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    80: "showers",
    81: "showers",
    82: "heavy showers",
    95: "thunderstorm",
    96: "thunderstorm",
    99: "thunderstorm",
}


@dataclass(frozen=True)
class HaState:
    entity_id: str
    state: str


def zone(name: str | None = None) -> ZoneInfo:
    try:
        return ZoneInfo(name) if name else ROME
    except (KeyError, ValueError, OSError):
        return ROME


def window(
    now: datetime | None = None, timezone: str | None = None
) -> tuple[datetime, datetime]:
    tz = zone(timezone)
    current = now.astimezone(tz) if now else datetime.now(tz)
    start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=2)
    return start, end


def day_name(when: date, today: date) -> str:
    if when == today:
        return "today"
    if when == today + timedelta(days=1):
        return "tomorrow"
    return when.isoformat()


def weather_from_open_meteo(payload: dict) -> tuple[WeatherFixture, ...]:
    current = payload["current"]
    daily = payload["daily"]
    today = datetime.fromisoformat(current["time"]).date()
    rows = [
        WeatherFixture(
            "today",
            WMO_TEXT.get(int(current["weather_code"]), "weather"),
            int(current["weather_code"]),
            temp_c=float(current["temperature_2m"]),
        )
    ]
    for index, day in enumerate(daily["time"]):
        parsed = date.fromisoformat(day)
        if parsed == today + timedelta(days=1):
            rows.append(
                WeatherFixture(
                    "tomorrow",
                    WMO_TEXT.get(int(daily["weather_code"][index]), "weather"),
                    int(daily["weather_code"][index]),
                    temp_min_c=float(daily["temperature_2m_min"][index]),
                    temp_max_c=float(daily["temperature_2m_max"][index]),
                )
            )
    return tuple(rows)


def _as_date(value: date | datetime) -> date:
    return value if not isinstance(value, datetime) else value.date()


def events_from_ics(ics_text: str, start: datetime, end: datetime) -> tuple[EventFixture, ...]:
    calendar = Calendar.from_ical(ics_text)
    today = start.astimezone(ROME).date()
    out: list[EventFixture] = []
    for event in of(calendar).between(start, end):
        title = str(event.get("summary") or "")
        raw_start = event.start
        if not isinstance(raw_start, datetime):
            start_day = _as_date(raw_start)
            raw_end = getattr(event, "end", None)
            end_day = _as_date(raw_end) if raw_end is not None else start_day + timedelta(days=1)
            if end_day <= start_day:
                end_day = start_day + timedelta(days=1)
            cursor = start_day
            while cursor < end_day:
                name = day_name(cursor, today)
                if name in {"today", "tomorrow"}:
                    out.append(EventFixture(name, "all day", title))
                cursor += timedelta(days=1)
            continue
        begin = raw_start
        if begin.tzinfo is None:
            begin = begin.replace(tzinfo=ROME)
        local = begin.astimezone(ROME)
        out.append(EventFixture(day_name(local.date(), today), local.strftime("%H:%M"), title))
    out.sort(key=lambda row: (0 if row.time_label == "all day" else 1, row.time_label, row.title))
    return tuple(out)


def footer_labels(states: tuple[HaState, ...]) -> tuple[str, ...]:
    by_id = {row.entity_id: row.state for row in states}
    labels: list[str] = []
    if ALWAYS_SHOW[0] in by_id:
        labels.append("workday")
    for entity_id, name in EXCEPTIONS:
        if by_id.get(entity_id) == "on":
            labels.append(name)
    return tuple(labels)


def ical_url_configured() -> str | None:
    value = os.environ.get(ICAL_ENV, "").strip()
    return value or None


class LastGoodStore:
    def __init__(self, path: object | None = None) -> None:
        self.path = Path(path) if path else Path(tempfile.gettempdir()) / "gf-homekindle-last.png"

    def get(self) -> bytes | None:
        if self.path.is_file():
            return self.path.read_bytes()
        return None

    def put(self, png: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(png)
