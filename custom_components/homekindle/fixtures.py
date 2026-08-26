"""Fixture weather, events, and footer for homekindle-core."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class WeatherFixture:
    day: str
    condition: str
    wmo_code: int
    temp_c: float | None = None
    temp_min_c: float | None = None
    temp_max_c: float | None = None


@dataclass(frozen=True)
class EventFixture:
    day: str
    time_label: str
    title: str


@dataclass(frozen=True)
class DashboardFixtures:
    weather: tuple[WeatherFixture, ...]
    events: tuple[EventFixture, ...]
    updated: str
    workday: bool
    exceptions: tuple[str, ...]
    as_of: date | None = None


DEFAULT_FIXTURES = DashboardFixtures(
    weather=(
        WeatherFixture("today", "mostly clear", 1, temp_c=25.0),
        WeatherFixture("tomorrow", "overcast", 3, temp_min_c=22.0, temp_max_c=33.0),
    ),
    events=(
        EventFixture("today", "all day", "Marta's birthday"),
        EventFixture("today", "09:00", "Stand-up"),
        EventFixture("today", "10:30", "Product Review"),
        EventFixture("today", "14:00", "Design Sprint"),
        EventFixture("today", "16:30", "1:1 with Manager"),
        EventFixture("tomorrow", "all day", "Leo's birthday"),
        EventFixture("tomorrow", "10:00", "Library"),
    ),
    updated="22:45",
    workday=True,
    exceptions=("fridge door",),
)
