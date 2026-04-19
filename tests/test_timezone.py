"""Tests for logslice.timezone."""

from datetime import timezone, timedelta, datetime
import pytest

from logslice.timezone import (
    parse_tzoffset,
    convert_timestamp,
    convert_line,
    convert_lines,
    count_converted,
)


def test_parse_utc():
    assert parse_tzoffset('UTC') == timezone.utc


def test_parse_z():
    assert parse_tzoffset('Z') == timezone.utc


def test_parse_positive_offset():
    tz = parse_tzoffset('+05:30')
    assert tz.utcoffset(None) == timedelta(hours=5, minutes=30)


def test_parse_negative_offset():
    tz = parse_tzoffset('-08:00')
    assert tz.utcoffset(None) == timedelta(hours=-8)


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        parse_tzoffset('EST')


def test_convert_timestamp_naive_assumes_utc():
    naive = datetime(2024, 1, 1, 12, 0, 0)
    tz = timezone(timedelta(hours=2))
    result = convert_timestamp(naive, tz)
    assert result.hour == 14
    assert result.tzinfo == tz


def test_convert_timestamp_aware():
    aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    tz = timezone(timedelta(hours=-5))
    result = convert_timestamp(aware, tz)
    assert result.hour == 7


def test_convert_line_replaces_timestamp():
    line = '2024-01-01T00:00:00+00:00 INFO starting up\n'
    tz = timezone(timedelta(hours=1))
    result = convert_line(line, tz)
    assert '2024-01-01T01:00:00' in result


def test_convert_line_no_timestamp_unchanged():
    line = 'no timestamp here\n'
    tz = timezone.utc
    assert convert_line(line, tz) == line


def test_convert_lines_all_converted():
    lines = [
        '2024-06-01T10:00:00+00:00 ERROR boom\n',
        '2024-06-01T10:01:00+00:00 INFO ok\n',
    ]
    tz = timezone(timedelta(hours=3))
    result = convert_lines(lines, tz)
    assert all('T13:' in r for r in result)


def test_count_converted():
    original = ['2024-01-01T00:00:00+00:00 INFO a\n', 'no ts\n']
    tz = timezone(timedelta(hours=1))
    converted = convert_lines(original, tz)
    assert count_converted(original, converted) == 1
