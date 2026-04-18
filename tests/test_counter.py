"""Tests for logslice.counter module."""

import pytest
from logslice.counter import SliceStats, count_lines


def test_stats_initial_values():
    s = SliceStats()
    assert s.total_lines == 0
    assert s.matched_lines == 0
    assert s.skipped_lines == 0
    assert s.pattern_hits == {}


def test_record_matched():
    s = SliceStats()
    s.record("some line", matched=True)
    assert s.total_lines == 1
    assert s.matched_lines == 1
    assert s.skipped_lines == 0


def test_record_skipped():
    s = SliceStats()
    s.record("some line", matched=False)
    assert s.total_lines == 1
    assert s.matched_lines == 0
    assert s.skipped_lines == 1


def test_record_pattern_hit():
    s = SliceStats()
    s.record("error here", matched=True, pattern="error")
    assert s.pattern_hits["error"] == 1
    s.record("another error", matched=True, pattern="error")
    assert s.pattern_hits["error"] == 2


def test_summary_no_patterns():
    s = SliceStats()
    s.record("a", matched=True)
    s.record("b", matched=False)
    summary = s.summary()
    assert "Total lines processed : 2" in summary
    assert "Matched lines         : 1" in summary
    assert "Skipped lines         : 1" in summary
    assert "Pattern hits" not in summary


def test_summary_with_patterns():
    s = SliceStats()
    s.record("error line", matched=True, pattern="error")
    summary = s.summary()
    assert "Pattern hits" in summary
    assert "'error': 1" in summary


def test_count_lines_no_pattern():
    lines = ["line one\n", "line two\n", "line three\n"]
    stats = count_lines(lines)
    assert stats.total_lines == 3
    assert stats.matched_lines == 3
    assert stats.skipped_lines == 0


def test_count_lines_with_pattern():
    lines = ["INFO start\n", "ERROR boom\n", "INFO end\n"]
    stats = count_lines(lines, pattern="ERROR")
    assert stats.total_lines == 3
    assert stats.pattern_hits.get("ERROR", 0) == 1
