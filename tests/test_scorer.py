"""Tests for logslice.scorer."""
import pytest
from logslice.scorer import (
    ScoredLine,
    compile_score_rules,
    count_scored,
    score_line,
    score_lines,
    top_lines,
)


@pytest.fixture()
def rules():
    return compile_score_rules([("error", 2.0), ("critical", 5.0), ("warn", 1.0)])


def test_compile_score_rules_returns_pairs(rules):
    assert len(rules) == 3


def test_score_line_no_match(rules):
    result = score_line("2024-01-01 INFO all good", rules)
    assert result.score == 0.0
    assert result.matched_terms == []


def test_score_line_single_match(rules):
    result = score_line("2024-01-01 ERROR disk full", rules)
    assert result.score == 2.0
    assert "error" in result.matched_terms[0].lower()


def test_score_line_multiple_matches(rules):
    result = score_line("CRITICAL error occurred", rules)
    assert result.score == 7.0  # 5.0 + 2.0
    assert len(result.matched_terms) == 2


def test_score_line_case_insensitive_by_default(rules):
    result = score_line("WARN something", rules)
    assert result.score == 1.0


def test_score_line_case_sensitive_no_match():
    compiled = compile_score_rules([("error", 3.0)], ignore_case=False)
    result = score_line("ERROR uppercase", compiled)
    assert result.score == 0.0


def test_score_lines_threshold_filters(rules):
    lines = [
        "INFO nothing",
        "ERROR something",
        "CRITICAL meltdown",
    ]
    results = list(score_lines(lines, rules, threshold=3.0))
    assert len(results) == 1
    assert "CRITICAL" in results[0].line


def test_score_lines_zero_threshold_includes_all(rules):
    lines = ["INFO ok", "WARN slow"]
    results = list(score_lines(lines, rules, threshold=0.0))
    assert len(results) == 2


def test_top_lines_returns_sorted_descending(rules):
    lines = ["INFO ok", "WARN slow", "CRITICAL meltdown", "ERROR bad"]
    results = top_lines(lines, rules, n=2)
    assert len(results) == 2
    assert results[0].score >= results[1].score
    assert "CRITICAL" in results[0].line


def test_top_lines_n_larger_than_input(rules):
    lines = ["ERROR a", "INFO b"]
    results = top_lines(lines, rules, n=100)
    assert len(results) == 2


def test_count_scored():
    data = [
        ScoredLine(line="a", score=0.0),
        ScoredLine(line="b", score=1.5),
        ScoredLine(line="c", score=3.0),
    ]
    counts = count_scored(data)
    assert counts["total"] == 3
    assert counts["above_zero"] == 2
    assert counts["zero"] == 1
