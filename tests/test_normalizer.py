"""Tests for logslice.normalizer."""

import pytest
from logslice.normalizer import (
    strip_ansi,
    collapse_whitespace,
    strip_control_chars,
    normalize_line,
    normalize_lines,
    count_normalized,
)


# ---------------------------------------------------------------------------
# strip_ansi
# ---------------------------------------------------------------------------

def test_strip_ansi_removes_color_code():
    assert strip_ansi("\x1b[31mERROR\x1b[0m") == "ERROR"


def test_strip_ansi_no_codes_unchanged():
    assert strip_ansi("plain text") == "plain text"


def test_strip_ansi_multiple_codes():
    line = "\x1b[1m\x1b[33mWARN\x1b[0m: something"
    assert strip_ansi(line) == "WARN: something"


# ---------------------------------------------------------------------------
# collapse_whitespace
# ---------------------------------------------------------------------------

def test_collapse_whitespace_basic():
    assert collapse_whitespace("foo   bar") == "foo bar"


def test_collapse_whitespace_preserve_indent():
    result = collapse_whitespace("    foo   bar", preserve_indent=True)
    assert result == "    foo bar"


def test_collapse_whitespace_single_spaces_unchanged():
    assert collapse_whitespace("a b c") == "a b c"


# ---------------------------------------------------------------------------
# strip_control_chars
# ---------------------------------------------------------------------------

def test_strip_control_chars_removes_bell():
    assert strip_control_chars("foo\x07bar") == "foobar"


def test_strip_control_chars_keeps_tab_and_newline():
    # tabs (\x09) and newlines (\x0a) are NOT matched by the pattern
    line = "col1\tcol2\n"
    assert strip_control_chars(line) == line


# ---------------------------------------------------------------------------
# normalize_line
# ---------------------------------------------------------------------------

def test_normalize_line_full_pipeline():
    line = "\x1b[32m2024-01-01  INFO\x1b[0m  message\x07\n"
    result = normalize_line(line)
    assert result == "2024-01-01 INFO message\n"


def test_normalize_line_preserves_trailing_newline():
    result = normalize_line("hello\n")
    assert result.endswith("\n")


def test_normalize_line_no_trailing_newline_kept_absent():
    result = normalize_line("hello")
    assert not result.endswith("\n")


def test_normalize_line_ansi_disabled():
    line = "\x1b[31mERROR\x1b[0m\n"
    result = normalize_line(line, ansi=False)
    assert "\x1b[" in result


def test_normalize_line_whitespace_disabled():
    result = normalize_line("foo   bar", whitespace=False)
    assert "   " in result


# ---------------------------------------------------------------------------
# normalize_lines
# ---------------------------------------------------------------------------

def test_normalize_lines_yields_all():
    lines = ["\x1b[31mERR\x1b[0m\n", "ok  line\n"]
    result = list(normalize_lines(lines))
    assert result == ["ERR\n", "ok line\n"]


# ---------------------------------------------------------------------------
# count_normalized
# ---------------------------------------------------------------------------

def test_count_normalized_detects_changes():
    original = ["foo   bar\n", "clean\n"]
    normalized = ["foo bar\n", "clean\n"]
    assert count_normalized(original, normalized) == 1


def test_count_normalized_no_changes():
    lines = ["a\n", "b\n"]
    assert count_normalized(lines, lines) == 0
