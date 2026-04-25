"""Tests for logslice.inspector."""

from __future__ import annotations

import pytest

from logslice.inspector import (
    InspectResult,
    _detect_ts_format,
    format_inspect,
    inspect_lines,
)


ISO_LINE = "2024-03-15T10:22:01 ERROR something broke request_id=abc123"
SPACE_LINE = "2024-03-15 10:22:01 INFO service started"
EPOCH_LINE = "1710498121 WARN disk usage high"
NO_TS_LINE = "plain log line with no timestamp"
KV_LINE = "2024-03-15T10:22:01 DEBUG user=alice action=login status=ok"


def test_total_lines():
    result = inspect_lines([ISO_LINE, SPACE_LINE, NO_TS_LINE])
    assert result.total_lines == 3


def test_timed_lines_counted():
    result = inspect_lines([ISO_LINE, SPACE_LINE, NO_TS_LINE])
    assert result.timed_lines == 2


def test_no_timed_lines():
    result = inspect_lines([NO_TS_LINE, "another plain line"])
    assert result.timed_lines == 0


def test_timestamp_format_iso8601():
    result = inspect_lines([ISO_LINE, SPACE_LINE])
    assert result.timestamp_formats.get("iso8601", 0) == 2


def test_timestamp_format_epoch():
    result = inspect_lines([EPOCH_LINE])
    assert result.timestamp_formats.get("epoch", 0) == 1


def test_level_counts_error():
    result = inspect_lines([ISO_LINE])
    assert result.level_counts.get("ERROR", 0) == 1


def test_level_counts_warning_normalised():
    line = "2024-03-15T10:00:00 WARNING something"
    result = inspect_lines([line])
    assert "WARN" in result.level_counts
    assert "WARNING" not in result.level_counts


def test_level_counts_multiple():
    lines = [
        "2024-03-15T10:00:00 INFO a",
        "2024-03-15T10:00:01 ERROR b",
        "2024-03-15T10:00:02 INFO c",
    ]
    result = inspect_lines(lines)
    assert result.level_counts["INFO"] == 2
    assert result.level_counts["ERROR"] == 1


def test_kv_fields_extracted():
    result = inspect_lines([KV_LINE])
    assert "user" in result.field_names
    assert "action" in result.field_names
    assert "status" in result.field_names


def test_kv_field_frequency():
    lines = [KV_LINE, "2024-03-15T10:22:02 DEBUG user=bob action=logout"]
    result = inspect_lines(lines)
    assert result.field_names["user"] == 2
    assert result.field_names["action"] == 2


def test_sample_lines_limited():
    lines = [f"2024-03-15T10:00:0{i} INFO msg {i}" for i in range(10)]
    result = inspect_lines(lines, max_samples=3)
    assert len(result.sample_lines) == 3


def test_sample_lines_default_five():
    lines = [f"2024-03-15T10:00:0{i} INFO msg {i}" for i in range(7)]
    result = inspect_lines(lines)
    assert len(result.sample_lines) == 5


def test_detect_ts_format_iso():
    assert _detect_ts_format(ISO_LINE) == "iso8601"


def test_detect_ts_format_epoch():
    assert _detect_ts_format(EPOCH_LINE) == "epoch"


def test_detect_ts_format_none():
    assert _detect_ts_format(NO_TS_LINE) is None


def test_format_inspect_contains_totals():
    result = inspect_lines([ISO_LINE, NO_TS_LINE])
    report = format_inspect(result)
    assert "total_lines" in report
    assert "timed_lines" in report


def test_format_inspect_no_levels():
    result = inspect_lines([NO_TS_LINE])
    report = format_inspect(result)
    assert "none" in report


def test_empty_input():
    result = inspect_lines([])
    assert result.total_lines == 0
    assert result.timed_lines == 0
    assert result.level_counts == {}
    assert result.field_names == {}
