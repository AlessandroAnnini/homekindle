"""Last-good PNG when render fails."""

from __future__ import annotations

from custom_components.homekindle import dashboard
from custom_components.homekindle.feeds import LastGoodStore


def test_last_good_used_when_render_raises(tmp_path, monkeypatch) -> None:
    store = LastGoodStore(tmp_path / "last.png")
    store.put(b"cached-png")
    monkeypatch.setattr(dashboard, "STORE", store)

    def boom() -> bytes:
        raise RuntimeError("fetch failed")

    monkeypatch.setattr(dashboard, "render_png", lambda *_a, **_k: boom())
    monkeypatch.setattr(dashboard, "fixtures_from_recorded", boom)
    assert dashboard.render_or_last_good() == b"cached-png"
