"""Tests for logslice.redactor and logslice.redactor_cli."""

import argparse
import pytest

from logslice.redactor import (
    compile_redact_patterns,
    redact_line,
    redact_lines,
    count_redactions,
    REDACT_PLACEHOLDER,
)
from logslice.redactor_cli import add_redact_args, apply_redaction


def test_compile_builtin_ip():
    patterns = compile_redact_patterns(["ip"])
    assert len(patterns) == 1


def test_compile_unknown_raises():
    with pytest.raises(ValueError, match="Unknown builtin"):
        compile_redact_patterns(["ssn"])


def test_compile_custom_pattern():
    patterns = compile_redact_patterns([], custom=[r"\bFOO\b"])
    assert len(patterns) == 1


def test_redact_line_ip():
    patterns = compile_redact_patterns(["ip"])
    result, count = redact_line("Connected from 192.168.1.1 ok", patterns)
    assert "192.168.1.1" not in result
    assert REDACT_PLACEHOLDER in result
    assert count == 1


def test_redact_line_email():
    patterns = compile_redact_patterns(["email"])
    result, count = redact_line("user admin@example.com logged in", patterns)
    assert "admin@example.com" not in result
    assert count == 1


def test_redact_line_no_match():
    patterns = compile_redact_patterns(["ip"])
    line = "nothing sensitive here"
    result, count = redact_line(line, patterns)
    assert result == line
    assert count == 0


def test_redact_lines_iterator():
    patterns = compile_redact_patterns(["ip"])
    lines = ["ip: 10.0.0.1\n", "safe line\n"]
    out = list(redact_lines(lines, patterns))
    assert "10.0.0.1" not in out[0]
    assert out[1] == "safe line\n"


def test_count_redactions():
    patterns = compile_redact_patterns(["email"])
    lines = ["a@b.com logged in", "c@d.org failed", "no match"]
    assert count_redactions(lines, patterns) == 2


def test_custom_placeholder():
    patterns = compile_redact_patterns(["ip"])
    result, _ = redact_line("from 1.2.3.4", patterns, placeholder="***")
    assert "***" in result


# CLI tests

def make_args(**kwargs):
    defaults = {"redact": [], "redact_pattern": [], "redact_placeholder": "[REDACTED]"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_redact_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_    args = parser.parse_args(["--redact", "ip", "--redact-placeholder", "XXX"])
    assert args.redact == ["ip"]
    assert args.redact_placeholder == "XXX"


def test_apply_redaction_no_patterns_passthrough():
    args = make_args()
    lines = ["hello world\n"]
    assert list(apply_redaction(args, lines)) == lines


def test_apply_redaction_redacts_ip():
    args = make_args(redact=["ip"])
    lines = ["request from 172.16.0.5\n"]
    out = list(apply_redaction(args, lines))
    assert "172.16.0.5" not in out[0]


def test_apply_redaction_custom_pattern():
    args = make_args(redact_pattern=[r"\bSECRET\b"])
    lines = ["value=SECRET here\n"]
    out = list(apply_redaction(args, lines))
    assert "SECRET" not in out[0]
    assert "[REDACTED]" in out[0]
