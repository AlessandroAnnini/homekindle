"""Fixture weather, events, and footer for homekindle-core."""

from __future__ import annotations

from dataclasses import dataclass


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
    todos: tuple[str, ...]


DEFAULT_FIXTURES = DashboardFixtures(
    weather=(
        WeatherFixture("today", "mostly clear", 1, temp_c=25.0),
        WeatherFixture("tomorrow", "overcast", 3, temp_min_c=22.0, temp_max_c=33.0),
    ),
    events=(
        EventFixture("today", "09:00", "Stand-up"),
        EventFixture("today", "14:30", "Library"),
    ),
    updated="22:45",
    workday=True,
    exceptions=("fridge door",),
    todos=(),
)
