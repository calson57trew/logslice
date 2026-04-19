"""Tests for logslice.profiler."""
from datetime import timedelta

import pytest

from logslice.profiler import ProfileResult, format_profile, profile_lines

LINES = [
    "2024-01-01T00:00:00Z INFO  start\n",
    "2024-01-01T00:00:05Z INFO  five seconds later\n",
    "continuation line\n",
    "2024-01-01T00:01:00Z ERROR big gap\n",
    "2024-01-01T00:01:01Z INFO  one second\n",
]


def test_total_lines():
    r = profile_lines(LINES)
    assert r.total_lines == 5


def test_timed_lines():
    r = profile_lines(LINES)
    assert r.timed_lines == 4


def test_first_and_last_timestamp():
    r = profile_lines(LINES)
    assert r.first_ts is not None
    assert r.last_ts is not None
    assert r.last_ts > r.first_ts


def test_duration():
    r = profile_lines(LINES)
    assert r.duration == timedelta(seconds=61)


def test_max_gap():
    r = profile_lines(LINES)
    assert r.max_gap == timedelta(seconds=55)


def test_gap_threshold_filters_small_gaps():
    r = profile_lines(LINES, gap_threshold=timedelta(seconds=10))
    # Only the 55-second gap should be recorded
    assert len(r.gaps) == 1
    assert r.gaps[0][2] == timedelta(seconds=55)


def test_all_gaps_no_threshold():
    r = profile_lines(LINES)
    assert len(r.gaps) == 3


def test_empty_input():
    r = profile_lines([])
    assert r.total_lines == 0
    assert r.first_ts is None
    assert r.duration is None
    assert r.lines_per_second is None


def test_no_timestamps():
    r = profile_lines(["no ts here\n", "also no ts\n"])
    assert r.timed_lines == 0
    assert r.max_gap is None


def test_lines_per_second():
    r = profile_lines(LINES)
    assert r.lines_per_second is not None
    assert r.lines_per_second > 0


def test_format_profile_contains_keys():
    r = profile_lines(LINES)
    text = format_profile(r)
    assert "Total lines" in text
    assert "Duration" in text
    assert "Largest gap" in text
    assert "Lines/sec" in text
