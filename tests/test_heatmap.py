"""Tests for logslice.heatmap."""
from __future__ import annotations

import pytest

from logslice.heatmap import (
    HeatmapResult,
    _floor_bucket,
    build_heatmap,
    format_heatmap,
)


# ---------------------------------------------------------------------------
# _floor_bucket
# ---------------------------------------------------------------------------

def test_floor_bucket_minute():
    ts = "2024-03-15T14:37:09"
    assert _floor_bucket(ts, "minute") == "2024-03-15T14:37"


def test_floor_bucket_hour():
    ts = "2024-03-15T14:37:09"
    assert _floor_bucket(ts, "hour") == "2024-03-15T14"


def test_floor_bucket_space_separator():
    ts = "2024-03-15 14:37:09"
    assert _floor_bucket(ts, "minute") == "2024-03-15 14:37"


def test_floor_bucket_no_timestamp_returns_none():
    assert _floor_bucket("no timestamp here", "minute") is None


# ---------------------------------------------------------------------------
# build_heatmap
# ---------------------------------------------------------------------------

LINES = [
    "2024-03-15T14:37:01 INFO  request received\n",
    "2024-03-15T14:37:45 ERROR something failed\n",
    "2024-03-15T14:38:10 INFO  ok\n",
    "2024-03-15T15:00:01 INFO  new hour\n",
    "no timestamp here\n",
]


def test_total_and_timed_lines():
    r = build_heatmap(LINES)
    assert r.total_lines == 5
    assert r.timed_lines == 4


def test_minute_buckets():
    r = build_heatmap(LINES)
    assert r.buckets["2024-03-15T14:37"] == 2
    assert r.buckets["2024-03-15T14:38"] == 1
    assert r.buckets["2024-03-15T15:00"] == 1


def test_hour_buckets():
    r = build_heatmap(LINES, bucket_size="hour")
    assert r.buckets["2024-03-15T14"] == 3
    assert r.buckets["2024-03-15T15"] == 1


def test_label_pattern_filters():
    r = build_heatmap(LINES, label_pattern=r"ERROR")
    assert r.buckets.get("2024-03-15T14:37") == 1
    assert "2024-03-15T14:38" not in r.buckets


def test_invalid_bucket_size_raises():
    with pytest.raises(ValueError, match="bucket_size"):
        build_heatmap(LINES, bucket_size="second")


def test_empty_input():
    r = build_heatmap([])
    assert r.buckets == {}
    assert r.total_lines == 0


# ---------------------------------------------------------------------------
# format_heatmap
# ---------------------------------------------------------------------------

def test_format_heatmap_no_buckets():
    r = HeatmapResult()
    rows = format_heatmap(r)
    assert rows == ["(no timed lines found)\n"]


def test_format_heatmap_contains_bucket_label():
    r = build_heatmap(LINES)
    rows = format_heatmap(r)
    combined = "".join(rows)
    assert "2024-03-15T14:37" in combined


def test_format_heatmap_shows_count_by_default():
    r = build_heatmap(LINES)
    rows = format_heatmap(r)
    # The line for 14:37 has count 2
    line_37 = next(row for row in rows if "14:37" in row)
    assert "2" in line_37


def test_format_heatmap_hide_count():
    r = build_heatmap(LINES)
    rows = format_heatmap(r, show_count=False)
    line_37 = next(row for row in rows if "14:37" in row)
    # Should still have bar characters but no trailing count
    assert "|" in line_37
    assert line_37.rstrip("\n").endswith("|")
