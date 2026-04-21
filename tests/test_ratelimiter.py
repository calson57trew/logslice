"""Tests for logslice.ratelimiter."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.ratelimiter import (
    RateLimitStats,
    count_ratelimited,
    parse_window,
    ratelimit_lines,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(second: int, sub: int = 0) -> str:
    """Build a log line whose timestamp sits at epoch + *second*."""
    dt = datetime(1970, 1, 1, 0, 0, second % 60, sub, tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + " some log message"


# ---------------------------------------------------------------------------
# parse_window
# ---------------------------------------------------------------------------

def test_parse_window_seconds():
    assert parse_window("1s") == 1
    assert parse_window("30s") == 30


def test_parse_window_minutes():
    assert parse_window("2m") == 120
    assert parse_window("1min") == 60


def test_parse_window_hours():
    assert parse_window("1h") == 3600
    assert parse_window("2hr") == 7200


def test_parse_window_bare_integer_is_seconds():
    assert parse_window("5") == 5


def test_parse_window_invalid_raises():
    with pytest.raises(ValueError):
        parse_window("banana")


# ---------------------------------------------------------------------------
# ratelimit_lines
# ---------------------------------------------------------------------------

def test_all_lines_within_limit_pass_through():
    lines = [_ts(0), _ts(0), _ts(1)]
    result = list(ratelimit_lines(lines, max_lines=5, window_seconds=1))
    assert result == lines


def test_excess_lines_in_same_window_are_dropped():
    lines = [_ts(0), _ts(0), _ts(0), _ts(0)]
    result = list(ratelimit_lines(lines, max_lines=2, window_seconds=1))
    assert len(result) == 2
    assert result == lines[:2]


def test_new_window_resets_counter():
    lines = [_ts(0), _ts(0), _ts(0), _ts(2), _ts(2)]
    result = list(ratelimit_lines(lines, max_lines=2, window_seconds=1))
    # first window: keep 2, drop 1; second window: keep 2
    assert len(result) == 4


def test_continuation_follows_kept_parent():
    lines = [_ts(0), "    at com.example.Foo", "    at com.example.Bar"]
    result = list(ratelimit_lines(lines, max_lines=5, window_seconds=1))
    assert result == lines


def test_continuation_dropped_with_parent():
    lines = [
        _ts(0), _ts(0), _ts(0),   # third should be dropped
        "    continuation of dropped",
    ]
    result = list(ratelimit_lines(lines, max_lines=2, window_seconds=1))
    assert len(result) == 2
    assert "continuation" not in "".join(result)


def test_lines_without_timestamp_always_emitted():
    lines = ["no timestamp here", "also no timestamp"]
    result = list(ratelimit_lines(lines, max_lines=1, window_seconds=1))
    assert result == lines


def test_invalid_max_lines_raises():
    with pytest.raises(ValueError):
        list(ratelimit_lines([], max_lines=0))


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        list(ratelimit_lines([], max_lines=1, window_seconds=0))


# ---------------------------------------------------------------------------
# count_ratelimited
# ---------------------------------------------------------------------------

def test_count_ratelimited_stats():
    lines = [_ts(0)] * 5
    stats = count_ratelimited(lines, max_lines=3, window_seconds=1)
    assert isinstance(stats, RateLimitStats)
    assert stats.total == 5
    assert stats.emitted == 3
    assert stats.dropped == 2
