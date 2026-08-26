"""Live weather, calendar, and footer builders. Secrets stay in env / HA."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

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
