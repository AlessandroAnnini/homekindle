"""Home Assistant HTTP view. Imported only when HA is installed."""

from __future__ import annotations

from homeassistant.components.http import HomeAssistantView

from .fixtures import DEFAULT_FIXTURES
from .http_view import dashboard_response
from .layout import packaged_layout_path
from .render import render_png


class HomeKindleDashboardView(HomeAssistantView):
    url = "/api/homekindle/dashboard.png"
    name = "api:homekindle:dashboard"
    requires_auth = False

    async def get(self, request):
        hass = request.app["hass"]
        png = await hass.async_add_executor_job(
            render_png, DEFAULT_FIXTURES, packaged_layout_path()
        )
        status, headers, body = dashboard_response(
            png, request.headers.get("If-None-Match")
        )
        from aiohttp import web

        return web.Response(status=status, headers=headers, body=body)
