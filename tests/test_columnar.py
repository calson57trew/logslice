"""Tests for logslice.columnar."""
import pytest
from logslice.columnar import split_columns, format_columns, count_columns


# ---------------------------------------------------------------------------
# split_columns
# ---------------------------------------------------------------------------

def test_split_columns_whitespace_default():
    assert split_columns("2024-01-01 INFO  hello world") == ["2024-01-01", "INFO", "hello", "world"]


def test_split_columns_strips_newline():
    assert split_columns("a b c\n") == ["a", "b", "c"]


def test_split_columns_custom_delimiter():
    assert split_columns("a,b,c", delimiter=",") == ["a", "b", "c"]


def test_split_columns_max_cols_merges_overflow():
    result = split_columns("a b c d e", max_cols=3)
    assert result == ["a", "b", "c d e"]


def test_split_columns_max_cols_exact_fit():
    result = split_columns("a b c", max_cols=3)
    assert result == ["a", "b", "c"]


def test_split_columns_single_token():
    assert split_columns("onlyone") == ["onlyone"]


# ---------------------------------------------------------------------------
# format_columns
# ---------------------------------------------------------------------------

def test_format_columns_aligns_cells():
    lines = ["a bb ccc\n", "dddd e ff\n"]
    result = list(format_columns(lines))
    # first cells: 'a' padded to 4, 'bb' padded to 2
    assert result[0].startswith("a   ")
    assert result[1].startswith("dddd")


def test_format_columns_last_column_not_padded():
    lines = ["x y short\n", "x y a-much-longer-last-cell\n"]
    result = list(format_columns(lines))
    # last column should not have trailing spaces
    assert result[0].rstrip("\n").endswith("short")
    assert result[1].rstrip("\n").endswith("a-much-longer-last-cell")


def test_format_columns_custom_separator():
    lines = ["a b\n", "c d\n"]
    result = list(format_columns(lines, separator="|"))
    assert "|" in result[0]


def test_format_columns_empty_input():
    assert list(format_columns([])) == []


def test_format_columns_each_line_ends_with_newline():
    lines = ["foo bar\n", "baz qux\n"]
    for out in format_columns(lines):
        assert out.endswith("\n")


def test_format_columns_respects_max_cols():
    lines = ["a b c d\n", "e f g h\n"]
    result = list(format_columns(lines, max_cols=3))
    # each row should have exactly 3 logical columns → 2 separators
    assert result[0].count("  ") >= 2


# ---------------------------------------------------------------------------
# count_columns
# ---------------------------------------------------------------------------

def test_count_columns_basic():
    lines = ["a b c\n", "d e\n"]
    assert count_columns(lines) == 3


def test_count_columns_empty():
    assert count_columns([]) == 0


def test_count_columns_single_line():
    assert count_columns(["only\n"]) == 1


def test_count_columns_custom_delimiter():
    lines = ["a,b,c,d\n", "x,y\n"]
    assert count_columns(lines, delimiter=",") == 4
