"""HomeKindle config and options flow. Schema filled in a later step."""

from __future__ import annotations

from typing import Any

from .const import DOMAIN
from .options import DEFAULTS

try:
    from homeassistant import config_entries
    from homeassistant.core import callback
except ImportError:  # local unit tests without HA
    config_entries = None  # type: ignore[assignment]


if config_entries is not None:

    class HomeKindleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
        VERSION = 1

        async def async_step_user(
            self, user_input: dict[str, Any] | None = None
        ) -> config_entries.ConfigFlowResult:
            if user_input is not None:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="HomeKindle", data=user_input)
            return self.async_show_form(step_id="user")

        @staticmethod
        @callback
        def async_get_options_flow(
            config_entry: config_entries.ConfigEntry,
        ) -> config_entries.OptionsFlow:
            return HomeKindleOptionsFlow()

    class HomeKindleOptionsFlow(config_entries.OptionsFlowWithReload):
        async def async_step_init(
            self, user_input: dict[str, Any] | None = None
        ) -> config_entries.ConfigFlowResult:
            if user_input is not None:
                return self.async_create_entry(title="", data=user_input)
            return self.async_show_form(
                step_id="init",
                data_schema=None,
                description_placeholders={"defaults": str(DEFAULTS)},
            )
