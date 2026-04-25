"""Tests for logslice.transformer_cli."""

from __future__ import annotations

import argparse

import pytest

from logslice.transformer_cli import add_transform_args, apply_transform


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "upper": False,
        "lower": False,
        "strip": False,
        "replace": [],
        "transform_ignore_case": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# add_transform_args
# ---------------------------------------------------------------------------

def test_add_transform_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_transform_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "upper")
    assert hasattr(args, "lower")
    assert hasattr(args, "strip")
    assert hasattr(args, "replace")
    assert hasattr(args, "transform_ignore_case")


def test_upper_flag_parsed():
    parser = argparse.ArgumentParser()
    add_transform_args(parser)
    args = parser.parse_args(["--upper"])
    assert args.upper is True


def test_replace_flag_parsed():
    parser = argparse.ArgumentParser()
    add_transform_args(parser)
    args = parser.parse_args(["--replace", r"\d+", "NUM"])
    assert args.replace == [[r"\d+", "NUM"]]


# ---------------------------------------------------------------------------
# apply_transform
# ---------------------------------------------------------------------------

def test_no_flags_passthrough():
    lines = ["hello", "world"]
    assert apply_transform(make_args(), lines) == lines


def test_upper_applied():
    args = make_args(upper=True)
    assert apply_transform(args, ["hello", "world"]) == ["HELLO", "WORLD"]


def test_lower_applied():
    args = make_args(lower=True)
    assert apply_transform(args, ["FOO", "BAR"]) == ["foo", "bar"]


def test_strip_applied():
    args = make_args(strip=True)
    assert apply_transform(args, ["  hi  ", " bye "]) == ["hi", "bye"]


def test_replace_applied():
    args = make_args(replace=[[r"\d+", "NUM"]])
    result = apply_transform(args, ["error 42", "line 7"])
    assert result == ["error NUM", "line NUM"]


def test_multiple_ops_chained():
    args = make_args(strip=True, upper=True)
    result = apply_transform(args, ["  hello  "])
    assert result == ["HELLO"]
