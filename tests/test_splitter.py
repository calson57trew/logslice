"""Tests for logslice.splitter."""
import pytest
from logslice.splitter import split_by_size, split_by_pattern, chunk_count


LINES = [f"line {i}\n" for i in range(10)]


# --- split_by_size ---

def test_split_by_size_even():
    chunks = list(split_by_size(LINES, 5))
    assert len(chunks) == 2
    assert chunks[0] == LINES[:5]
    assert chunks[1] == LINES[5:]


def test_split_by_size_partial_last_chunk():
    chunks = list(split_by_size(LINES, 3))
    assert len(chunks) == 4
    assert len(chunks[-1]) == 1


def test_split_by_size_larger_than_input():
    chunks = list(split_by_size(LINES, 100))
    assert chunks == [LINES]


def test_split_by_size_invalid_raises():
    with pytest.raises(ValueError):
        list(split_by_size(LINES, 0))


def test_split_by_size_empty_input():
    assert list(split_by_size([], 5)) == []


# --- split_by_pattern ---

def test_split_by_pattern_basic():
    lines = ["START a\n", "detail\n", "START b\n", "more\n"]
    chunks = list(split_by_pattern(lines, r"^START"))
    assert len(chunks) == 2
    assert chunks[0] == ["START a\n", "detail\n"]
    assert chunks[1] == ["START b\n", "more\n"]


def test_split_by_pattern_leading_non_matching():
    lines = ["preamble\n", "START x\n", "body\n"]
    chunks = list(split_by_pattern(lines, r"^START"))
    assert chunks[0] == ["preamble\n"]
    assert chunks[1] == ["START x\n", "body\n"]


def test_split_by_pattern_no_match_single_chunk():
    chunks = list(split_by_pattern(LINES, r"^NOMATCH"))
    assert chunks == [LINES]


def test_split_by_pattern_case_insensitive():
    lines = ["error: bad\n", "info: ok\n", "ERROR: worse\n"]
    chunks = list(split_by_pattern(lines, r"^error"))
    assert len(chunks) == 2


# --- chunk_count ---

def test_chunk_count_exact():
    assert chunk_count(LINES, 5) == 2


def test_chunk_count_partial():
    assert chunk_count(LINES, 3) == 4


def test_chunk_count_invalid_raises():
    with pytest.raises(ValueError):
        chunk_count(LINES, 0)
