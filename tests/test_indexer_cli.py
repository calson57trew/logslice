"""Tests for logslice.indexer_cli."""
from __future__ import annotations

import argparse
import io

import pytest

from logslice.indexer_cli import add_index_args, apply_index
from logslice.indexer import build_index, save_index


LOG_LINES = [
    "2024-03-01T08:00:00 INFO  boot\n",
    "2024-03-01T08:01:00 WARN  slow query\n",
]


def make_args(**kwargs):
    defaults = dict(
        index_build=None,
        index_file=None,
        index_seek=None,
        index_stats=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture()
def log_file(tmp_path):
    p = tmp_path / "app.log"
    p.write_text("".join(LOG_LINES), encoding="utf-8")
    return str(p)


@pytest.fixture()
def index_file(tmp_path, log_file):
    index = build_index(log_file)
    p = str(tmp_path / "app.idx")
    save_index(index, p)
    return p


def test_add_index_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_index_args(parser)
    args = parser.parse_args([])
    assert args.index_build is None
    assert args.index_file is None
    assert args.index_seek is None
    assert args.index_stats is False


def test_no_flags_passthrough():
    args = make_args()
    lines = ["hello\n", "world\n"]
    result = apply_index(args, lines, out=io.StringIO())
    assert result == lines


def test_index_build_writes_file(tmp_path, log_file):
    dest = str(tmp_path / "out.idx")
    out = io.StringIO()
    args = make_args(index_build=log_file, index_file=dest)
    apply_index(args, [], out=out)
    import os
    assert os.path.exists(dest)
    assert "Index written" in out.getvalue()


def test_index_seek_prints_offset(index_file):
    out = io.StringIO()
    args = make_args(index_file=index_file, index_seek="2024-03-01T08:01:00")
    apply_index(args, [], out=out)
    output = out.getvalue().strip()
    assert output.isdigit()
    assert int(output) > 0


def test_index_seek_no_match(index_file):
    out = io.StringIO()
    args = make_args(index_file=index_file, index_seek="2099-01-01T00:00:00")
    apply_index(args, [], out=out)
    assert "No entry found" in out.getvalue()


def test_index_seek_missing_index_file_warns():
    out = io.StringIO()
    args = make_args(index_file=None, index_seek="2024-03-01T08:00:00")
    apply_index(args, [], out=out)
    assert "required" in out.getvalue()


def test_index_stats_prints_counts(index_file):
    out = io.StringIO()
    args = make_args(index_file=index_file, index_stats=True)
    apply_index(args, [], out=out)
    output = out.getvalue()
    assert "total" in output
    assert "timed" in output
