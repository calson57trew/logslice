"""Tests for logslice.chunker."""
from __future__ import annotations

import pytest

from logslice.chunker import (
    TimeChunk,
    _floor_bucket,
    chunk_by_time,
    count_chunks,
)


# ---------------------------------------------------------------------------
# _floor_bucket
# ---------------------------------------------------------------------------

def test_floor_bucket_5min_exact():
    assert _floor_bucket("2024-03-01 10:00:00", 5) == "2024-03-01 10:00"


def test_floor_bucket_5min_mid():
    assert _floor_bucket("2024-03-01 10:07:33", 5) == "2024-03-01 10:05"


def test_floor_bucket_t_separator():
    assert _floor_bucket("2024-03-01T10:13:00", 10) == "2024-03-01 10:10"


def test_floor_bucket_no_timestamp_returns_none():
    assert _floor_bucket("short", 5) is None


def test_floor_bucket_1min_granularity():
    assert _floor_bucket("2024-03-01 09:59:59", 1) == "2024-03-01 09:59"


# ---------------------------------------------------------------------------
# chunk_by_time
# ---------------------------------------------------------------------------

def _log(*entries):
    return list(entries)


def test_single_bucket():
    lines = [
        "2024-01-01 12:00:00 INFO  a\n",
        "2024-01-01 12:02:00 INFO  b\n",
        "2024-01-01 12:04:59 INFO  c\n",
    ]
    chunks = list(chunk_by_time(lines, bucket_minutes=5))
    assert len(chunks) == 1
    assert len(chunks[0]) == 3
    assert chunks[0].bucket == "2024-01-01 12:00"


def test_two_buckets():
    lines = [
        "2024-01-01 12:00:00 INFO  a\n",
        "2024-01-01 12:05:00 INFO  b\n",
    ]
    chunks = list(chunk_by_time(lines, bucket_minutes=5))
    assert len(chunks) == 2
    assert chunks[0].bucket == "2024-01-01 12:00"
    assert chunks[1].bucket == "2024-01-01 12:05"


def test_continuation_line_appended_to_current_bucket():
    lines = [
        "2024-01-01 12:01:00 ERROR oops\n",
        "    traceback line\n",
    ]
    chunks = list(chunk_by_time(lines, bucket_minutes=5))
    assert len(chunks) == 1
    assert len(chunks[0]) == 2


def test_unassigned_bucket_for_leading_continuation():
    lines = ["    no timestamp yet\n", "2024-01-01 08:00:00 INFO hi\n"]
    chunks = list(chunk_by_time(lines, bucket_minutes=5))
    assert chunks[0].bucket == "(unassigned)"
    assert len(chunks) == 2


def test_invalid_bucket_minutes_raises():
    with pytest.raises(ValueError):
        list(chunk_by_time([], bucket_minutes=0))


def test_empty_input_yields_nothing():
    assert list(chunk_by_time([], bucket_minutes=5)) == []


def test_count_chunks():
    lines = [
        "2024-01-01 00:00:00 A\n",
        "2024-01-01 00:10:00 B\n",
        "2024-01-01 00:20:00 C\n",
    ]
    assert count_chunks(lines, bucket_minutes=10) == 3
