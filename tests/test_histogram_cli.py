"""Tests for logslice.histogram_cli."""
from __future__ import annotations

import argparse
import io

import pytest

from logslice.histogram_cli import add_histogram_args, apply_histogram


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "histogram": None,
        "histogram_bar_width": 40,
        "histogram_no_other": False,
        "histogram_only": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


_LINES = [
    "2024-01-01 ERROR something bad\n",
    "2024-01-01 INFO all good\n",
    "2024-01-01 ERROR again\n",
    "plain continuation\n",
]


def test_add_histogram_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_histogram_args(parser)
    args = parser.parse_args(["--histogram"])
    assert args.histogram == ""


def test_add_histogram_args_defaults():
    parser = argparse.ArgumentParser()
    add_histogram_args(parser)
    args = parser.parse_args([])
    assert args.histogram is None
    assert args.histogram_bar_width == 40
    assert not args.histogram_no_other
    assert not args.histogram_only


def test_no_flag_passthrough():
    args = make_args(histogram=None)
    result = apply_histogram(args, _LINES, out=io.StringIO())
    assert result is _LINES


def test_histogram_writes_output():
    buf = io.StringIO()
    args = make_args(histogram="")
    apply_histogram(args, _LINES, out=buf)
    output = buf.getvalue()
    assert "ERROR" in output
    assert "INFO" in output


def test_histogram_only_returns_empty():
    buf = io.StringIO()
    args = make_args(histogram="", histogram_only=True)
    result = apply_histogram(args, _LINES, out=buf)
    assert result == []


def test_histogram_not_only_returns_lines():
    buf = io.StringIO()
    args = make_args(histogram="", histogram_only=False)
    result = apply_histogram(args, _LINES, out=buf)
    assert result is _LINES


def test_histogram_no_other_omits_unmatched():
    buf = io.StringIO()
    args = make_args(histogram="", histogram_no_other=True)
    apply_histogram(args, _LINES, out=buf)
    assert "(other)" not in buf.getvalue()


def test_histogram_custom_pattern():
    buf = io.StringIO()
    args = make_args(histogram=r"(ERROR|INFO)")
    apply_histogram(args, _LINES, out=buf)
    assert "ERROR" in buf.getvalue()


def test_histogram_invalid_pattern_raises():
    buf = io.StringIO()
    args = make_args(histogram="[invalid")
    with pytest.raises(ValueError, match="Invalid histogram pattern"):
        apply_histogram(args, _LINES, out=buf)
