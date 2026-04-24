"""Tests for logslice/pivot_cli.py"""

import argparse
import io

import pytest

from logslice.pivot_cli import add_pivot_args, apply_pivot


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    defaults = dict(
        pivot_pattern=None,
        pivot_bucket=60,
        pivot_top=0,
        pivot_ignore_case=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


LINES = [
    "2024-01-15 12:00:10 ERROR disk full\n",
    "2024-01-15 12:00:45 ERROR disk full\n",
    "2024-01-15 12:01:05 INFO  all good\n",
]


# ---------------------------------------------------------------------------
# add_pivot_args
# ---------------------------------------------------------------------------

def test_add_pivot_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_pivot_args(parser)
    args = parser.parse_args([])
    assert args.pivot_pattern is None
    assert args.pivot_bucket == 60
    assert args.pivot_top == 0
    assert args.pivot_ignore_case is False


def test_add_pivot_args_custom_values():
    parser = argparse.ArgumentParser()
    add_pivot_args(parser)
    args = parser.parse_args(
        ["--pivot-pattern", "ERROR", "--pivot-bucket", "300", "--pivot-top", "5", "--pivot-ignore-case"]
    )
    assert args.pivot_pattern == "ERROR"
    assert args.pivot_bucket == 300
    assert args.pivot_top == 5
    assert args.pivot_ignore_case is True


# ---------------------------------------------------------------------------
# apply_pivot
# ---------------------------------------------------------------------------

def test_no_pattern_returns_lines_unchanged():
    args = make_args(pivot_pattern=None)
    result = apply_pivot(args, LINES)
    assert result is LINES


def test_pivot_writes_report_to_out():
    args = make_args(pivot_pattern="ERROR")
    buf = io.StringIO()
    result = apply_pivot(args, LINES, out=buf)
    report = buf.getvalue()
    assert "pivot" in report
    assert "ERROR" in report
    assert "matched=2" in report


def test_pivot_returns_original_lines():
    args = make_args(pivot_pattern="ERROR")
    buf = io.StringIO()
    result = apply_pivot(args, LINES, out=buf)
    assert result == LINES


def test_pivot_top_n_limits_rows():
    lines = [
        "2024-01-15 12:00:01 ERROR a\n",
        "2024-01-15 12:00:02 ERROR b\n",
        "2024-01-15 12:01:01 ERROR c\n",
    ]
    args = make_args(pivot_pattern="ERROR", pivot_top=1)
    buf = io.StringIO()
    apply_pivot(args, lines, out=buf)
    data_rows = [r for r in buf.getvalue().splitlines() if r.startswith("2024")]
    assert len(data_rows) == 1


def test_pivot_ignore_case_flag():
    lines = ["2024-01-15 12:00:01 error lowercase\n"]
    args = make_args(pivot_pattern="ERROR", pivot_ignore_case=True)
    buf = io.StringIO()
    apply_pivot(args, lines, out=buf)
    assert "matched=1" in buf.getvalue()
