"""Tests for logslice.indexer."""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from logslice.indexer import (
    IndexEntry,
    LogIndex,
    build_index,
    count_indexed,
    load_index,
    save_index,
    seek_to_timestamp,
)


LOG_LINES = [
    "2024-01-01T10:00:00 INFO  starting up\n",
    "continuation line with no timestamp\n",
    "2024-01-01T10:01:00 ERROR something failed\n",
    "2024-01-01T10:02:00 INFO  recovered\n",
]


@pytest.fixture()
def log_file(tmp_path):
    p = tmp_path / "test.log"
    p.write_text("".join(LOG_LINES), encoding="utf-8")
    return str(p)


def test_build_index_entry_count(log_file):
    index = build_index(log_file)
    assert len(index) == 4


def test_build_index_first_offset_is_zero(log_file):
    index = build_index(log_file)
    assert index.entries[0].offset == 0


def test_build_index_timed_entries(log_file):
    index = build_index(log_file)
    timed = index.timed_entries()
    assert len(timed) == 3


def test_build_index_untimed_entry_has_none_timestamp(log_file):
    index = build_index(log_file)
    assert index.entries[1].timestamp is None


def test_build_index_line_numbers(log_file):
    index = build_index(log_file)
    assert [e.line_number for e in index.entries] == [0, 1, 2, 3]


def test_save_and_load_roundtrip(log_file, tmp_path):
    index = build_index(log_file)
    idx_path = str(tmp_path / "test.idx")
    save_index(index, idx_path)
    loaded = load_index(idx_path)
    assert len(loaded) == len(index)
    assert loaded.entries[0].offset == index.entries[0].offset
    assert loaded.entries[2].timestamp == index.entries[2].timestamp


def test_load_invalid_json_type(tmp_path):
    p = tmp_path / "bad.idx"
    p.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    with pytest.raises(ValueError, match="JSON array"):
        load_index(str(p))


def test_seek_returns_first_matching_offset(log_file):
    index = build_index(log_file)
    offset = seek_to_timestamp(index, "2024-01-01T10:01:00")
    assert offset is not None
    # Byte offset of third line
    expected = sum(len(line.encode()) for line in LOG_LINES[:2])
    assert offset == expected


def test_seek_no_match_returns_none(log_file):
    index = build_index(log_file)
    assert seek_to_timestamp(index, "2099-01-01T00:00:00") is None


def test_count_indexed(log_file):
    index = build_index(log_file)
    stats = count_indexed(index)
    assert stats["total"] == 4
    assert stats["timed"] == 3
    assert stats["untimed"] == 1
