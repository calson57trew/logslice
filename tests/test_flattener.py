"""Tests for logslice.flattener."""
from __future__ import annotations

import pytest

from logslice.flattener import flatten_lines, count_flattened, is_continuation


TS = "2024-01-15T10:00:00 "
TS2 = "2024-01-15T10:00:01 "


def _lines(*args: str) -> list[str]:
    return list(args)


# ---------------------------------------------------------------------------
# is_continuation
# ---------------------------------------------------------------------------

def test_is_continuation_plain_text():
    assert is_continuation("    at com.example.Foo(Foo.java:42)\n") is True


def test_is_continuation_timestamped_line():
    assert is_continuation(f"{TS}INFO something\n") is False


# ---------------------------------------------------------------------------
# flatten_lines
# ---------------------------------------------------------------------------

def test_single_line_unchanged():
    src = [f"{TS}INFO hello\n"]
    result = list(flatten_lines(src))
    assert result == [f"{TS}INFO hello\n"]


def test_continuation_merged_with_parent():
    src = [
        f"{TS}ERROR boom\n",
        "    at stackframe\n",
    ]
    result = list(flatten_lines(src))
    assert len(result) == 1
    assert "ERROR boom" in result[0]
    assert "at stackframe" in result[0]


def test_multiple_continuations_all_merged():
    src = [
        f"{TS}ERROR boom\n",
        "    line 1\n",
        "    line 2\n",
        "    line 3\n",
    ]
    result = list(flatten_lines(src))
    assert len(result) == 1
    assert result[0].count(" | ") == 3


def test_two_entries_emitted_separately():
    src = [
        f"{TS}INFO first\n",
        f"{TS2}INFO second\n",
    ]
    result = list(flatten_lines(src))
    assert len(result) == 2


def test_custom_separator():
    src = [
        f"{TS}WARN msg\n",
        "continuation\n",
    ]
    result = list(flatten_lines(src, sep=" ## "))
    assert " ## " in result[0]


def test_output_always_ends_with_newline():
    src = [f"{TS}INFO no-newline"]
    result = list(flatten_lines(src))
    assert result[0].endswith("\n")


def test_empty_input_yields_nothing():
    assert list(flatten_lines([])) == []


# ---------------------------------------------------------------------------
# count_flattened
# ---------------------------------------------------------------------------

def test_count_flattened_basic():
    src = [
        f"{TS}ERROR boom\n",
        "    at frame1\n",
        "    at frame2\n",
        f"{TS2}INFO ok\n",
    ]
    stats = count_flattened(src)
    assert stats["input_lines"] == 4
    assert stats["output_lines"] == 2
    assert stats["merged_lines"] == 2


def test_count_flattened_no_continuations():
    src = [f"{TS}INFO a\n", f"{TS2}INFO b\n"]
    stats = count_flattened(src)
    assert stats["merged_lines"] == 0
    assert stats["output_lines"] == 2
