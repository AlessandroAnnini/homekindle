"""User-facing HomeKindle options. No secrets in this module."""

from __future__ import annotations

from datetime import timedelta

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
