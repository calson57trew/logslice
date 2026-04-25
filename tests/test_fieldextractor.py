"""Tests for logslice.fieldextractor."""

from __future__ import annotations

import pytest

from logslice.fieldextractor import (
    count_extracted,
    extract_fields,
    pick_fields,
    project_lines,
)


# ---------------------------------------------------------------------------
# extract_fields
# ---------------------------------------------------------------------------

def test_extract_simple_pairs():
    line = "level=INFO msg=started"
    assert extract_fields(line) == {"level": "INFO", "msg": "started"}


def test_extract_quoted_value():
    line = 'level=ERROR msg="disk full" host=web01'
    result = extract_fields(line)
    assert result["msg"] == "disk full"
    assert result["host"] == "web01"


def test_extract_no_fields_returns_empty():
    assert extract_fields("plain log line with no kv pairs") == {}


def test_extract_numeric_value():
    line = "duration=42 retries=0"
    result = extract_fields(line)
    assert result["duration"] == "42"
    assert result["retries"] == "0"


def test_extract_ignores_timestamp_like_prefix():
    line = "2024-01-01T00:00:00Z level=WARN msg=timeout"
    result = extract_fields(line)
    assert "level" in result
    assert "msg" in result


# ---------------------------------------------------------------------------
# pick_fields
# ---------------------------------------------------------------------------

def test_pick_fields_subset():
    line = "level=DEBUG msg=ok host=db01"
    result = pick_fields(line, ["level", "host"])
    assert result == {"level": "DEBUG", "host": "db01"}


def test_pick_fields_missing_uses_placeholder():
    line = "level=INFO"
    result = pick_fields(line, ["level", "host"], missing="-")
    assert result["host"] == "-"


def test_pick_fields_empty_field_list():
    line = "level=INFO msg=ok"
    assert pick_fields(line, []) == {}


# ---------------------------------------------------------------------------
# project_lines
# ---------------------------------------------------------------------------

def test_project_lines_tab_separated():
    lines = ["level=INFO msg=ok\n", "level=ERROR msg=fail\n"]
    result = list(project_lines(lines, ["level", "msg"]))
    assert result[0] == "INFO\tok\n"
    assert result[1] == "ERROR\tfail\n"


def test_project_lines_custom_separator():
    lines = ["a=1 b=2\n"]
    result = list(project_lines(lines, ["a", "b"], separator=","))
    assert result[0] == "1,2\n"


def test_project_lines_missing_field_placeholder():
    lines = ["level=WARN\n"]
    result = list(project_lines(lines, ["level", "host"], missing="N/A"))
    assert result[0] == "WARN\tN/A\n"


# ---------------------------------------------------------------------------
# count_extracted
# ---------------------------------------------------------------------------

def test_count_extracted_all_present():
    lines = ["level=INFO\n", "level=ERROR\n"]
    total, present = count_extracted(lines, "level")
    assert total == 2
    assert present == 2


def test_count_extracted_some_missing():
    lines = ["level=INFO\n", "no fields here\n", "level=DEBUG\n"]
    total, present = count_extracted(lines, "level")
    assert total == 3
    assert present == 2


def test_count_extracted_none_present():
    lines = ["msg=hello\n", "msg=world\n"]
    total, present = count_extracted(lines, "level")
    assert total == 2
    assert present == 0
