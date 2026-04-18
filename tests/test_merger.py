"""Tests for logslice.merger."""

import pytest
from logslice.merger import merge_logs


TS_A = "2024-01-01T10:00:00 line A early\n"
TS_B = "2024-01-01T10:00:05 line B mid\n"
TS_C = "2024-01-01T10:00:10 line C late\n"
TS_D = "2024-01-01T10:00:03 line D between\n"
NO_TS = "continuation or no-timestamp line\n"


def test_merge_two_sources_sorted():
    src1 = [TS_A, TS_C]
    src2 = [TS_D, TS_B]
    result = list(merge_logs([src1, src2], sort=True))
    lines = [l.split(" ", 2)[2].strip() for l in result]
    assert lines == ["line A early", "line D between", "line B mid", "line C late"]


def test_merge_no_sort_preserves_order():
    src1 = [TS_C, TS_A]
    src2 = [TS_B]
    result = list(merge_logs([src1, src2], sort=False))
    assert result == [TS_C, TS_A, TS_B]


def test_untimed_lines_emitted_first():
    src1 = [NO_TS, TS_B]
    src2 = [TS_A]
    result = list(merge_logs([src1, src2], sort=True))
    assert result[0] == NO_TS


def test_label_prepended():
    src1 = [TS_A]
    src2 = [TS_B]
    result = list(merge_logs([src1, src2], sort=False, label=True, labels=["app", "db"]))
    assert result[0].startswith("[app] ")
    assert result[1].startswith("[db] ")


def test_default_labels_used_when_none():
    src1 = [TS_A]
    result = list(merge_logs([src1], sort=False, label=True))
    assert result[0].startswith("[source0] ")


def test_empty_sources_returns_nothing():
    assert list(merge_logs([])) == []


def test_single_source_passthrough():
    src = [TS_A, TS_B, TS_C]
    assert list(merge_logs([src], sort=True)) == [TS_A, TS_B, TS_C]


def test_all_untimed():
    src1 = ["foo\n", "bar\n"]
    src2 = ["baz\n"]
    result = list(merge_logs([src1, src2], sort=True))
    assert result == ["foo\n", "bar\n", "baz\n"]
