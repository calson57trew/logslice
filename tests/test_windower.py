"""Tests for logslice.windower."""
from __future__ import annotations

import pytest

from logslice.windower import (
    WindowResult,
    _floor,
    _parse_ts,
    count_windows,
    tumbling_windows,
)
from datetime import datetime


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ts(s: str) -> str:
    return f"{s} ERROR something happened\n"


# ---------------------------------------------------------------------------
# _parse_ts
# ---------------------------------------------------------------------------

def test_parse_ts_iso8601_T():
    line = "2024-03-01T12:00:05 some log\n"
    dt = _parse_ts(line)
    assert dt == datetime(2024, 3, 1, 12, 0, 5)


def test_parse_ts_space_separator():
    dt = _parse_ts("2024-03-01 12:00:05.123 INFO ok\n")
    assert dt == datetime(2024, 3, 1, 12, 0, 5, 123000)


def test_parse_ts_no_timestamp_returns_none():
    assert _parse_ts("   continuation line\n") is None


# ---------------------------------------------------------------------------
# _floor
# ---------------------------------------------------------------------------

def test_floor_60s_exact():
    dt = datetime(2024, 1, 1, 0, 1, 0)
    assert _floor(dt, 60) == datetime(2024, 1, 1, 0, 1, 0)


def test_floor_60s_mid_minute():
    dt = datetime(2024, 1, 1, 0, 1, 45)
    assert _floor(dt, 60) == datetime(2024, 1, 1, 0, 1, 0)


def test_floor_300s_bucket():
    dt = datetime(2024, 1, 1, 0, 7, 30)
    assert _floor(dt, 300) == datetime(2024, 1, 1, 0, 5, 0)


# ---------------------------------------------------------------------------
# tumbling_windows
# ---------------------------------------------------------------------------

LINES_60S = [
    _ts("2024-03-01 10:00:10"),
    _ts("2024-03-01 10:00:45"),
    _ts("2024-03-01 10:01:05"),
    _ts("2024-03-01 10:01:55"),
    _ts("2024-03-01 10:03:00"),
]


def test_tumbling_windows_count():
    wins = list(tumbling_windows(LINES_60S, 60))
    assert len(wins) == 3


def test_tumbling_window_first_bucket_lines():
    wins = list(tumbling_windows(LINES_60S, 60))
    assert len(wins[0]) == 2


def test_tumbling_window_start_end_strings():
    wins = list(tumbling_windows(LINES_60S, 60))
    assert wins[0].start == "2024-03-01 10:00:00"
    assert wins[0].end == "2024-03-01 10:01:00"


def test_continuation_attached_to_last_bucket():
    lines = [
        _ts("2024-03-01 10:00:05"),
        "    continuation line\n",
    ]
    wins = list(tumbling_windows(lines, 60))
    assert len(wins) == 1
    assert len(wins[0]) == 2


def test_untimed_only_lines_produce_no_windows():
    lines = ["   no timestamp\n", "   another\n"]
    wins = list(tumbling_windows(lines, 60))
    assert wins == []


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        list(tumbling_windows([], 0))


# ---------------------------------------------------------------------------
# count_windows
# ---------------------------------------------------------------------------

def test_count_windows():
    assert count_windows(LINES_60S, 60) == 3


def test_count_windows_large_bucket():
    assert count_windows(LINES_60S, 3600) == 1
