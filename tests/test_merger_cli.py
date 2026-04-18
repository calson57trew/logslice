"""Tests for logslice.merger_cli."""

import argparse
import pytest
from logslice.merger_cli import add_merge_args, apply_merge


def make_args(**kwargs):
    ns = argparse.Namespace(
        merge=None,
        merge_sort=True,
        merge_label=False,
    )
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_merge_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_merge_args(parser)
    args = parser.parse_args([])
    assert args.merge is None
    assert args.merge_sort is True
    assert args.merge_label is False


def test_apply_merge_no_extra_files_passthrough():
    primary = ["line1\n", "line2\n"]
    args = make_args(merge=None)
    result = apply_merge(args, primary)
    assert result == primary


def test_apply_merge_with_extra_file(tmp_path):
    extra = tmp_path / "extra.log"
    extra.write_text("2024-01-01T10:00:02 extra line\n")

    primary = ["2024-01-01T10:00:01 primary line\n"]
    args = make_args(merge=[str(extra)], merge_sort=True, merge_label=False)
    result = apply_merge(args, primary)
    assert len(result) == 2
    assert "primary line" in result[0]
    assert "extra line" in result[1]


def test_apply_merge_missing_file_raises():
    args = make_args(merge=["/nonexistent/path.log"])
    with pytest.raises(SystemExit, match="cannot open merge file"):
        apply_merge(args, [])


def test_apply_merge_label_flag(tmp_path):
    extra = tmp_path / "db.log"
    extra.write_text("db line\n")
    primary = ["app line\n"]
    args = make_args(merge=[str(extra)], merge_sort=False, merge_label=True)
    result = apply_merge(args, primary)
    assert any("[<stdin>]" in l for l in result)
    assert any(str(extra) in l for l in result)
