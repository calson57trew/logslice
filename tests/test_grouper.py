"""Tests for logslice.grouper."""

from __future__ import annotations

import pytest

from logslice.grouper import (
    GroupResult,
    compile_group_rules,
    count_grouped,
    group_by_hour,
    group_by_pattern,
)

ERROR_LINE = "2024-01-15T10:05:00 ERROR something broke\n"
WARN_LINE  = "2024-01-15T11:20:00 WARN disk full\n"
INFO_LINE  = "2024-01-15T10:55:00 INFO all good\n"
NOTS_LINE  = "no timestamp here\n"


@pytest.fixture()
def rules():
    return compile_group_rules([(r"ERROR", "errors"), (r"WARN", "warnings")])


def test_compile_group_rules_returns_pairs(rules):
    assert len(rules) == 2
    label_names = [label for _, label in rules]
    assert label_names == ["errors", "warnings"]


def test_group_by_pattern_single_match(rules):
    result = group_by_pattern([ERROR_LINE, WARN_LINE, INFO_LINE], rules)
    assert ERROR_LINE in result.groups["errors"]
    assert WARN_LINE in result.groups["warnings"]
    assert INFO_LINE in result.ungrouped


def test_group_by_pattern_first_match_only(rules):
    both = "2024-01-15T10:00:00 ERROR WARN both\n"
    result = group_by_pattern([both], rules, multi=False)
    assert both in result.groups["errors"]
    assert both not in result.groups.get("warnings", [])


def test_group_by_pattern_multi(rules):
    both = "2024-01-15T10:00:00 ERROR WARN both\n"
    result = group_by_pattern([both], rules, multi=True)
    assert both in result.groups["errors"]
    assert both in result.groups["warnings"]


def test_group_by_pattern_no_rules():
    result = group_by_pattern([ERROR_LINE, INFO_LINE], [])
    assert result.ungrouped == [ERROR_LINE, INFO_LINE]
    assert len(result.groups) == 0


def test_group_by_hour_buckets():
    lines = [ERROR_LINE, WARN_LINE, INFO_LINE]
    result = group_by_hour(lines)
    assert "2024-01-15 10" in result.groups
    assert "2024-01-15 11" in result.groups
    assert len(result.groups["2024-01-15 10"]) == 2  # ERROR + INFO
    assert len(result.groups["2024-01-15 11"]) == 1  # WARN


def test_group_by_hour_no_timestamp_goes_ungrouped():
    result = group_by_hour([NOTS_LINE])
    assert NOTS_LINE in result.ungrouped
    assert len(result.groups) == 0


def test_count_grouped_includes_ungrouped(rules):
    result = group_by_pattern([ERROR_LINE, NOTS_LINE], rules)
    counts = count_grouped(result)
    assert counts["errors"] == 1
    assert counts["(ungrouped)"] == 1


def test_count_grouped_no_ungrouped(rules):
    result = group_by_pattern([ERROR_LINE], rules)
    counts = count_grouped(result)
    assert "(ungrouped)" not in counts


def test_compile_group_rules_ignore_case():
    compiled = compile_group_rules([(r"error", "errors")], ignore_case=True)
    result = group_by_pattern([ERROR_LINE], compiled)
    assert ERROR_LINE in result.groups["errors"]
