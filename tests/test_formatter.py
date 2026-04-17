"""Tests for logslice.formatter."""

import io
import pytest
from logslice.formatter import (
    format_lines_plain,
    format_lines_json,
    format_lines_numbered,
    get_formatter,
    write_output,
)
import json


LINES = ["first line\n", "second line\n", "third line\n"]


def test_plain_passthrough():
    result = list(format_lines_plain(LINES))
    assert result == LINES


def test_json_format():
    result = list(format_lines_json(LINES))
    assert len(result) == 3
    obj = json.loads(result[0])
    assert obj["index"] == 0
    assert obj["line"] == "first line"


def test_json_strips_newline():
    result = list(format_lines_json(["hello\n"]))
    obj = json.loads(result[0])
    assert obj["line"] == "hello"


def test_numbered_format():
    result = list(format_lines_numbered(LINES))
    assert result[0].startswith("     1  first line")
    assert result[2].startswith("     3  third line")


def test_numbered_custom_start():
    result = list(format_lines_numbered(["a\n"], start=10))
    assert "10" in result[0]


def test_get_formatter_valid():
    f = get_formatter("json")
    assert callable(f)


def test_get_formatter_invalid():
    with pytest.raises(ValueError, match="Unknown format"):
        get_formatter("xml")


def test_write_output_plain():
    buf = io.StringIO()
    count = write_output(iter(LINES), fmt="plain", output=buf)
    assert count == 3
    buf.seek(0)
    content = buf.read()
    assert "first line" in content


def test_write_output_json():
    buf = io.StringIO()
    write_output(iter(["hello\n"]), fmt="json", output=buf)
    buf.seek(0)
    obj = json.loads(buf.readline())
    assert obj["line"] == "hello"


def test_write_output_ensures_newline():
    buf = io.StringIO()
    write_output(iter(["no newline"]), fmt="plain", output=buf)
    buf.seek(0)
    assert buf.read().endswith("\n")
