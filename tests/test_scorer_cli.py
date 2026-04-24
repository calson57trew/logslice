"""Tests for logslice.scorer_cli."""
import argparse
import pytest
from logslice.scorer_cli import add_score_args, apply_scoring


def make_args(**kwargs):
    defaults = {
        "score_rules": [],
        "score_threshold": 0.0,
        "score_top": None,
        "score_case_sensitive": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_score_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_score_args(parser)
    args = parser.parse_args([
        "--score", "error:2",
        "--score-threshold", "1.5",
        "--score-top", "5",
    ])
    assert args.score_rules == ["error:2"]
    assert args.score_threshold == 1.5
    assert args.score_top == 5


def test_no_rules_passthrough():
    args = make_args()
    lines = ["line one", "line two"]
    result = apply_scoring(args, lines)
    assert list(result) == lines


def test_apply_scoring_filters_by_threshold():
    args = make_args(score_rules=["error:3.0"], score_threshold=3.0)
    lines = ["INFO ok", "ERROR bad", "DEBUG verbose"]
    result = list(apply_scoring(args, lines))
    assert result == ["ERROR bad"]


def test_apply_scoring_top_n():
    args = make_args(
        score_rules=["error:2.0", "critical:5.0"],
        score_top=1,
    )
    lines = ["INFO ok", "ERROR bad", "CRITICAL meltdown"]
    result = list(apply_scoring(args, lines))
    assert len(result) == 1
    assert "CRITICAL" in result[0]


def test_apply_scoring_case_sensitive():
    args = make_args(
        score_rules=["error:2.0"],
        score_threshold=1.0,
        score_case_sensitive=True,
    )
    lines = ["ERROR uppercase", "error lowercase"]
    result = list(apply_scoring(args, lines))
    # Only lowercase 'error' matches the case-sensitive pattern
    assert result == ["error lowercase"]


def test_apply_scoring_multiple_rules_accumulate():
    args = make_args(
        score_rules=["warn:1.0", "disk:1.5"],
        score_threshold=2.0,
    )
    lines = ["WARN disk full", "WARN memory ok", "INFO disk io"]
    result = list(apply_scoring(args, lines))
    assert result == ["WARN disk full"]  # score 2.5 >= 2.0
