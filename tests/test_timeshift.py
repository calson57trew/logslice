"""Tests for logslice.timeshift."""

from datetime import timedelta
import pytest

from logslice.timeshift import parse_delta, shift_line, shift_lines


# ---------------------------------------------------------------------------
# parse_delta
# ---------------------------------------------------------------------------

def test_parse_delta_positive_seconds():
    assert parse_delta("+3600") == timedelta(seconds=3600)


def test_parse_delta_negative_minutes():
    assert parse_delta("-90m") == timedelta(seconds=-5400)


def test_parse_delta_hours():
    assert parse_delta("+2h") == timedelta(hours=2)


def test_parse_delta_days():
    assert parse_delta("-1d") == timedelta(days=-1)


def test_parse_delta_no_suffix_defaults_to_seconds():
    assert parse_delta("120") == timedelta(seconds=120)


def test_parse_delta_empty_raises():
    with pytest.raises(ValueError):
        parse_delta("")


# ---------------------------------------------------------------------------
# shift_line
# ---------------------------------------------------------------------------

def test_shift_line_iso_basic():
    line = "2024-03-01T12:00:00 ERROR something failed\n"
    result = shift_line(line, timedelta(hours=1))
    assert "2024-03-01T13:00:00" in result
    assert "ERROR something failed" in result


def test_shift_line_with_fractional():
    line = "2024-03-01T12:00:00.123456 INFO ok\n"
    result = shift_line(line, timedelta(seconds=30))
    assert "2024-03-01T12:00:30" in result


def test_shift_line_no_timestamp_unchanged():
    line = "    continuation line with no timestamp\n"
    assert shift_line(line, timedelta(hours=1)) == line


def test_shift_line_negative_delta():
    line = "2024-03-01T12:00:00 WARN slow query\n"
    result = shift_line(line, timedelta(hours=-2))
    assert "2024-03-01T10:00:00" in result


def test_shift_line_space_separated_date():
    line = "2024-03-01 06:00:00 DEBUG boot\n"
    result = shift_line(line, timedelta(minutes=5))
    assert "06:05:00" in result


# ---------------------------------------------------------------------------
# shift_lines
# ---------------------------------------------------------------------------

def test_shift_lines_iterator():
    lines = [
        "2024-01-01T00:00:00 INFO start\n",
        "    continuation\n",
        "2024-01-01T00:01:00 INFO end\n",
    ]
    result = list(shift_lines(iter(lines), timedelta(hours=1)))
    assert "2024-01-01T01:00:00" in result[0]
    assert result[1] == "    continuation\n"
    assert "2024-01-01T01:01:00" in result[2]
