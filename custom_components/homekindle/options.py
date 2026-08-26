"""User-facing HomeKindle options. No secrets in this module."""

from __future__ import annotations

from datetime import timedelta
from urllib.parse import urlencode

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

CONF_USE_HA_HOME = "use_ha_home"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_KINDLE_MODEL = "kindle_model"
CONF_WEATHER_MODEL = "weather_model"
CONF_ICAL_URL = "ical_url"
CONF_REFRESH_MINUTES = "refresh_minutes"

KINDLE_TOUCH = "touch"
KINDLE_PW1 = "pw1"
CANVASES: dict[str, tuple[int, int]] = {
    KINDLE_TOUCH: (600, 800),
    KINDLE_PW1: (758, 1024),
}

WEATHER_BEST_MATCH = "best_match"
WEATHER_ICON_2I = "italia_meteo_arpae_icon_2i"
WEATHER_MODELS = (
    WEATHER_BEST_MATCH,
    WEATHER_ICON_2I,
    "icon_seamless",
    "icon_eu",
    "ecmwf_ifs025",
    "gfs_seamless",
)

REFRESH_MIN = 5
REFRESH_MAX = 120
DEFAULT_REFRESH_MINUTES = 15

DEFAULTS: dict[str, object] = {
    CONF_USE_HA_HOME: True,
    CONF_KINDLE_MODEL: KINDLE_TOUCH,
    CONF_WEATHER_MODEL: WEATHER_ICON_2I,
    CONF_ICAL_URL: "",
    CONF_REFRESH_MINUTES: DEFAULT_REFRESH_MINUTES,
}


def canvas_for(model: str) -> tuple[int, int]:
    return CANVASES.get(model, CANVASES[KINDLE_TOUCH])


def refresh_interval(minutes: int) -> timedelta:
    clamped = max(REFRESH_MIN, min(REFRESH_MAX, int(minutes)))
    return timedelta(minutes=clamped)


def build_open_meteo_url(
    latitude: float,
    longitude: float,
    weather_model: str,
    timezone: str = "Europe/Rome",
) -> str:
    query: dict[str, object] = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "current": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
    }
    if weather_model and weather_model != WEATHER_BEST_MATCH:
        query["models"] = weather_model
    return f"{OPEN_METEO_URL}?{urlencode(query)}"


def fetch_text(url: str, timeout: float = 20) -> str:
    from urllib.request import Request, urlopen

    request = Request(url, headers={"User-Agent": "HomeKindle"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")
