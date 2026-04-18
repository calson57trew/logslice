"""Tests for logslice.exporter."""

import json
import pytest

from logslice.exporter import (
    export_plain,
    export_json,
    export_csv,
    get_exporter,
    export_lines,
    SUPPORTED_FORMATS,
)

SAMPLE_LINES = [
    "2024-01-15T10:00:00 INFO  server started\n",
    "2024-01-15T10:00:05 ERROR disk full\n",
    "continuation line\n",
]


def test_plain_passthrough():
    result = list(export_plain(SAMPLE_LINES))
    assert result == SAMPLE_LINES


def test_plain_adds_newline_if_missing():
    result = list(export_plain(["no newline"]))
    assert result == ["no newline\n"]


def test_json_produces_valid_json():
    result = list(export_json(SAMPLE_LINES))
    assert len(result) == 3
    obj = json.loads(result[0])
    assert "timestamp" in obj
    assert "message" in obj


def test_json_timestamp_parsed():
    result = list(export_json(["2024-01-15T10:00:00 INFO hello"]))
    obj = json.loads(result[0])
    assert obj["timestamp"] == "2024-01-15T10:00:00"


def test_json_no_timestamp_is_none():
    result = list(export_json(["continuation line"]))
    obj = json.loads(result[0])
    assert obj["timestamp"] is None


def test_csv_has_header():
    result = list(export_csv(SAMPLE_LINES))
    assert result[0].strip() == "timestamp,message"


def test_csv_row_count():
    result = list(export_csv(SAMPLE_LINES))
    # header + 3 data rows
    assert len(result) == 4


def test_csv_empty_timestamp_for_continuation():
    result = list(export_csv(["plain continuation"]))
    # header + 1 row
    assert len(result) == 2
    assert result[1].startswith(",")


def test_get_exporter_returns_callable():
    for fmt in SUPPORTED_FORMATS:
        fn = get_exporter(fmt)
        assert callable(fn)


def test_get_exporter_invalid_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        get_exporter("xml")


def test_export_lines_materializes():
    result = export_lines(SAMPLE_LINES, "plain")
    assert isinstance(result, list)
    assert len(result) == 3
