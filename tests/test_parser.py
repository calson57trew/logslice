"""Tests for logslice.parser timestamp extraction."""

import pytest
from datetime import datetime
from logslice.parser import extract_timestamp, parse_user_timestamp


class TestExtractTimestamp:
    def test_iso8601_basic(self):
        line = '2024-03-12T14:22:01 INFO server started'
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 12, 14, 22, 1)

    def test_iso8601_with_fractional(self):
        line = '2024-03-12T14:22:01.456Z ERROR disk full'
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 12, 14, 22, 1)

    def test_space_separated(self):
        line = '2024-01-01 00:00:00 DEBUG boot'
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 1, 1, 0, 0, 0)

    def test_no_timestamp_returns_none(self):
        line = '    at com.example.App.main(App.java:42)'
        assert extract_timestamp(line) is None

    def test_nginx_combined(self):
        line = '127.0.0.1 - - [12/Mar/2024:14:22:01 +0000] "GET / HTTP/1.1" 200'
        ts = extract_timestamp(line)
        assert ts == datetime(2024, 3, 12, 14, 22, 1)


class TestParseUserTimestamp:
    def test_full_datetime(self):
        assert parse_user_timestamp('2024-03-12 14:22:01') == datetime(2024, 3, 12, 14, 22, 1)

    def test_date_only(self):
        assert parse_user_timestamp('2024-03-12') == datetime(2024, 3, 12, 0, 0, 0)

    def test_iso_no_seconds(self):
        assert parse_user_timestamp('2024-03-12T14:22') == datetime(2024, 3, 12, 14, 22, 0)

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match='Unrecognized timestamp format'):
            parse_user_timestamp('not-a-date')
