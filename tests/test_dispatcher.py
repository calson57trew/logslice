"""Tests for logslice.dispatcher."""

from __future__ import annotations

import pytest
from logslice.dispatcher import (
    DispatchResult,
    compile_dispatch_rules,
    count_dispatched,
    dispatch_line,
    dispatch_lines,
    iter_channel,
)


@pytest.fixture
def rules():
    return compile_dispatch_rules(
        [("errors", r"ERROR"), ("warnings", r"WARN")]
    )


def test_compile_dispatch_rules_returns_list(rules):
    assert len(rules) == 2
    assert rules[0].channel == "errors"
    assert rules[1].channel == "warnings"


def test_compile_dispatch_rules_ignore_case():
    r = compile_dispatch_rules([("ch", r"error")], ignore_case=True)
    assert r[0].pattern.search("ERROR line") is not None


def test_dispatch_line_first_match(rules):
    assert dispatch_line("2024-01-01 ERROR boom", rules) == "errors"


def test_dispatch_line_second_rule(rules):
    assert dispatch_line("2024-01-01 WARN low disk", rules) == "warnings"


def test_dispatch_line_no_match_returns_none(rules):
    assert dispatch_line("2024-01-01 INFO all good", rules) is None


def test_dispatch_lines_routes_correctly(rules):
    lines = [
        "2024-01-01 ERROR crash\n",
        "2024-01-01 WARN memory\n",
        "2024-01-01 INFO startup\n",
    ]
    result = dispatch_lines(lines, rules)
    assert result.total == 3
    assert result.dispatched == 2
    assert result.channels["errors"] == ["2024-01-01 ERROR crash\n"]
    assert result.channels["warnings"] == ["2024-01-01 WARN memory\n"]
    assert result.default == ["2024-01-01 INFO startup\n"]


def test_dispatch_lines_default_channel(rules):
    lines = ["INFO line\n"]
    result = dispatch_lines(lines, rules, default_channel="misc")
    assert "misc" in result.channels
    assert result.default == []


def test_dispatch_lines_empty_input(rules):
    result = dispatch_lines([], rules)
    assert result.total == 0
    assert result.dispatched == 0
    assert result.default == []


def test_iter_channel_yields_lines(rules):
    lines = ["ERROR a\n", "ERROR b\n", "INFO c\n"]
    result = dispatch_lines(lines, rules)
    out = list(iter_channel(result, "errors"))
    assert out == ["ERROR a\n", "ERROR b\n"]


def test_iter_channel_missing_returns_empty(rules):
    result = dispatch_lines([], rules)
    assert list(iter_channel(result, "nonexistent")) == []


def test_count_dispatched(rules):
    lines = ["ERROR x\n", "INFO y\n"]
    result = dispatch_lines(lines, rules)
    assert count_dispatched(result) == 1


def test_all_channels_sorted():
    r = compile_dispatch_rules([("z_channel", r"Z"), ("a_channel", r"A")])
    result = dispatch_lines(["Z line\n", "A line\n"], r)
    assert result.all_channels() == ["a_channel", "z_channel"]
