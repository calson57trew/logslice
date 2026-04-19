"""Tests for logslice.bookmarker."""

import json
import os
import pytest

from logslice.bookmarker import (
    Bookmark,
    delete_bookmark,
    get_bookmark,
    list_bookmarks,
    load_bookmarks,
    save_bookmarks,
    set_bookmark,
)


@pytest.fixture()
def bm_file(tmp_path):
    return str(tmp_path / "bookmarks.json")


def test_load_missing_file_returns_empty(bm_file):
    assert load_bookmarks(bm_file) == {}


def test_save_and_load_roundtrip(bm_file):
    bms = {"start": Bookmark(name="start", timestamp="2024-01-01T00:00:00", line_number=5)}
    save_bookmarks(bms, bm_file)
    loaded = load_bookmarks(bm_file)
    assert "start" in loaded
    assert loaded["start"].timestamp == "2024-01-01T00:00:00"
    assert loaded["start"].line_number == 5


def test_set_bookmark_creates_entry(bm_file):
    bm = set_bookmark("mymark", timestamp="2024-06-01T12:00:00", line_number=42, path=bm_file)
    assert bm.name == "mymark"
    loaded = load_bookmarks(bm_file)
    assert "mymark" in loaded


def test_set_bookmark_overwrites_existing(bm_file):
    set_bookmark("x", timestamp="2024-01-01T00:00:00", path=bm_file)
    set_bookmark("x", timestamp="2024-06-01T00:00:00", path=bm_file)
    bm = get_bookmark("x", bm_file)
    assert bm.timestamp == "2024-06-01T00:00:00"


def test_get_bookmark_missing_returns_none(bm_file):
    assert get_bookmark("nope", bm_file) is None


def test_delete_bookmark_removes_entry(bm_file):
    set_bookmark("del_me", path=bm_file)
    removed = delete_bookmark("del_me", bm_file)
    assert removed is True
    assert get_bookmark("del_me", bm_file) is None


def test_delete_bookmark_missing_returns_false(bm_file):
    assert delete_bookmark("ghost", bm_file) is False


def test_list_bookmarks_sorted(bm_file):
    set_bookmark("zebra", path=bm_file)
    set_bookmark("alpha", path=bm_file)
    set_bookmark("middle", path=bm_file)
    names = [b.name for b in list_bookmarks(bm_file)]
    assert names == sorted(names)


def test_list_bookmarks_empty(bm_file):
    assert list_bookmarks(bm_file) == []
