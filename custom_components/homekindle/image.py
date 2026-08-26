"""Dashboard image entity. Helpers stay importable without Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

from .const import DOMAIN
from .options import (
    CONF_KINDLE_MODEL,
    CONF_REFRESH_MINUTES,
    DEFAULT_REFRESH_MINUTES,
    KINDLE_PW1,
    KINDLE_TOUCH,
    refresh_interval,
)

_LOGGER = logging.getLogger(__name__)


def kindle_model_label(model: str) -> str:
    if model == KINDLE_PW1:
        return "Paperwhite 1"
    return "Kindle Touch"


def dashboard_unique_id(entry_id: str) -> str:
    return f"{entry_id}_dashboard"


def dashboard_device_info(entry_id: str, model: str) -> dict[str, Any]:
    known = model if model in {KINDLE_TOUCH, KINDLE_PW1} else KINDLE_TOUCH
    return {
        "identifiers": {(DOMAIN, entry_id)},
        "name": "HomeKindle",
        "manufacturer": "HomeKindle",
        "model": kindle_model_label(known),
        "model_id": known,
    }


try:
    from homeassistant.components.image import ImageEntity
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, callback
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
    from homeassistant.util import dt as dt_util

    from .dashboard import render_or_last_good
    from .ha_view import ha_states

    async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        options = hass.data[DOMAIN]["options"]
        minutes = int(options.get(CONF_REFRESH_MINUTES) or DEFAULT_REFRESH_MINUTES)

        async def _async_update() -> bytes:
            opts = hass.data[DOMAIN]["options"]
            return await hass.async_add_executor_job(
                render_or_last_good, opts, ha_states(hass)
            )

        coordinator: DataUpdateCoordinator[bytes] = DataUpdateCoordinator(
            hass,
            _LOGGER,
            config_entry=entry,
            name="homekindle",
            update_interval=refresh_interval(minutes),
            update_method=_async_update,
            always_update=False,
        )
        await coordinator.async_config_entry_first_refresh()
        async_add_entities([HomeKindleImage(hass, entry, coordinator)])

    class HomeKindleImage(ImageEntity):
        _attr_has_entity_name = True
        _attr_translation_key = "dashboard"
        _attr_content_type = "image/png"

        def __init__(
            self,
            hass: HomeAssistant,
            entry: ConfigEntry,
            coordinator: DataUpdateCoordinator[bytes],
        ) -> None:
            super().__init__(hass)
            self.coordinator = coordinator
            model = str(
                hass.data[DOMAIN]["options"].get(CONF_KINDLE_MODEL) or KINDLE_TOUCH
            )
            self._attr_unique_id = dashboard_unique_id(entry.entry_id)
            self._attr_device_info = DeviceInfo(
                **dashboard_device_info(entry.entry_id, model)
            )
            if coordinator.data:
                self._attr_image_last_updated = dt_util.utcnow()

        async def async_added_to_hass(self) -> None:
            await super().async_added_to_hass()
            self.async_on_remove(
                self.coordinator.async_add_listener(self._handle_coordinator_update)
            )

        @callback
        def _handle_coordinator_update(self) -> None:
            self._attr_image_last_updated = dt_util.utcnow()
            self.async_write_ha_state()

        async def async_image(self) -> bytes | None:
            return self.coordinator.data

except ImportError:
    pass
