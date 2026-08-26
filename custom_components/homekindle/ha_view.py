"""Home Assistant HTTP view. Imported only when HA is installed."""

from __future__ import annotations

from homeassistant.components.http import HomeAssistantView

from .dashboard import render_or_last_good
from .feeds import ALWAYS_SHOW, EXCEPTIONS, HaState
from .http_view import dashboard_response


def ha_states(hass) -> tuple[HaState, ...]:
    ids = [ALWAYS_SHOW[0], *(entity_id for entity_id, _name in EXCEPTIONS)]
    rows: list[HaState] = []
    for entity_id in ids:
        state = hass.states.get(entity_id)
        if state is not None:
            rows.append(HaState(entity_id, state.state))
    return tuple(rows)


class HomeKindleDashboardView(HomeAssistantView):
    url = "/api/homekindle/dashboard.png"
    name = "api:homekindle:dashboard"
    requires_auth = False

    async def get(self, request):
        hass = request.app["hass"]
        options = hass.data.get("homekindle", {}).get("options")
        png = await hass.async_add_executor_job(
            render_or_last_good, options, ha_states(hass)
        )
        status, headers, body = dashboard_response(
            png, request.headers.get("If-None-Match")
        )
        from aiohttp import web

        return web.Response(status=status, headers=headers, body=body)
