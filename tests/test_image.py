"""Image entity helpers. No Home Assistant import required."""

from custom_components.homekindle.button import regenerate_unique_id
from custom_components.homekindle.const import DOMAIN
from custom_components.homekindle.image import (
    dashboard_device_info,
    dashboard_unique_id,
    kindle_model_label,
)
from custom_components.homekindle.options import KINDLE_PW1, KINDLE_TOUCH


def test_kindle_model_label() -> None:
    assert kindle_model_label(KINDLE_TOUCH) == "Kindle Touch"
    assert kindle_model_label(KINDLE_PW1) == "Paperwhite 1"
    assert kindle_model_label("unknown") == "Kindle Touch"


def test_dashboard_unique_id() -> None:
    assert dashboard_unique_id("abc123") == "abc123_dashboard"


def test_regenerate_unique_id() -> None:
    assert regenerate_unique_id("abc123") == "abc123_regenerate"


def test_dashboard_device_info() -> None:
    info = dashboard_device_info("abc123", KINDLE_TOUCH)
    assert info["identifiers"] == {(DOMAIN, "abc123")}
    assert info["name"] == "HomeKindle"
    assert info["manufacturer"] == "HomeKindle"
    assert info["model"] == "Kindle Touch"
    assert info["model_id"] == KINDLE_TOUCH


def test_dashboard_device_info_pw1() -> None:
    info = dashboard_device_info("xyz", KINDLE_PW1)
    assert info["model"] == "Paperwhite 1"
    assert info["model_id"] == KINDLE_PW1
