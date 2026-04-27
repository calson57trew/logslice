"""Tests for logslice/baseliner_cli.py"""
import argparse
import io
import json
import os
import pytest

from logslice.baseliner_cli import add_baseline_args, apply_baseline
from logslice.baseliner import save_baseline


LINES = [
    "2024-01-01 00:00:01 INFO  startup\n",
    "2024-01-01 00:00:02 ERROR crash\n",
]


def make_args(**kwargs):
    defaults = dict(
        baseline_file=None,
        baseline_save=False,
        baseline_summary=False,
        baseline_emit_known=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_baseline_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_baseline_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "baseline_file")
    assert hasattr(args, "baseline_save")
    assert hasattr(args, "baseline_summary")
    assert hasattr(args, "baseline_emit_known")


def test_no_baseline_file_passthrough():
    args = make_args(baseline_file=None)
    result = apply_baseline(args, LINES)
    assert result is LINES


def test_save_baseline_writes_file(tmp_path):
    path = str(tmp_path / "bl.json")
    args = make_args(baseline_file=path, baseline_save=True)
    out = io.StringIO()
    returned = apply_baseline(args, LINES, out=out)
    assert returned is LINES
    assert os.path.exists(path)
    with open(path) as fh:
        data = json.load(fh)
    assert isinstance(data, list)
    assert len(data) == 2


def test_save_baseline_summary_message(tmp_path):
    path = str(tmp_path / "bl.json")
    args = make_args(baseline_file=path, baseline_save=True, baseline_summary=True)
    out = io.StringIO()
    apply_baseline(args, LINES, out=out)
    assert "saved" in out.getvalue().lower()


def test_compare_returns_only_new_lines(tmp_path):
    path = str(tmp_path / "bl.json")
    save_baseline(path, LINES[:1])
    args = make_args(baseline_file=path)
    result = apply_baseline(args, LINES)
    assert len(result) == 1
    assert result[0] == LINES[1]


def test_emit_known_returns_all_lines(tmp_path):
    path = str(tmp_path / "bl.json")
    save_baseline(path, LINES)
    args = make_args(baseline_file=path, baseline_emit_known=True)
    result = apply_baseline(args, LINES)
    assert result == LINES


def test_summary_printed_on_compare(tmp_path):
    path = str(tmp_path / "bl.json")
    save_baseline(path, LINES[:1])
    args = make_args(baseline_file=path, baseline_summary=True)
    out = io.StringIO()
    apply_baseline(args, LINES, out=out)
    text = out.getvalue()
    assert "New" in text
    assert "Known" in text
