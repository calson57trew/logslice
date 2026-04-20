"""Tests for logslice.throttler."""

from __future__ import annotations

import pytest

from logslice.throttler import throttle_lines, count_throttled


def _ts(second: int, msg: str = "msg") -> str:
    """Build a simple ISO-8601 log line at the given second within one minute."""
    return f"2024-01-01T00:00:{second:02d}Z INFO {msg}\n"


def test_all_lines_within_limit_pass_through():
    lines = [_ts(0, "a"), _ts(1, "b"), _ts(2, "c")]
    result = list(throttle_lines(lines, max_per_window=5, window_seconds=1.0))
    assert result == lines


def test_excess_lines_in_window_are_dropped():
    # Three lines all within the same 1-second window
    lines = [_ts(0, "a"), _ts(0, "b"), _ts(0, "c")]
    result = list(throttle_lines(lines, max_per_window=2, window_seconds=1.0))
    assert len(result) == 2
    assert result == lines[:2]


def test_new_window_resets_counter():
    # First window: seconds 0–0; second window: second 2 (gap >= 1s)
    lines = [_ts(0, "a"), _ts(0, "b"), _ts(0, "c"), _ts(2, "d")]
    result = list(throttle_lines(lines, max_per_window=1, window_seconds=1.0))
    assert _ts(0, "a") in result
    assert _ts(2, "d") in result
    assert len(result) == 2


def test_continuation_lines_follow_parent_kept():
    lines = [_ts(0, "start"), "    traceback line\n", "    more trace\n"]
    result = list(throttle_lines(lines, max_per_window=5))
    assert result == lines


def test_continuation_lines_follow_parent_dropped():
    lines = [
        _ts(0, "a"), _ts(0, "b"),  # only 1 allowed
        "    continuation of b\n",
    ]
    result = list(throttle_lines(lines, max_per_window=1))
    assert _ts(0, "a") in result
    assert _ts(0, "b") not in result
    assert "    continuation of b\n" not in result


def test_lines_without_timestamp_always_pass():
    lines = ["no timestamp here\n", "another plain line\n"]
    result = list(throttle_lines(lines, max_per_window=1))
    assert result == lines


def test_invalid_max_per_window_raises():
    with pytest.raises(ValueError, match="max_per_window"):
        list(throttle_lines([_ts(0)], max_per_window=0))


def test_invalid_window_seconds_raises():
    with pytest.raises(ValueError, match="window_seconds"):
        list(throttle_lines([_ts(0)], max_per_window=1, window_seconds=0))


def test_count_throttled_summary():
    lines = [_ts(0, "a"), _ts(0, "b"), _ts(0, "c")]
    summary = count_throttled(lines, max_per_window=1, window_seconds=1.0)
    assert summary["total"] == 3
    assert summary["kept"] == 1
    assert summary["dropped"] == 2


def test_empty_input_returns_empty():
    result = list(throttle_lines([], max_per_window=10))
    assert result == []
