"""Tests for logslice.histogram."""
from __future__ import annotations

import re

import pytest

from logslice.histogram import (
    HistogramResult,
    _extract_key,
    build_histogram,
    format_histogram,
)


# ---------------------------------------------------------------------------
# _extract_key
# ---------------------------------------------------------------------------

def test_extract_key_level_error():
    assert _extract_key("2024-01-01 ERROR something", None) == "ERROR"


def test_extract_key_level_warning():
    assert _extract_key("WARNING: disk full", None) == "WARNING"


def test_extract_key_no_level_returns_none():
    assert _extract_key("just a plain line", None) is None


def test_extract_key_custom_pattern():
    pat = re.compile(r"(user_\w+)")
    assert _extract_key("login by user_alice ok", pat) == "user_alice"


def test_extract_key_custom_pattern_no_match_returns_none():
    pat = re.compile(r"(user_\w+)")
    assert _extract_key("no user here", pat) is None


def test_extract_key_pattern_no_group_returns_full_match():
    pat = re.compile(r"timeout")
    assert _extract_key("connection timeout reached", pat) == "timeout"


# ---------------------------------------------------------------------------
# build_histogram
# ---------------------------------------------------------------------------

def test_total_lines():
    lines = ["ERROR x\n", "INFO y\n", "plain\n"]
    r = build_histogram(lines)
    assert r.total == 3


def test_timed_lines_counts_matched():
    lines = ["ERROR x\n", "INFO y\n", "plain\n"]
    r = build_histogram(lines)
    # ERROR + INFO are matched; plain goes to (other)
    assert r.timed == 2


def test_buckets_accumulate():
    lines = ["ERROR a\n", "ERROR b\n", "INFO c\n"]
    r = build_histogram(lines)
    assert r.buckets["ERROR"] == 2
    assert r.buckets["INFO"] == 1


def test_other_bucket_included_by_default():
    lines = ["plain line\n"]
    r = build_histogram(lines)
    assert r.buckets["(other)"] == 1


def test_other_bucket_excluded_when_flag_off():
    lines = ["plain line\n"]
    r = build_histogram(lines, bucket_other=False)
    assert "(other)" not in r.buckets


def test_empty_input_returns_empty_result():
    r = build_histogram([])
    assert r.total == 0
    assert len(r.buckets) == 0


# ---------------------------------------------------------------------------
# format_histogram
# ---------------------------------------------------------------------------

def test_format_no_data_returns_placeholder():
    r = HistogramResult()
    out = format_histogram(r)
    assert out == ["(no data)\n"]


def test_format_contains_key_name():
    lines = ["ERROR x\n", "ERROR y\n"]
    r = build_histogram(lines, bucket_other=False)
    out = format_histogram(r)
    assert any("ERROR" in row for row in out)


def test_format_bar_uses_hashes():
    lines = ["ERROR x\n"]
    r = build_histogram(lines, bucket_other=False)
    out = format_histogram(r, bar_width=10)
    assert "##########" in out[0]


def test_format_count_shown_by_default():
    lines = ["INFO a\n", "INFO b\n"]
    r = build_histogram(lines, bucket_other=False)
    out = format_histogram(r)
    assert "2" in out[0]


def test_format_count_hidden_when_flag_off():
    lines = ["INFO a\n"]
    r = build_histogram(lines, bucket_other=False)
    out = format_histogram(r, show_count=False)
    # Count suffix "  1" should not appear
    assert "  1" not in out[0]
