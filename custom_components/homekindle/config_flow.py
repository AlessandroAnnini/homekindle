"""HomeKindle config and options flow (HA Settings chrome)."""

from __future__ import annotations

from typing import Any

from .const import DOMAIN
from .options import (
    CONF_ICAL_URL,
    CONF_KINDLE_MODEL,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_REFRESH_MINUTES,
    CONF_USE_HA_HOME,
    CONF_WEATHER_MODEL,
    DEFAULT_REFRESH_MINUTES,
    DEFAULTS,
    KINDLE_PW1,
    KINDLE_TOUCH,
    REFRESH_MAX,
    REFRESH_MIN,
    WEATHER_MODELS,
)

try:
    import voluptuous as vol
    from homeassistant import config_entries
    from homeassistant.core import callback
    from homeassistant.helpers.selector import (
        BooleanSelector,
        NumberSelector,
        NumberSelectorConfig,
        SelectSelector,
        SelectSelectorConfig,
        TextSelector,
        TextSelectorConfig,
    )
except ImportError:  # local unit tests without HA
    config_entries = None  # type: ignore[assignment]


def _form_schema(defaults: dict[str, Any]) -> Any:
    return vol.Schema(
        {
            vol.Required(
                CONF_USE_HA_HOME,
                default=defaults.get(CONF_USE_HA_HOME, True),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LATITUDE,
                default=defaults.get(CONF_LATITUDE, 43.62),
            ): NumberSelector(
                NumberSelectorConfig(min=-90, max=90, step=0.01, mode="box")
            ),
            vol.Optional(
                CONF_LONGITUDE,
                default=defaults.get(CONF_LONGITUDE, 13.41),
            ): NumberSelector(
                NumberSelectorConfig(min=-180, max=180, step=0.01, mode="box")
            ),
            vol.Required(
                CONF_KINDLE_MODEL,
                default=defaults.get(CONF_KINDLE_MODEL, KINDLE_TOUCH),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        {"value": KINDLE_TOUCH, "label": "Kindle Touch (600×800)"},
                        {"value": KINDLE_PW1, "label": "Paperwhite 1 (758×1024)"},
                    ]
                )
            ),
            vol.Required(
                CONF_WEATHER_MODEL,
                default=defaults.get(CONF_WEATHER_MODEL, DEFAULTS[CONF_WEATHER_MODEL]),
            ): SelectSelector(
                SelectSelectorConfig(
                    options=[{"value": mid, "label": mid} for mid in WEATHER_MODELS]
                )
            ),
            vol.Optional(
                CONF_ICAL_URL,
                default=defaults.get(CONF_ICAL_URL, ""),
            ): TextSelector(TextSelectorConfig(type="password")),
            vol.Required(
                CONF_REFRESH_MINUTES,
                default=int(defaults.get(CONF_REFRESH_MINUTES, DEFAULT_REFRESH_MINUTES)),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=REFRESH_MIN, max=REFRESH_MAX, step=1, mode="box"
                )
            ),
        }
    )


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
            defaults = {
                **DEFAULTS,
                CONF_LATITUDE: getattr(self.hass.config, "latitude", 43.62),
                CONF_LONGITUDE: getattr(self.hass.config, "longitude", 13.41),
            }
            return self.async_show_form(
                step_id="user", data_schema=_form_schema(defaults)
            )

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
            current = {**self.config_entry.data, **self.config_entry.options}
            return self.async_show_form(
                step_id="init", data_schema=_form_schema(current)
            )
