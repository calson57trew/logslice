"""Tests for logslice.templater."""
from __future__ import annotations

import pytest

from logslice.templater import (
    _extract_level,
    _extract_message,
    count_templated,
    render_template,
    template_lines,
)

# ---------------------------------------------------------------------------
# _extract_level
# ---------------------------------------------------------------------------

def test_extract_level_error():
    assert _extract_level("2024-01-01T00:00:00Z ERROR something broke") == "ERROR"


def test_extract_level_info():
    assert _extract_level("INFO server started") == "INFO"


def test_extract_level_warning_variant():
    assert _extract_level("WARNING: disk low") == "WARNING"


def test_extract_level_no_match():
    assert _extract_level("no level here") == ""


# ---------------------------------------------------------------------------
# _extract_message
# ---------------------------------------------------------------------------

def test_extract_message_strips_timestamp():
    line = "2024-03-15T12:00:00Z INFO hello world"
    msg = _extract_message(line)
    assert "hello world" in msg
    assert "2024-03-15" not in msg


def test_extract_message_no_timestamp_returns_full():
    line = "no timestamp here"
    assert _extract_message(line) == "no timestamp here"


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_line_placeholder():
    result = render_template("{line}", "hello\n")
    assert result == "hello"


def test_render_template_index_placeholder():
    result = render_template("#{index} {line}", "msg\n", index=5)
    assert result == "#5 msg"


def test_render_template_timestamp_and_level():
    line = "2024-01-02T10:00:00Z ERROR boom\n"
    result = render_template("[{timestamp}] {level}: {message}", line)
    assert "2024-01-02" in result
    assert "ERROR" in result
    assert "boom" in result


def test_render_template_empty_timestamp_when_absent():
    result = render_template("{timestamp}|{line}", "plain line\n")
    assert result.startswith("|") or result.startswith("|plain")


def test_render_template_invalid_placeholder_raises():
    with pytest.raises(ValueError, match="Invalid template"):
        render_template("{unknown_field}", "line\n")


# ---------------------------------------------------------------------------
# template_lines
# ---------------------------------------------------------------------------

def test_template_lines_yields_newlines():
    lines = ["a\n", "b\n"]
    result = list(template_lines(lines, "{index}:{line}"))
    assert result == ["1:a\n", "2:b\n"]


def test_template_lines_custom_start_index():
    lines = ["x\n"]
    result = list(template_lines(lines, "{index}", start_index=10))
    assert result == ["10\n"]


# ---------------------------------------------------------------------------
# count_templated
# ---------------------------------------------------------------------------

def test_count_templated_returns_count():
    lines = ["line1\n", "line2\n", "line3\n"]
    rendered, count = count_templated(lines, "{line}")
    assert count == 3
    assert len(rendered) == 3
