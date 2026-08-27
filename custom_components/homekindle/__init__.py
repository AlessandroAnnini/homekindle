"""HomeKindle custom integration."""

from __future__ import annotations

from typing import Any

from .const import DOMAIN, PLATFORMS

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import config_validation as cv
    from homeassistant.helpers.typing import ConfigType
except ImportError:  # local unit tests without HA installed
    HomeAssistant = Any  # type: ignore[misc,assignment]
    ConfigType = dict  # type: ignore[misc,assignment]

    class cv:  # type: ignore[no-redef]
        @staticmethod
        def empty_config_schema(domain: str) -> dict:
            return {domain: dict}


CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    try:
        from .ha_view import HomeKindleDashboardView, HomeKindleLegacyPngView

        hass.http.register_view(HomeKindleDashboardView())
        hass.http.register_view(HomeKindleLegacyPngView())
    except (ImportError, AttributeError):
        pass
    return True


async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    from . import dashboard
    from .options import CONF_TIMEZONE, apply_home_location

    home = None
    try:
        home = (float(hass.config.latitude), float(hass.config.longitude))
    except (AttributeError, TypeError):
        home = None
    opts = apply_home_location({**entry.data, **entry.options}, home)
    tz = getattr(hass.config, "time_zone", None)
    if tz:
        opts[CONF_TIMEZONE] = tz
    store = hass.data.setdefault(DOMAIN, {})
    store["options"] = opts
    dashboard.CURRENT_OPTIONS = opts
    from .image import async_create_coordinator

    store["coordinator"] = await async_create_coordinator(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: Any) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop("coordinator", None)
    return unloaded
