"""Tests for logslice.alerter."""

from __future__ import annotations

import pytest

from logslice.alerter import (
    AlertEvent,
    AlertRule,
    alert_lines,
    compile_alert_rules,
    count_alerts,
)


# ---------------------------------------------------------------------------
# compile_alert_rules
# ---------------------------------------------------------------------------

def test_compile_alert_rules_returns_list():
    rules = compile_alert_rules([("ERROR", "err", 1)])
    assert len(rules) == 1
    assert isinstance(rules[0], AlertRule)


def test_compile_alert_rules_ignore_case():
    rules = compile_alert_rules([("error", "err", 1)], ignore_case=True)
    assert rules[0].pattern.search("ERROR found")


def test_compile_alert_rules_case_sensitive_by_default():
    rules = compile_alert_rules([("error", "err", 1)])
    assert rules[0].pattern.search("error found")
    assert not rules[0].pattern.search("ERROR found")


# ---------------------------------------------------------------------------
# alert_lines
# ---------------------------------------------------------------------------

def _lines(*items):
    return [f"{l}\n" for l in items]


def test_no_match_yields_no_events():
    rules = compile_alert_rules([("CRITICAL", "crit", 1)])
    results = list(alert_lines(_lines("INFO ok", "DEBUG fine"), rules))
    events = [e for _, e in results]
    assert all(e is None for e in events)


def test_single_match_fires_immediately_at_threshold_one():
    rules = compile_alert_rules([("ERROR", "err", 1)])
    results = list(alert_lines(_lines("INFO ok", "ERROR bad", "INFO ok"), rules))
    events = [e for _, e in results]
    assert events[0] is None
    assert isinstance(events[1], AlertEvent)
    assert events[1].label == "err"
    assert events[2] is None


def test_threshold_two_fires_on_second_match():
    rules = compile_alert_rules([("ERROR", "err", 2)])
    results = list(alert_lines(_lines("ERROR first", "ERROR second", "ERROR third"), rules))
    events = [e for _, e in results]
    assert events[0] is None          # first match — not yet at threshold
    assert isinstance(events[1], AlertEvent)  # second match fires
    assert events[1].count == 2
    assert events[2] is None          # counter reset; needs 2 more


def test_count_resets_after_firing():
    rules = compile_alert_rules([("WARN", "w", 2)])
    lines = _lines("WARN a", "WARN b", "WARN c", "WARN d")
    results = list(alert_lines(lines, rules))
    fired = [i for i, (_, e) in enumerate(results) if e is not None]
    assert fired == [1, 3]  # fires at index 1 and 3


def test_first_matching_rule_wins():
    rules = compile_alert_rules([("ERROR", "err", 1), ("ERROR", "err2", 1)])
    results = list(alert_lines(_lines("ERROR boom"), rules))
    _, event = results[0]
    assert event is not None
    assert event.label == "err"  # first rule wins


def test_original_lines_always_yielded():
    rules = compile_alert_rules([("ERROR", "err", 1)])
    input_lines = _lines("INFO ok", "ERROR bad", "INFO ok")
    output_lines = [line for line, _ in alert_lines(input_lines, rules)]
    assert output_lines == input_lines


def test_count_alerts_counts_non_none():
    events = [None, AlertEvent("x", "line", 1), None, AlertEvent("y", "line2", 2)]
    assert count_alerts(events) == 2


def test_event_carries_timestamp():
    rules = compile_alert_rules([("ERROR", "err", 1)])
    line = "2024-01-15T10:00:00 ERROR something failed\n"
    results = list(alert_lines([line], rules))
    _, event = results[0]
    assert event is not None
    assert event.timestamp == "2024-01-15T10:00:00"
