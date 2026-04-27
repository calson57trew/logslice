"""Tests for logslice.heatmap_cli."""
from __future__ import annotations

import argparse
import io

import pytest

from logslice.heatmap_cli import add_heatmap_args, apply_heatmap


LINES = [
    "2024-03-15T14:37:01 INFO  alpha\n",
    "2024-03-15T14:37:55 ERROR beta\n",
    "2024-03-15T14:38:10 INFO  gamma\n",
]


def make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        heatmap=False,
        heatmap_bucket="minute",
        heatmap_pattern=None,
        heatmap_width=40,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_heatmap_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_heatmap_args(parser)
    args = parser.parse_args(["--heatmap", "--heatmap-bucket", "hour"])
    assert args.heatmap is True
    assert args.heatmap_bucket == "hour"


def test_add_heatmap_args_defaults():
    parser = argparse.ArgumentParser()
    add_heatmap_args(parser)
    args = parser.parse_args([])
    assert args.heatmap is False
    assert args.heatmap_bucket == "minute"
    assert args.heatmap_pattern is None
    assert args.heatmap_width == 40


def test_no_flag_passthrough():
    args = make_args(heatmap=False)
    result = apply_heatmap(args, LINES)
    assert result is LINES


def test_heatmap_writes_output_and_returns_empty():
    args = make_args(heatmap=True)
    out = io.StringIO()
    result = apply_heatmap(args, LINES, out=out)
    assert result == []
    output = out.getvalue()
    assert "14:37" in output
    assert "14:38" in output


def test_heatmap_hour_bucket():
    args = make_args(heatmap=True, heatmap_bucket="hour")
    out = io.StringIO()
    apply_heatmap(args, LINES, out=out)
    output = out.getvalue()
    assert "2024-03-15T14" in output


def test_heatmap_pattern_filters():
    args = make_args(heatmap=True, heatmap_pattern="ERROR")
    out = io.StringIO()
    apply_heatmap(args, LINES, out=out)
    output = out.getvalue()
    # 14:37 bucket should show count 1 (only ERROR line), 14:38 absent
    assert "14:37" in output
    assert "14:38" not in output
