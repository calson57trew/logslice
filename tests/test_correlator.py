"""Tests for logslice.correlator."""

from __future__ import annotations

import io
import re
import types

import pytest

from logslice.correlator import (
    compile_id_pattern,
    correlate_lines,
    count_correlated,
    extract_id,
    format_correlation,
)
from logslice.correlator_cli import add_correlate_args, apply_correlation


REQ_PATTERN = re.compile(r"req-id=(\w+)")

LINES = [
    "2024-01-01T00:00:01Z req-id=abc GET /api\n",
    "2024-01-01T00:00:02Z req-id=abc 200 OK\n",
    "2024-01-01T00:00:03Z req-id=xyz POST /upload\n",
    "2024-01-01T00:00:04Z req-id=xyz 500 Error\n",
    "2024-01-01T00:00:05Z heartbeat\n",
]


# --- compile_id_pattern ---

def test_compile_valid_pattern():
    p = compile_id_pattern(r"id=(\w+)")
    assert isinstance(p, re.Pattern)


def test_compile_no_group_raises():
    with pytest.raises(ValueError, match="capturing group"):
        compile_id_pattern(r"id=\w+")


def test_compile_invalid_regex_raises():
    with pytest.raises(ValueError, match="Invalid correlation pattern"):
        compile_id_pattern(r"[unclosed")


# --- extract_id ---

def test_extract_id_found():
    line = "req-id=abc GET /api\n"
    assert extract_id(line, REQ_PATTERN) == "abc"


def test_extract_id_not_found():
    assert extract_id("heartbeat\n", REQ_PATTERN) is None


# --- correlate_lines ---

def test_correlate_groups_by_id():
    groups = correlate_lines(LINES, REQ_PATTERN)
    assert set(groups.keys()) == {"abc", "xyz"}
    assert len(groups["abc"].lines) == 2
    assert len(groups["xyz"].lines) == 2


def test_correlate_unmatched_excluded_by_default():
    groups = correlate_lines(LINES, REQ_PATTERN)
    assert "__unmatched__" not in groups


def test_correlate_unmatched_included():
    groups = correlate_lines(LINES, REQ_PATTERN, include_unmatched=True)
    assert "__unmatched__" in groups
    assert groups["__unmatched__"].lines == ["2024-01-01T00:00:05Z heartbeat\n"]


# --- count_correlated ---

def test_count_correlated():
    groups = correlate_lines(LINES, REQ_PATTERN)
    n_groups, n_lines = count_correlated(groups)
    assert n_groups == 2
    assert n_lines == 4


# --- format_correlation ---

def test_format_correlation_contains_keys():
    groups = correlate_lines(LINES, REQ_PATTERN)
    rendered = format_correlation(groups)
    header_lines = [l for l in rendered if l.startswith("===")]
    assert len(header_lines) == 2
    assert any("abc" in h for h in header_lines)
    assert any("xyz" in h for h in header_lines)


# --- apply_correlation (CLI) ---

def _make_args(**kwargs):
    defaults = {
        "correlate_id": None,
        "correlate_key": None,
        "correlate_unmatched": False,
        "correlate_report": False,
    }
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_no_pattern_passthrough():
    args = _make_args()
    result = apply_correlation(args, LINES[:])
    assert result == LINES


def test_filter_by_key():
    args = _make_args(correlate_id=r"req-id=(\w+)", correlate_key="abc")
    result = apply_correlation(args, LINES[:])
    assert all("req-id=abc" in l for l in result)
    assert len(result) == 2


def test_filter_missing_key_returns_empty():
    args = _make_args(correlate_id=r"req-id=(\w+)", correlate_key="nope")
    assert apply_correlation(args, LINES[:]) == []


def test_report_writes_to_out_and_returns_empty():
    args = _make_args(correlate_id=r"req-id=(\w+)", correlate_report=True)
    buf = io.StringIO()
    result = apply_correlation(args, LINES[:], out=buf)
    assert result == []
    output = buf.getvalue()
    assert "abc" in output
    assert "xyz" in output
