"""Tests for logslice/pivot.py"""

import pytest

from logslice.pivot import PivotTable, _floor_to_bucket, build_pivot, format_pivot


# ---------------------------------------------------------------------------
# _floor_to_bucket
# ---------------------------------------------------------------------------

def test_floor_exact_minute():
    assert _floor_to_bucket("2024-01-15 12:01:00", 60) == "2024-01-15 12:01:00"


def test_floor_mid_minute():
    result = _floor_to_bucket("2024-01-15 12:01:45", 60)
    assert result == "2024-01-15 12:01:00"


def test_floor_five_minute_bucket():
    result = _floor_to_bucket("2024-01-15 12:07:33", 300)
    assert result == "2024-01-15 12:05:00"


def test_floor_no_timestamp_returns_original():
    raw = "not a timestamp at all"
    assert _floor_to_bucket(raw, 60) == raw


def test_floor_iso8601_T_separator():
    result = _floor_to_bucket("2024-01-15T09:30:45", 60)
    assert result == "2024-01-15 09:30:00"


# ---------------------------------------------------------------------------
# build_pivot
# ---------------------------------------------------------------------------

LINES = [
    "2024-01-15 12:00:10 ERROR disk full\n",
    "2024-01-15 12:00:45 ERROR disk full\n",
    "2024-01-15 12:01:05 INFO  all good\n",
    "2024-01-15 12:01:55 ERROR disk full\n",
    "continuation line no timestamp\n",
]


def test_total_lines():
    t = build_pivot(LINES, pattern="ERROR")
    assert t.total_lines == 5


def test_total_matched():
    t = build_pivot(LINES, pattern="ERROR")
    assert t.total_matched == 3


def test_bucket_counts():
    t = build_pivot(LINES, pattern="ERROR", bucket_size=60)
    assert t.buckets["2024-01-15 12:00:00"] == 2
    assert t.buckets["2024-01-15 12:01:00"] == 1


def test_ignore_case():
    lines = ["2024-01-15 12:00:01 error something\n"]
    t = build_pivot(lines, pattern="ERROR", ignore_case=True)
    assert t.total_matched == 1


def test_no_timestamp_lines_use_no_timestamp_bucket():
    lines = ["no ts line with ERROR\n"]
    t = build_pivot(lines, pattern="ERROR")
    assert t.buckets["(no timestamp)"] == 1


def test_invalid_bucket_size_raises():
    with pytest.raises(ValueError):
        build_pivot([], pattern="x", bucket_size=0)


def test_empty_input():
    t = build_pivot([], pattern="ERROR")
    assert t.total_lines == 0
    assert t.total_matched == 0
    assert len(t.buckets) == 0


# ---------------------------------------------------------------------------
# format_pivot
# ---------------------------------------------------------------------------

def test_format_pivot_header():
    t = build_pivot(LINES, pattern="ERROR")
    out = format_pivot(t)
    assert any("pivot" in row for row in out)
    assert any("matched=3" in row for row in out)


def test_format_pivot_rows_sorted():
    t = build_pivot(LINES, pattern="ERROR", bucket_size=60)
    out = format_pivot(t)
    data_rows = [r for r in out if r.startswith("2024")]
    assert len(data_rows) == 2
    assert data_rows[0] < data_rows[1]


def test_format_pivot_top_n():
    t = build_pivot(LINES, pattern="ERROR", bucket_size=60)
    out = format_pivot(t, top_n=1)
    data_rows = [r for r in out if r.startswith("2024")]
    assert len(data_rows) == 1
    # The busiest bucket (count=2) should be the one kept
    assert "12:00:00" in data_rows[0]
