"""Tests for logslice.splitter_cli."""
import argparse
import pytest
from logslice.splitter_cli import add_split_args, apply_split


LINES = [f"line {i}\n" for i in range(6)]


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"split_size": None, "split_pattern": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_split_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_split_args(parser)
    args = parser.parse_args(["--split-size", "3"])
    assert args.split_size == 3


def test_add_split_pattern_flag():
    parser = argparse.ArgumentParser()
    add_split_args(parser)
    args = parser.parse_args(["--split-pattern", "^ERROR"])
    assert args.split_pattern == "^ERROR"


def test_no_flags_returns_single_chunk():
    args = make_args()
    result = apply_split(LINES, args)
    assert result == [LINES]


def test_split_size_applied():
    args = make_args(split_size=2)
    result = apply_split(LINES, args)
    assert len(result) == 3
    assert result[0] == LINES[:2]


def test_split_pattern_applied():
    lines = ["START a\n", "body\n", "START b\n", "more\n"]
    args = make_args(split_pattern="^START")
    result = apply_split(lines, args)
    assert len(result) == 2


def test_split_size_takes_precedence_over_pattern():
    """When both flags set, split_size wins (checked first)."""
    args = make_args(split_size=3, split_pattern="^START")
    result = apply_split(LINES, args)
    assert len(result) == 2
