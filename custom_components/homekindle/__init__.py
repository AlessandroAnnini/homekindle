"""HomeKindle custom integration."""

from __future__ import annotations

from typing import Any

from .const import DOMAIN

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType
except ImportError:  # local unit tests without HA installed
    HomeAssistant = Any  # type: ignore[misc,assignment]
    ConfigType = dict  # type: ignore[misc,assignment]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    try:
        from .ha_view import HomeKindleDashboardView

        hass.http.register_view(HomeKindleDashboardView())
    except (ImportError, AttributeError):
        pass
    return True


async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    return True
