"""Tests for logslice.dispatcher_cli."""

from __future__ import annotations

import argparse
import io
import pytest

from logslice.dispatcher_cli import (
    _parse_rule_entry,
    add_dispatch_args,
    apply_dispatch,
)


def make_args(**kwargs):
    defaults = {
        "dispatch_rules": [],
        "dispatch_default": None,
        "dispatch_ignore_case": False,
        "dispatch_show": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_dispatch_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_dispatch_args(parser)
    args = parser.parse_args([])
    assert args.dispatch_rules == []
    assert args.dispatch_default is None
    assert args.dispatch_ignore_case is False
    assert args.dispatch_show is None


def test_parse_rule_entry_valid():
    ch, pat = _parse_rule_entry("errors:ERROR")
    assert ch == "errors"
    assert pat == "ERROR"


def test_parse_rule_entry_pattern_with_colon():
    ch, pat = _parse_rule_entry("ts:2024-01-01:.*")
    assert ch == "ts"
    assert pat == "2024-01-01:.*"


def test_parse_rule_entry_missing_colon_raises():
    with pytest.raises(ValueError, match="expected 'channel:pattern'"):
        _parse_rule_entry("nodivider")


def test_parse_rule_entry_empty_channel_raises():
    with pytest.raises(ValueError, match="non-empty"):
        _parse_rule_entry(":pattern")


def test_no_rules_passthrough():
    lines = ["INFO hello\n", "ERROR boom\n"]
    args = make_args()
    result = apply_dispatch(args, lines, out=io.StringIO())
    assert result == lines


def test_dispatch_routes_and_returns_all_lines():
    lines = ["ERROR crash\n", "INFO ok\n"]
    args = make_args(dispatch_rules=["errors:ERROR"])
    out = io.StringIO()
    result = apply_dispatch(args, lines, out=out)
    assert result == lines  # no --dispatch-show, so all lines returned
    assert "dispatched=1" in out.getvalue()


def test_dispatch_show_filters_to_channel():
    lines = ["ERROR crash\n", "INFO ok\n", "ERROR again\n"]
    args = make_args(dispatch_rules=["errors:ERROR"], dispatch_show="errors")
    out = io.StringIO()
    result = apply_dispatch(args, lines, out=out)
    assert result == ["ERROR crash\n", "ERROR again\n"]


def test_dispatch_ignore_case_flag():
    lines = ["error lowercase\n", "INFO other\n"]
    args = make_args(
        dispatch_rules=["errs:error"],
        dispatch_ignore_case=True,
        dispatch_show="errs",
    )
    result = apply_dispatch(args, lines, out=io.StringIO())
    assert result == ["error lowercase\n"]
