"""Tests for logslice.pattern_counter and logslice.pattern_counter_cli."""
from __future__ import annotations

import argparse
import io
import pytest

from logslice.pattern_counter import (
    compile_patterns,
    count_patterns,
    format_pattern_counts,
    PatternCountResult,
)
from logslice.pattern_counter_cli import add_pattern_count_args, apply_pattern_count


SAMPLE = [
    "2024-01-01 10:00:00 ERROR something broke\n",
    "2024-01-01 10:00:01 INFO  all good\n",
    "2024-01-01 10:00:02 ERROR another failure\n",
    "2024-01-01 10:00:03 WARN  watch out\n",
]


# ---------------------------------------------------------------------------
# compile_patterns
# ---------------------------------------------------------------------------

def test_compile_patterns_returns_pairs():
    pairs = compile_patterns(["ERROR", "WARN"])
    assert len(pairs) == 2
    assert pairs[0][0] == "ERROR"
    assert pairs[1][0] == "WARN"


def test_compile_patterns_invalid_regex_raises():
    with pytest.raises(ValueError, match="Invalid pattern"):
        compile_patterns(["[unclosed"])


def test_compile_patterns_ignore_case():
    pairs = compile_patterns(["error"], ignore_case=True)
    _, regex = pairs[0]
    assert regex.search("ERROR line")


# ---------------------------------------------------------------------------
# count_patterns
# ---------------------------------------------------------------------------

def test_count_total_lines():
    result = count_patterns(SAMPLE, ["ERROR"])
    assert result.total_lines == 4


def test_count_matched_lines():
    result = count_patterns(SAMPLE, ["ERROR"])
    assert result.matched_lines == 2


def test_count_per_pattern():
    result = count_patterns(SAMPLE, ["ERROR", "WARN"])
    counts = {pc.pattern: pc.count for pc in result.counts}
    assert counts["ERROR"] == 2
    assert counts["WARN"] == 1


def test_count_no_match_is_zero():
    result = count_patterns(SAMPLE, ["CRITICAL"])
    assert result.counts[0].count == 0


def test_count_example_captured():
    result = count_patterns(SAMPLE, ["ERROR"])
    pc = result.counts[0]
    assert pc.example is not None
    assert "ERROR" in pc.example


def test_count_example_none_when_no_match():
    result = count_patterns(SAMPLE, ["CRITICAL"])
    assert result.counts[0].example is None


def test_count_ignore_case():
    lines = ["error occurred\n", "all fine\n"]
    result = count_patterns(lines, ["ERROR"], ignore_case=True)
    assert result.counts[0].count == 1


# ---------------------------------------------------------------------------
# format_pattern_counts
# ---------------------------------------------------------------------------

def test_format_contains_totals():
    result = count_patterns(SAMPLE, ["ERROR"])
    text = format_pattern_counts(result)
    assert "Total lines" in text
    assert "Matched lines" in text


def test_format_shows_example_when_requested():
    result = count_patterns(SAMPLE, ["ERROR"])
    text = format_pattern_counts(result, show_examples=True)
    assert "example:" in text


def test_format_hides_example_by_default():
    result = count_patterns(SAMPLE, ["ERROR"])
    text = format_pattern_counts(result, show_examples=False)
    assert "example:" not in text


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    ns = argparse.Namespace(
        count_patterns=[],
        count_ignore_case=False,
        count_examples=False,
        count_only=False,
    )
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_pattern_count_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_pattern_count_args(parser)
    args = parser.parse_args(["--count-pattern", "ERROR", "--count-ignore-case"])
    assert args.count_patterns == ["ERROR"]
    assert args.count_ignore_case is True


def test_no_patterns_passthrough():
    args = make_args()
    lines = list(SAMPLE)
    result = apply_pattern_count(args, lines, out=io.StringIO())
    assert result is lines


def test_apply_writes_report_to_out():
    args = make_args(count_patterns=["ERROR"])
    out = io.StringIO()
    apply_pattern_count(args, list(SAMPLE), out=out)
    assert "ERROR" in out.getvalue()


def test_apply_count_only_returns_empty():
    args = make_args(count_patterns=["ERROR"], count_only=True)
    result = apply_pattern_count(args, list(SAMPLE), out=io.StringIO())
    assert result == []


def test_apply_normal_returns_original_lines():
    args = make_args(count_patterns=["ERROR"])
    lines = list(SAMPLE)
    result = apply_pattern_count(args, lines, out=io.StringIO())
    assert result == lines
