"""Tests for logslice.contextwin and logslice.contextwin_cli."""

import argparse
import pytest

from logslice.contextwin import context_window, count_context_lines
from logslice.contextwin_cli import add_context_args, apply_context


LINES = [
    "2024-01-01T00:00:01 INFO  startup\n",
    "2024-01-01T00:00:02 DEBUG loop tick\n",
    "2024-01-01T00:00:03 ERROR something broke\n",
    "2024-01-01T00:00:04 DEBUG recovering\n",
    "2024-01-01T00:00:05 INFO  recovered\n",
    "2024-01-01T00:00:06 ERROR second failure\n",
    "2024-01-01T00:00:07 INFO  done\n",
]


def _err_pred(line: str) -> bool:
    return "ERROR" in line


def test_no_predicate_yields_all_lines():
    result = list(context_window(LINES))
    assert result == LINES


def test_before_context_only():
    result = list(context_window(LINES, before=1, predicate=_err_pred))
    assert LINES[1] in result  # line before first ERROR
    assert LINES[2] in result  # first ERROR itself
    assert LINES[4] not in result  # "recovered" not adjacent


def test_after_context_only():
    result = list(context_window(LINES, after=1, predicate=_err_pred))
    assert LINES[2] in result  # first ERROR
    assert LINES[3] in result  # line after first ERROR
    assert LINES[1] not in result  # line before not included


def test_before_and_after_context():
    result = list(context_window(LINES, before=1, after=1, predicate=_err_pred))
    # Both errors + their neighbours
    assert LINES[1] in result
    assert LINES[2] in result
    assert LINES[3] in result
    assert LINES[5] in result
    assert LINES[6] in result


def test_overlapping_windows_no_duplicates():
    # If two matches are close, lines between them should appear only once
    result = list(context_window(LINES, before=2, after=2, predicate=_err_pred))
    assert len(result) == len(set(result))


def test_negative_before_raises():
    with pytest.raises(ValueError):
        list(context_window(LINES, before=-1, predicate=_err_pred))


def test_negative_after_raises():
    with pytest.raises(ValueError):
        list(context_window(LINES, after=-1, predicate=_err_pred))


def test_count_context_lines():
    n = count_context_lines(LINES, before=1, after=0, predicate=_err_pred)
    assert n >= 2  # at minimum both ERROR lines


# --- CLI tests ---

def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"before": 0, "after": 0, "context": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_context_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_context_args(parser)
    args = parser.parse_args(["-B", "2", "-A", "3"])
    assert args.before == 2
    assert args.after == 3


def test_context_shorthand_sets_both():
    parser = argparse.ArgumentParser()
    add_context_args(parser)
    args = parser.parse_args(["-C", "2"])
    result = apply_context(args, LINES, pattern="ERROR")
    assert any("ERROR" in l for l in result)


def test_no_flags_passthrough():
    args = make_args()
    result = apply_context(args, LINES, pattern="ERROR")
    assert result == LINES


def test_no_pattern_passthrough():
    args = make_args(before=2, after=2)
    result = apply_context(args, LINES, pattern=None)
    assert result == LINES


def test_apply_context_filters_correctly():
    args = make_args(before=0, after=1)
    result = apply_context(args, LINES, pattern="ERROR")
    assert any("ERROR" in l for l in result)
    assert any("recovering" in l or "done" in l for l in result)
