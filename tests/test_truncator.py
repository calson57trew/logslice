"""Tests for logslice.truncator and logslice.truncator_cli."""

import argparse
import pytest

from logslice.truncator import (
    truncate_line,
    truncate_lines,
    count_truncated,
    DEFAULT_MAX_LENGTH,
)
from logslice.truncator_cli import add_truncate_args, apply_truncation


# --- truncate_line ---

def test_short_line_unchanged():
    assert truncate_line("hello", max_length=20) == "hello"


def test_exact_length_unchanged():
    line = "a" * 10
    assert truncate_line(line, max_length=10) == line


def test_long_line_truncated():
    line = "a" * 50
    result = truncate_line(line, max_length=10)
    assert result == "a" * 7 + "..."
    assert len(result) == 10


def test_newline_stripped_before_check():
    line = "hello\n"
    assert truncate_line(line, max_length=20) == "hello"


def test_invalid_max_length_raises():
    with pytest.raises(ValueError):
        truncate_line("hello", max_length=0)


# --- truncate_lines ---

def test_truncate_lines_all():
    lines = ["short", "x" * 100]
    result = list(truncate_lines(lines, max_length=20))
    assert result[0] == "short"
    assert len(result[1]) == 20


def test_truncate_lines_only_long():
    lines = ["short", "x" * 100, "also short"]
    result = list(truncate_lines(lines, max_length=20, only_long=True))
    assert len(result) == 1
    assert result[0].endswith("...")


def test_truncate_lines_default_max():
    lines = ["a" * (DEFAULT_MAX_LENGTH + 10)]
    result = list(truncate_lines(lines))
    assert len(result[0]) == DEFAULT_MAX_LENGTH


# --- count_truncated ---

def test_count_truncated_none():
    assert count_truncated(["hi", "there"], max_length=20) == 0


def test_count_truncated_some():
    lines = ["short", "x" * 50, "y" * 50]
    assert count_truncated(lines, max_length=20) == 2


# --- CLI integration ---

def make_args(**kwargs):
    defaults = {"max_line_length": None, "truncate_only_long": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_truncate_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_truncate_args(parser)
    args = parser.parse_args(["--max-line-length", "80"])
    assert args.max_line_length == 80


def test_apply_truncation_no_flag_passthrough():
    lines = ["a" * 300]
    args = make_args(max_line_length=None)
    assert apply_truncation(args, lines) == lines


def test_apply_truncation_truncates():
    lines = ["a" * 300]
    args = make_args(max_line_length=50)
    result = apply_truncation(args, lines)
    assert len(result[0]) == 50


def test_apply_truncation_only_long_filters():
    lines = ["short", "x" * 200]
    args = make_args(max_line_length=50, truncate_only_long=True)
    result = apply_truncation(args, lines)
    assert len(result) == 1
