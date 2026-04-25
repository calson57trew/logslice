"""Tests for logslice.router and logslice.router_cli."""

from __future__ import annotations

import argparse
import pytest

from logslice.router import (
    RouteRule,
    RoutedLine,
    collect_sinks,
    compile_route_rules,
    count_routed,
    route_line,
    route_lines,
)
from logslice.router_cli import add_route_args, apply_routing


# ---------------------------------------------------------------------------
# compile_route_rules
# ---------------------------------------------------------------------------

def test_compile_route_rules_returns_list():
    rules = compile_route_rules([("ERROR", "errors"), ("WARN", "warnings")])
    assert len(rules) == 2
    assert all(isinstance(r, RouteRule) for r in rules)


def test_compile_route_rules_ignore_case():
    rules = compile_route_rules([("error", "errors")], ignore_case=True)
    assert rules[0].pattern.search("2024-01-01 ERROR something")


# ---------------------------------------------------------------------------
# route_line
# ---------------------------------------------------------------------------

@pytest.fixture
def rules():
    return compile_route_rules([("ERROR", "errors"), ("WARN", "warnings")])


def test_route_line_first_match(rules):
    result = route_line("2024-01-01 ERROR boom", rules)
    assert result.sink == "errors"
    assert result.line == "2024-01-01 ERROR boom"


def test_route_line_second_rule(rules):
    result = route_line("2024-01-01 WARN low disk", rules)
    assert result.sink == "warnings"


def test_route_line_no_match_uses_default(rules):
    result = route_line("2024-01-01 INFO all good", rules)
    assert result.sink == "default"


def test_route_line_custom_default(rules):
    result = route_line("INFO ok", rules, default_sink="misc")
    assert result.sink == "misc"


# ---------------------------------------------------------------------------
# route_lines / collect_sinks / count_routed
# ---------------------------------------------------------------------------

def test_route_lines_yields_all(rules):
    lines = ["ERROR x", "WARN y", "INFO z"]
    result = list(route_lines(lines, rules))
    assert len(result) == 3


def test_collect_sinks_groups_correctly(rules):
    lines = ["ERROR a", "ERROR b", "WARN c", "INFO d"]
    routed = route_lines(lines, rules)
    sinks = collect_sinks(routed)
    assert sinks["errors"] == ["ERROR a", "ERROR b"]
    assert sinks["warnings"] == ["WARN c"]
    assert sinks["default"] == ["INFO d"]


def test_count_routed(rules):
    lines = ["ERROR a", "WARN b", "WARN c"]
    routed = route_lines(lines, rules)
    counts = count_routed(routed)
    assert counts == {"errors": 1, "warnings": 2}


# ---------------------------------------------------------------------------
# router_cli
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    defaults = dict(
        route_rules=[],
        route_default="default",
        route_ignore_case=False,
        route_show_sink=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_route_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_route_args(parser)
    args = parser.parse_args([])
    assert args.route_rules == []
    assert args.route_default == "default"
    assert args.route_ignore_case is False
    assert args.route_show_sink is False


def test_no_rules_passthrough():
    lines = ["ERROR x", "INFO y"]
    args = make_args()
    result = apply_routing(args, lines)
    assert result == lines


def test_apply_routing_routes_lines():
    lines = ["ERROR x", "INFO y"]
    args = make_args(route_rules=["ERROR:errors"])
    result = apply_routing(args, lines)
    assert result == ["ERROR x", "INFO y"]


def test_apply_routing_show_sink_prefixes():
    lines = ["ERROR x", "INFO y"]
    args = make_args(route_rules=["ERROR:errors"], route_show_sink=True)
    result = apply_routing(args, lines)
    assert result[0] == "[errors] ERROR x"
    assert result[1] == "[default] INFO y"


def test_apply_routing_bad_spec_raises():
    args = make_args(route_rules=["NO_COLON_HERE"])
    with pytest.raises(ValueError, match="PATTERN:SINK"):
        apply_routing(args, ["some line"])
