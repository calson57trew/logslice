"""Tests for logslice.summarizer_cli."""

import argparse
import io

from logslice.summarizer_cli import add_summarize_args, apply_summarize


SAMPLE = [
    "2024-01-01T10:00:00 INFO  started\n",
    "2024-01-01T10:00:01 ERROR boom\n",
]


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"summarize": False, "summary_only": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_summarize_args_registers_flags():
    p = argparse.ArgumentParser()
    add_summarize_args(p)
    args = p.parse_args(["--summarize"])
    assert args.summarize is True
    assert args.summary_only is False


def test_add_summary_only_flag():
    p = argparse.ArgumentParser()
    add_summarize_args(p)
    args = p.parse_args(["--summary-only"])
    assert args.summary_only is True


def test_no_flags_passthrough():
    args = make_args()
    out = io.StringIO()
    result = apply_summarize(args, SAMPLE, out=out)
    assert result == SAMPLE
    assert out.getvalue() == ""


def test_summarize_writes_output_and_returns_lines():
    args = make_args(summarize=True)
    out = io.StringIO()
    result = apply_summarize(args, SAMPLE, out=out)
    assert result == SAMPLE
    text = out.getvalue()
    assert "Total lines" in text
    assert "ERROR" in text


def test_summary_only_returns_empty_list():
    args = make_args(summary_only=True)
    out = io.StringIO()
    result = apply_summarize(args, SAMPLE, out=out)
    assert result == []
    assert "Total lines" in out.getvalue()


def test_summarize_empty_input():
    args = make_args(summarize=True)
    out = io.StringIO()
    result = apply_summarize(args, [], out=out)
    assert result == []
    assert "Total lines     : 0" in out.getvalue()
