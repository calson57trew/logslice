"""Tests for logslice.deduplicator."""

import pytest
from logslice.deduplicator import normalize_line, deduplicate_lines, count_duplicates


def test_normalize_removes_iso8601():
    line = "2024-03-15T12:00:00Z ERROR something happened"
    assert normalize_line(line) == "ERROR something happened"


def test_normalize_removes_space_separated_timestamp():
    line = "2024-03-15 12:00:00 INFO starting up"
    assert normalize_line(line) == "INFO starting up"


def test_normalize_no_timestamp():
    line = "plain log line"
    assert normalize_line(line) == "plain log line"


def test_deduplicate_removes_global_duplicates():
    lines = [
        "2024-01-01T00:00:01Z INFO hello\n",
        "2024-01-01T00:00:02Z INFO world\n",
        "2024-01-01T00:00:03Z INFO hello\n",
    ]
    result = list(deduplicate_lines(lines))
    assert len(result) == 2
    assert result[0] == lines[0]
    assert result[1] == lines[1]


def test_deduplicate_consecutive_only_suppresses_repeats():
    lines = [
        "2024-01-01T00:00:01Z INFO hello\n",
        "2024-01-01T00:00:02Z INFO hello\n",
        "2024-01-01T00:00:03Z INFO world\n",
        "2024-01-01T00:00:04Z INFO hello\n",
    ]
    result = list(deduplicate_lines(lines, consecutive_only=True))
    assert len(result) == 3
    assert result[2] == lines[3]


def test_deduplicate_consecutive_only_keeps_non_adjacent():
    lines = [
        "2024-01-01T00:00:01Z INFO a\n",
        "2024-01-01T00:00:02Z INFO b\n",
        "2024-01-01T00:00:03Z INFO a\n",
    ]
    result = list(deduplicate_lines(lines, consecutive_only=True))
    assert len(result) == 3


def test_deduplicate_empty_input():
    assert list(deduplicate_lines([])) == []


def test_count_duplicates_global():
    lines = ["INFO a\n", "INFO b\n", "INFO a\n", "INFO a\n"]
    assert count_duplicates(lines) == 2


def test_count_duplicates_consecutive():
    lines = ["INFO a\n", "INFO a\n", "INFO b\n", "INFO a\n"]
    assert count_duplicates(lines, consecutive_only=True) == 1


def test_count_duplicates_no_dupes():
    lines = ["INFO a\n", "INFO b\n", "INFO c\n"]
    assert count_duplicates(lines) == 0
