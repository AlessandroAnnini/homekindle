"""Home Assistant HTTP view. Imported only when HA is installed."""

from __future__ import annotations

from homeassistant.components.http import HomeAssistantView

from .dashboard import render_or_last_good
from .http_view import dashboard_response


class HomeKindleDashboardView(HomeAssistantView):
    url = "/api/homekindle/dashboard.png"
    name = "api:homekindle:dashboard"
    requires_auth = False

    async def get(self, request):
        hass = request.app["hass"]
        png = await hass.async_add_executor_job(render_or_last_good)
        status, headers, body = dashboard_response(
            png, request.headers.get("If-None-Match")
        )
        from aiohttp import web

        return web.Response(status=status, headers=headers, body=body)
