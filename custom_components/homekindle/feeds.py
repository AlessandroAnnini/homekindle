"""Live weather, calendar, and footer builders. Secrets stay in env / HA."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar
from recurring_ical_events import of

from .fixtures import EventFixture, WeatherFixture

ROME = ZoneInfo("Europe/Rome")
LAT = 43.62
LON = 13.41
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_MODEL = "italia_meteo_arpae_icon_2i"
ICAL_ENV = "HOMEKINDLE_ICAL_URL"
ALWAYS_SHOW = ("binary_sensor.workday_sensor_it_an",)
EXCEPTIONS = (
    ("binary_sensor.refrigerator_door_open_fridge", "fridge door"),
    ("binary_sensor.maltempo_serrande", "storm shutters"),
    ("input_boolean.qualcuno_dorme", "someone sleeping"),
    ("input_boolean.ospiti", "guests"),
    ("input_boolean.vacanza", "holiday"),
)
WMO_TEXT = {0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast"}


@dataclass(frozen=True)
class HaState:
    entity_id: str
    state: str


def window(now: datetime | None = None) -> tuple[datetime, datetime]:
    current = now.astimezone(ROME) if now else datetime.now(ROME)
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


def events_from_ics(ics_text: str, start: datetime, end: datetime) -> tuple[EventFixture, ...]:
    calendar = Calendar.from_ical(ics_text)
    today = start.astimezone(ROME).date()
    out: list[EventFixture] = []
    for event in of(calendar).between(start, end):
        begin = event.start
        if not isinstance(begin, datetime):
            begin = datetime.combine(begin, datetime.min.time(), tzinfo=ROME)
        if begin.tzinfo is None:
            begin = begin.replace(tzinfo=ROME)
        local = begin.astimezone(ROME)
        title = str(event.get("summary") or "")
        all_day = not isinstance(event.start, datetime)
        time_label = "all day" if all_day else local.strftime("%H:%M")
        out.append(EventFixture(day_name(local.date(), today), time_label, title))
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
        self.path = Path(path) if path else Path("/tmp/gf-homekindle-last.png")

    def get(self) -> bytes | None:
        if self.path.is_file():
            return self.path.read_bytes()
        return None

    def put(self, png: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(png)
