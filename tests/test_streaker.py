"""Tests for logslice.streaker."""
from __future__ import annotations

import pytest

from logslice.streaker import (
    Streak,
    compile_predicate,
    count_streaks,
    find_streaks,
    format_streak_summary,
    longest_streak,
)


# ---------------------------------------------------------------------------
# compile_predicate
# ---------------------------------------------------------------------------

def test_compile_predicate_matches_substring():
    pred = compile_predicate("error")
    assert pred("2024-01-01 ERROR something went wrong")


def test_compile_predicate_case_insensitive_by_default():
    pred = compile_predicate("warn")
    assert pred("WARNING: disk almost full")


def test_compile_predicate_case_sensitive_flag():
    pred = compile_predicate("ERROR", ignore_case=False)
    assert not pred("error: lowercase")
    assert pred("ERROR: uppercase")


def test_compile_predicate_no_match_returns_false():
    pred = compile_predicate("critical")
    assert not pred("INFO: all good")


# ---------------------------------------------------------------------------
# find_streaks
# ---------------------------------------------------------------------------

_LINES = [
    "INFO  startup\n",
    "ERROR first\n",
    "ERROR second\n",
    "ERROR third\n",
    "INFO  recovered\n",
    "ERROR lone\n",
    "INFO  done\n",
]


def test_find_streaks_basic():
    pred = compile_predicate("error")
    streaks = list(find_streaks(_LINES, pred, min_length=2))
    assert len(streaks) == 1
    assert len(streaks[0]) == 3


def test_find_streaks_min_length_one_includes_singles():
    pred = compile_predicate("error")
    streaks = list(find_streaks(_LINES, pred, min_length=1))
    assert len(streaks) == 2  # run-of-3 and the lone ERROR


def test_find_streaks_no_match_returns_empty():
    pred = compile_predicate("critical")
    streaks = list(find_streaks(_LINES, pred))
    assert streaks == []


def test_find_streaks_streak_at_end_of_input():
    lines = ["INFO a\n", "ERROR x\n", "ERROR y\n"]
    pred = compile_predicate("error")
    streaks = list(find_streaks(lines, pred, min_length=2))
    assert len(streaks) == 1
    assert streaks[0].lines == ["ERROR x\n", "ERROR y\n"]


def test_find_streaks_captures_timestamps():
    lines = [
        "2024-01-01T10:00:00 ERROR a\n",
        "2024-01-01T10:00:01 ERROR b\n",
        "2024-01-01T10:00:02 INFO ok\n",
    ]
    pred = compile_predicate("error")
    streaks = list(find_streaks(lines, pred, min_length=2))
    assert streaks[0].start_ts == "2024-01-01T10:00:00"
    assert streaks[0].end_ts == "2024-01-01T10:00:01"


# ---------------------------------------------------------------------------
# longest_streak / count_streaks
# ---------------------------------------------------------------------------

def test_longest_streak_returns_largest():
    s1 = Streak(lines=["a", "b"])
    s2 = Streak(lines=["a", "b", "c"])
    assert longest_streak([s1, s2]) is s2


def test_longest_streak_empty_input_returns_none():
    assert longest_streak([]) is None


def test_count_streaks_correct():
    pred = compile_predicate("error")
    streaks = list(find_streaks(_LINES, pred, min_length=1))
    assert count_streaks(streaks) == 2


# ---------------------------------------------------------------------------
# format_streak_summary
# ---------------------------------------------------------------------------

def test_format_summary_no_streaks():
    assert format_streak_summary([]) == "No streaks found."


def test_format_summary_contains_count():
    s = Streak(lines=["a", "b", "c"])
    summary = format_streak_summary([s])
    assert "Streaks found: 1" in summary
    assert "3 lines" in summary
