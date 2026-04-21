"""Tests for logslice.grouper_cli."""

from __future__ import annotations

import argparse
import sys

import pytest

from logslice.grouper_cli import add_group_args, apply_grouping

ERROR_LINE = "2024-01-15T10:05:00 ERROR something broke\n"
WARN_LINE  = "2024-01-15T11:20:00 WARN disk full\n"
INFO_LINE  = "2024-01-15T10:55:00 INFO all good\n"


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "group_rules": [],
        "group_by_hour": False,
        "group_multi": False,
        "group_summary": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_group_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_group_args(parser)
    args = parser.parse_args([])
    assert args.group_rules == []
    assert args.group_by_hour is False
    assert args.group_multi is False
    assert args.group_summary is False


def test_no_flags_passthrough():
    lines = [ERROR_LINE, INFO_LINE]
    args = make_args()
    result = apply_grouping(args, lines)
    assert result == lines


def test_pattern_group_returns_sorted_groups(capsys):
    args = make_args(group_rules=["ERROR:errors", "WARN:warnings"])
    result = apply_grouping(args, [WARN_LINE, ERROR_LINE, INFO_LINE])
    # errors group comes before warnings alphabetically
    assert result.index(ERROR_LINE) < result.index(WARN_LINE)
    assert INFO_LINE in result  # ungrouped appended last
    assert result.index(WARN_LINE) < result.index(INFO_LINE)


def test_group_by_hour_buckets(capsys):
    args = make_args(group_by_hour=True)
    result = apply_grouping(args, [ERROR_LINE, WARN_LINE, INFO_LINE])
    # All lines returned (no summary-only mode)
    assert len(result) == 3
    captured = capsys.readouterr()
    assert "2024-01-15 10" in captured.err
    assert "2024-01-15 11" in captured.err


def test_group_summary_returns_empty_lines(capsys):
    args = make_args(group_rules=["ERROR:errors"], group_summary=True)
    result = apply_grouping(args, [ERROR_LINE, INFO_LINE])
    assert result == []
    captured = capsys.readouterr()
    assert "errors" in captured.err


def test_invalid_rule_raises():
    args = make_args(group_rules=["BADSPEC"])
    with pytest.raises(ValueError, match="PATTERN:LABEL"):
        apply_grouping(args, [ERROR_LINE])


def test_stderr_counts_printed(capsys):
    args = make_args(group_rules=["ERROR:errors"])
    apply_grouping(args, [ERROR_LINE, ERROR_LINE, INFO_LINE])
    captured = capsys.readouterr()
    assert "errors: 2" in captured.err
    assert "(ungrouped): 1" in captured.err
