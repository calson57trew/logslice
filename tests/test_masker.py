"""Tests for logslice.masker."""

from __future__ import annotations

import pytest

from logslice.masker import (
    DEFAULT_PLACEHOLDER,
    compile_mask_rules,
    count_masked,
    mask_line,
    mask_lines,
)


# ---------------------------------------------------------------------------
# compile_mask_rules
# ---------------------------------------------------------------------------

def test_compile_returns_list_of_pairs():
    rules = compile_mask_rules([r"(\d+)"])
    assert len(rules) == 1
    pattern, placeholder = rules[0]
    assert placeholder == DEFAULT_PLACEHOLDER


def test_compile_custom_placeholder():
    rules = compile_mask_rules([r"(\d+)"], placeholder="[HIDDEN]")
    _, ph = rules[0]
    assert ph == "[HIDDEN]"


def test_compile_ignore_case_flag():
    import re
    rules = compile_mask_rules([r"(error)"], ignore_case=True)
    pattern, _ = rules[0]
    assert pattern.flags & re.IGNORECASE


# ---------------------------------------------------------------------------
# mask_line
# ---------------------------------------------------------------------------

def test_mask_capturing_group_only():
    rules = compile_mask_rules([r"password=(\S+)"])
    result = mask_line("auth password=secret123 ok", rules)
    assert result == "auth password=*** ok"


def test_mask_full_match_when_no_group():
    rules = compile_mask_rules([r"\d{3}-\d{4}"])
    result = mask_line("call 555-1234 now", rules)
    assert result == "call *** now"


def test_mask_multiple_occurrences():
    rules = compile_mask_rules([r"(\d+)"])
    result = mask_line("id=42 count=7", rules)
    assert result == "id=*** count=***"


def test_mask_no_match_unchanged():
    rules = compile_mask_rules([r"(\d+)"])
    line = "no numbers here"
    assert mask_line(line, rules) == line


def test_mask_multiple_rules_applied():
    rules = compile_mask_rules([r"(\d+)", r"(secret)"])
    result = mask_line("id=99 secret", rules)
    assert result == "id=*** ***"


def test_mask_ignore_case():
    rules = compile_mask_rules([r"(ERROR)"], ignore_case=True)
    result = mask_line("[error] something broke", rules)
    assert result == "[***] something broke"


# ---------------------------------------------------------------------------
# mask_lines
# ---------------------------------------------------------------------------

def test_mask_lines_yields_all():
    rules = compile_mask_rules([r"(\d+)"])
    lines = ["a=1\n", "b=2\n", "no digits\n"]
    result = list(mask_lines(lines, rules))
    assert result == ["a=***\n", "b=***\n", "no digits\n"]


def test_mask_lines_empty_rules_passthrough():
    lines = ["hello\n", "world\n"]
    assert list(mask_lines(lines, [])) == lines


# ---------------------------------------------------------------------------
# count_masked
# ---------------------------------------------------------------------------

def test_count_masked_some():
    rules = compile_mask_rules([r"(\d+)"])
    lines = ["a=1", "b=2", "no digits"]
    assert count_masked(lines, rules) == 2


def test_count_masked_none():
    rules = compile_mask_rules([r"(\d+)"])
    lines = ["no digits", "here either"]
    assert count_masked(lines, rules) == 0
