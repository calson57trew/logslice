"""Tests for logslice.filter module."""

import re
import pytest
from logslice.filter import compile_pattern, filter_lines, filter_by_level


LINES = [
    "2024-01-01 INFO  service started\n",
    "  continuation of start\n",
    "2024-01-01 ERROR something failed\n",
    "  traceback line 1\n",
    "  traceback line 2\n",
    "2024-01-01 DEBUG low level noise\n",
    "2024-01-01 INFO  all good\n",
]


def test_compile_pattern_basic():
    p = compile_pattern(r"ERROR")
    assert p.search("ERROR found")
    assert not p.search("error found")


def test_compile_pattern_ignore_case():
    p = compile_pattern(r"error", ignore_case=True)
    assert p.search("ERROR found")


def test_filter_include_only():
    p = compile_pattern(r"INFO")
    result = list(filter_lines(LINES, include_pattern=p, keep_continuations=False))
    assert all("INFO" in l for l in result)
    assert len(result) == 2


def test_filter_exclude_only():
    p = compile_pattern(r"DEBUG")
    result = list(filter_lines(LINES, exclude_pattern=p, keep_continuations=False))
    assert not any("DEBUG" in l for l in result)


def test_filter_continuations_kept():
    p = compile_pattern(r"ERROR")
    result = list(filter_lines(LINES, include_pattern=p, keep_continuations=True))
    assert any("traceback" in l for l in result)


def test_filter_continuations_dropped():
    p = compile_pattern(r"ERROR")
    result = list(filter_lines(LINES, include_pattern=p, keep_continuations=False))
    assert not any("traceback" in l for l in result)


def test_filter_include_and_exclude():
    inc = compile_pattern(r"INFO|ERROR")
    exc = compile_pattern(r"ERROR")
    result = list(filter_lines(LINES, include_pattern=inc, exclude_pattern=exc, keep_continuations=False))
    assert all("INFO" in l for l in result)


def test_filter_by_level_single():
    result = list(filter_by_level(LINES, ["ERROR"]))
    assert len(result) == 1
    assert "ERROR" in result[0]


def test_filter_by_level_multiple():
    result = list(filter_by_level(LINES, ["INFO", "ERROR"]))
    assert len(result) == 3


def test_filter_by_level_case_insensitive():
    result = list(filter_by_level(LINES, ["info"], ignore_case=True))
    assert len(result) == 2
