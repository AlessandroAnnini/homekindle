"""Regenerate button. Helpers stay importable without Home Assistant."""

from __future__ import annotations

from .const import DOMAIN
from .image import dashboard_device_info
from .options import CONF_KINDLE_MODEL, KINDLE_TOUCH


def regenerate_unique_id(entry_id: str) -> str:
    return f"{entry_id}_regenerate"


try:
    from homeassistant.components.button import ButtonEntity
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        coordinator = hass.data[DOMAIN]["coordinator"]
        async_add_entities([HomeKindleRegenerateButton(hass, entry, coordinator)])

    class HomeKindleRegenerateButton(ButtonEntity):
        _attr_has_entity_name = True
        _attr_translation_key = "regenerate"

        def __init__(
            self,
            hass: HomeAssistant,
            entry: ConfigEntry,
            coordinator: DataUpdateCoordinator[bytes],
        ) -> None:
            self.coordinator = coordinator
            model = str(
                hass.data[DOMAIN]["options"].get(CONF_KINDLE_MODEL) or KINDLE_TOUCH
            )
            self._attr_unique_id = regenerate_unique_id(entry.entry_id)
            self._attr_device_info = DeviceInfo(
                **dashboard_device_info(entry.entry_id, model)
            )

        async def async_press(self) -> None:
            await self.coordinator.async_request_refresh()

except ImportError:
    pass
