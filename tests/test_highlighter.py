"""Tests for logslice.highlighter."""

import pytest
from logslice.highlighter import (
    highlight_level,
    highlight_pattern,
    highlight_lines,
    ANSI_RESET,
    LEVEL_COLORS,
)


def test_highlight_level_error():
    line = "2024-01-01 ERROR something went wrong"
    result = highlight_level(line)
    assert LEVEL_COLORS["ERROR"] in result
    assert ANSI_RESET in result
    assert "ERROR" in result


def test_highlight_level_info():
    line = "2024-01-01 INFO service started"
    result = highlight_level(line)
    assert LEVEL_COLORS["INFO"] in result


def test_highlight_level_warning_variant():
    line = "WARNING: disk space low"
    result = highlight_level(line)
    assert LEVEL_COLORS["WARNING"] in result


def test_highlight_level_no_match():
    line = "plain log line with no level"
    assert highlight_level(line) == line


def test_highlight_level_case_insensitive():
    line = "2024-01-01 debug verbose output"
    result = highlight_level(line)
    assert ANSI_RESET in result


def test_highlight_pattern_basic():
    line = "connected to host-42 successfully"
    result = highlight_pattern(line, r"host-\d+")
    assert "host-42" in result
    assert ANSI_RESET in result


def test_highlight_pattern_no_match():
    line = "no numbers here"
    result = highlight_pattern(line, r"\d+")
    assert result == line


def test_highlight_pattern_invalid_regex():
    line = "some log line"
    result = highlight_pattern(line, r"[invalid")
    assert result == line


def test_highlight_lines_levels_only():
    lines = ["INFO starting", "ERROR failed", "plain line"]
    result = list(highlight_lines(iter(lines), levels=True))
    assert LEVEL_COLORS["INFO"] in result[0]
    assert LEVEL_COLORS["ERROR"] in result[1]
    assert result[2] == "plain line"


def test_highlight_lines_pattern_only():
    lines = ["request id=abc123", "no match here"]
    result = list(highlight_lines(iter(lines), levels=False, pattern=r"id=\w+"))
    assert ANSI_RESET in result[0]
    assert result[1] == "no match here"


def test_highlight_lines_both():
    lines = ["ERROR id=xyz failed"]
    result = list(highlight_lines(iter(lines), levels=True, pattern=r"id=\w+"))
    assert LEVEL_COLORS["ERROR"] in result[0]
    assert ANSI_RESET in result[0]
