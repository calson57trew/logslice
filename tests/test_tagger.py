"""Tests for logslice.tagger and logslice.tagger_cli."""

import argparse
import pytest

from logslice.tagger import compile_tag_rules, tag_line, apply_tag, tag_lines, count_tagged
from logslice.tagger_cli import add_tag_args, apply_tagging


RULES_RAW = [("error", "ERROR"), ("warn", "WARN")]


def compiled():
    return compile_tag_rules(RULES_RAW)


def test_compile_tag_rules_returns_pairs():
    rules = compiled()
    assert len(rules) == 2
    assert rules[0][1] == "ERROR"


def test_tag_line_first_match_only():
    rules = compiled()
    tags = tag_line("ERROR and warn here", rules, multi=False)
    assert tags == ["ERROR"]


def test_tag_line_multi():
    rules = compiled()
    tags = tag_line("error and warn here", rules, multi=True)
    assert tags == ["ERROR", "WARN"]


def test_tag_line_no_match():
    rules = compiled()
    assert tag_line("all good", rules) == []


def test_apply_tag_prefix():
    result = apply_tag("some line\n", ["ERROR"])
    assert result == "[ERROR] some line\n"


def test_apply_tag_suffix():
    result = apply_tag("some line\n", ["ERROR", "WARN"], prefix=False)
    assert result == "some line #ERROR,WARN\n"


def test_apply_tag_empty_tags_returns_original():
    line = "unchanged\n"
    assert apply_tag(line, []) == line


def test_tag_lines_passthrough_untagged():
    rules = compiled()
    lines = ["error occurred\n", "all fine\n"]
    result = list(tag_lines(lines, rules))
    assert result[0].startswith("[ERROR]")
    assert result[1] == "all fine\n"


def test_tag_lines_suppress_untagged():
    rules = compiled()
    lines = ["error here\n", "nothing\n"]
    result = list(tag_lines(lines, rules, passthrough_untagged=False))
    assert len(result) == 1
    assert "[ERROR]" in result[0]


def test_count_tagged():
    rules = compiled()
    lines = ["error\n", "warn\n", "ok\n"]
    assert count_tagged(lines, rules) == 2


# CLI tests

def make_args(**kwargs):
    base = {"tags": [], "tag_multi": False, "tag_suffix": False, "tag_only": False}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_add_tag_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_tag_args(parser)
    args = parser.parse_args(["--tag", "error=ERROR", "--tag-multi"])
    assert args.tags == ["error=ERROR"]
    assert args.tag_multi is True


def test_apply_tagging_no_tags_passthrough():
    args = make_args()
    lines = ["hello\n"]
    assert apply_tagging(args, lines) == lines


def test_apply_tagging_tags_line():
    args = make_args(tags=["error=ERR"])
    lines = ["an error occurred\n", "fine\n"]
    result = apply_tagging(args, lines)
    assert result[0] == "[ERR] an error occurred\n"
    assert result[1] == "fine\n"


def test_apply_tagging_invalid_format_raises():
    args = make_args(tags=["badformat"])
    with pytest.raises(ValueError, match="PATTERN=LABEL"):
        apply_tagging(args, [])
