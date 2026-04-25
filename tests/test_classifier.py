"""Tests for logslice.classifier."""

import pytest
from logslice.classifier import (
    builtin_rules,
    classify_line,
    classify_lines,
    compile_classify_rules,
    count_classified,
)


@pytest.fixture
def rules():
    return compile_classify_rules([
        ("error", r"ERROR"),
        ("warning", r"WARN"),
        ("info", r"INFO"),
    ])


def test_compile_classify_rules_returns_pairs(rules):
    assert len(rules) == 3
    assert rules[0][0] == "error"


def test_classify_line_first_match_only(rules):
    result = classify_line("2024-01-01 ERROR something broke", rules)
    assert result == ["error"]


def test_classify_line_no_match_returns_default(rules):
    result = classify_line("2024-01-01 DEBUG trace output", rules)
    assert result == ["unclassified"]


def test_classify_line_custom_default(rules):
    result = classify_line("nothing here", rules, default="other")
    assert result == ["other"]


def test_classify_line_multi_returns_all_matches():
    multi_rules = compile_classify_rules([
        ("error", r"ERROR"),
        ("critical", r"CRITICAL|ERROR"),
    ])
    result = classify_line("ERROR CRITICAL event", multi_rules, multi=True)
    assert "error" in result
    assert "critical" in result


def test_classify_line_empty_string_returns_default(rules):
    """An empty line should fall back to the default classification."""
    result = classify_line("", rules)
    assert result == ["unclassified"]


def test_classify_lines_no_tag_passthrough(rules):
    lines = ["INFO startup\n", "ERROR boom\n"]
    result = list(classify_lines(lines, rules, tag=False))
    assert result == lines


def test_classify_lines_tag_prepended(rules):
    lines = ["ERROR boom\n", "INFO ok\n"]
    result = list(classify_lines(lines, rules, tag=True))
    assert result[0].startswith("[error] ")
    assert result[1].startswith("[info] ")


def test_classify_lines_tag_unclassified(rules):
    lines = ["DEBUG verbose\n"]
    result = list(classify_lines(lines, rules, tag=True))
    assert result[0].startswith("[unclassified] ")


def test_classify_lines_preserves_line_content(rules):
    """Tagged lines should retain the original line content after the tag prefix."""
    line = "ERROR something went wrong\n"
    result = list(classify_lines([line], rules, tag=True))
    assert result[0] == "[error] ERROR something went wrong\n"


def test_count_classified(rules):
    lines = ["ERROR a\n", "ERROR b\n", "INFO c\n", "nothing\n"]
    counts = count_classified(lines, rules)
    assert counts["error"] == 2
    assert counts["info"] == 1
    assert counts["unclassified"] == 1


def test_count_classified_empty_input(rules):
    """count_classified on an empty sequence should return an empty mapping."""
    counts = count_classified([], rules)
    assert len(counts) == 0


def test_builtin_rules_match_common_levels():
    rules = builtin_rules()
    cats = {r[0] for r in rules}
    assert {"error", "warning", "info", "debug"}.issubset(cats)


def test_builtin_rules_case_insensitive():
    rules = builtin_rules()
    result = classify_line("Exception raised", rules)
    assert result == ["error"]
