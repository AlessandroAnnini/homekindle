"""Extra renderer / layout coverage beyond AC IDs."""

from __future__ import annotations

from custom_components.homekindle.fixtures import DEFAULT_FIXTURES
from custom_components.homekindle.layout import load_kindle_yaml, packaged_layout_path
from custom_components.homekindle.render import last_text_blobs, render_png


def test_packaged_yaml_has_footer_span() -> None:
    data = load_kindle_yaml(packaged_layout_path())
    footer = data["views"][0]["sections"][2]
    assert footer.get("column_span") == 2


def test_footer_includes_updated_and_exception() -> None:
    render_png(DEFAULT_FIXTURES, packaged_layout_path())
    blob = " ".join(last_text_blobs()).lower()
    assert "updated 22:45" in blob
    assert "fridge door" in blob
