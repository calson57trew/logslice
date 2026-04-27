"""Tests for logslice.deduplicator_cli."""
from __future__ import annotations

import argparse
import io
from typing import List

import pytest

from logslice.deduplicator_cli import add_dedup_args, apply_deduplication


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"dedup": False, "dedup_consecutive": False, "dedup_summary": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _lines(*items: str) -> List[str]:
    return [f"{item}\n" for item in items]


# ---------------------------------------------------------------------------
# add_dedup_args
# ---------------------------------------------------------------------------

def test_add_dedup_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_dedup_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "dedup")
    assert hasattr(args, "dedup_consecutive")
    assert hasattr(args, "dedup_summary")


def test_add_dedup_args_defaults_are_false():
    parser = argparse.ArgumentParser()
    add_dedup_args(parser)
    args = parser.parse_args([])
    assert args.dedup is False
    assert args.dedup_consecutive is False
    assert args.dedup_summary is False


# ---------------------------------------------------------------------------
# apply_deduplication — passthrough
# ---------------------------------------------------------------------------

def test_no_flags_returns_lines_unchanged():
    original = _lines("a", "b", "a")
    result = apply_deduplication(make_args(), original)
    assert result == original


# ---------------------------------------------------------------------------
# apply_deduplication — global dedup
# ---------------------------------------------------------------------------

def test_dedup_removes_global_duplicates():
    lines = _lines("a", "b", "a", "c", "b")
    result = apply_deduplication(make_args(dedup=True), lines)
    assert result.count("a\n") == 1
    assert result.count("b\n") == 1
    assert result.count("c\n") == 1


# ---------------------------------------------------------------------------
# apply_deduplication — consecutive dedup
# ---------------------------------------------------------------------------

def test_dedup_consecutive_keeps_non_adjacent_duplicates():
    lines = _lines("a", "a", "b", "a")
    result = apply_deduplication(make_args(dedup_consecutive=True), lines)
    # first run of "a" collapsed; second "a" (after "b") kept
    assert result == ["a\n", "b\n", "a\n"]


# ---------------------------------------------------------------------------
# apply_deduplication — summary output
# ---------------------------------------------------------------------------

def test_dedup_summary_writes_removed_count():
    lines = _lines("x", "x", "y")
    buf = io.StringIO()
    apply_deduplication(make_args(dedup=True, dedup_summary=True), lines, out=buf)
    output = buf.getvalue()
    assert "[dedup]" in output
    assert "1" in output


def test_dedup_summary_reports_mode_global():
    lines = _lines("x", "x")
    buf = io.StringIO()
    apply_deduplication(make_args(dedup=True, dedup_summary=True), lines, out=buf)
    assert "global" in buf.getvalue()


def test_dedup_summary_reports_mode_consecutive():
    lines = _lines("x", "x")
    buf = io.StringIO()
    apply_deduplication(
        make_args(dedup_consecutive=True, dedup_summary=True), lines, out=buf
    )
    assert "consecutive" in buf.getvalue()


def test_no_summary_flag_writes_nothing():
    lines = _lines("x", "x")
    buf = io.StringIO()
    apply_deduplication(make_args(dedup=True, dedup_summary=False), lines, out=buf)
    assert buf.getvalue() == ""
