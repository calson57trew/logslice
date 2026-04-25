"""Tests for logslice.transformer."""

from __future__ import annotations

import pytest

from logslice.transformer import (
    compile_transforms,
    count_transformed,
    transform_line,
    transform_lines,
)


# ---------------------------------------------------------------------------
# compile_transforms
# ---------------------------------------------------------------------------

def test_compile_upper_returns_callable():
    fns = compile_transforms([("upper",)])
    assert len(fns) == 1
    assert fns[0]("hello") == "HELLO"


def test_compile_lower_returns_callable():
    fns = compile_transforms([("lower",)])
    assert fns[0]("WORLD") == "world"


def test_compile_strip_returns_callable():
    fns = compile_transforms([("strip",)])
    assert fns[0]("  hi  ") == "hi"


def test_compile_replace_basic():
    fns = compile_transforms([("replace", r"\d+", "NUM")])
    assert fns[0]("error 42 at line 7") == "error NUM at line NUM"


def test_compile_replace_ignore_case():
    fns = compile_transforms([("replace", "error", "ERR")], ignore_case=True)
    assert fns[0]("ERROR: something") == "ERR: something"


def test_compile_unknown_op_raises():
    with pytest.raises(ValueError, match="Unknown transform op"):
        compile_transforms([("reverse",)])


def test_compile_replace_missing_args_raises():
    with pytest.raises(ValueError, match="requires pattern and replacement"):
        compile_transforms([("replace", "only_one")])


# ---------------------------------------------------------------------------
# transform_line
# ---------------------------------------------------------------------------

def test_transform_line_chained():
    fns = compile_transforms([("strip",), ("upper",)])
    assert transform_line("  hello  ", fns) == "HELLO"


def test_transform_line_no_transforms():
    assert transform_line("unchanged", []) == "unchanged"


# ---------------------------------------------------------------------------
# transform_lines
# ---------------------------------------------------------------------------

def test_transform_lines_yields_all():
    fns = compile_transforms([("lower",)])
    result = list(transform_lines(["FOO", "BAR", "BAZ"], fns))
    assert result == ["foo", "bar", "baz"]


def test_transform_lines_empty_input():
    fns = compile_transforms([("upper",)])
    assert list(transform_lines([], fns)) == []


# ---------------------------------------------------------------------------
# count_transformed
# ---------------------------------------------------------------------------

def test_count_transformed_some_changed():
    original = ["hello", "world", "foo"]
    result = ["HELLO", "world", "FOO"]
    assert count_transformed(original, result) == 2


def test_count_transformed_none_changed():
    lines = ["a", "b"]
    assert count_transformed(lines, lines[:]) == 0


def test_count_transformed_all_changed():
    original = ["a", "b", "c"]
    result = ["A", "B", "C"]
    assert count_transformed(original, result) == 3
