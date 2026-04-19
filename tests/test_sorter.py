"""Tests for logslice.sorter and logslice.sorter_cli."""

import argparse
import pytest
from logslice.sorter import sort_lines, count_out_of_order
from logslice.sorter_cli import add_sort_args, apply_sorting


L1 = "2024-01-01T10:00:00 INFO  first\n"
L2 = "2024-01-01T10:05:00 INFO  second\n"
L3 = "2024-01-01T10:10:00 INFO  third\n"
CONT = "    continuation of third\n"
UNTIMED = "bare line without timestamp\n"


def test_sort_ascending():
    result = sort_lines([L3, L1, L2])
    assert result == [L1, L2, L3]


def test_sort_descending():
    result = sort_lines([L1, L3, L2], reverse=True)
    assert result == [L3, L2, L1]


def test_continuation_travels_with_parent():
    result = sort_lines([L3, CONT, L1, L2])
    assert result == [L1, L2, L3, CONT]


def test_untimed_lines_placed_first_ascending():
    result = sort_lines([L2, UNTIMED, L1])
    assert result[0] == UNTIMED


def test_untimed_lines_placed_last_descending():
    result = sort_lines([L1, UNTIMED, L2], reverse=True)
    assert result[-1] == UNTIMED


def test_already_sorted_unchanged():
    lines = [L1, L2, L3]
    assert sort_lines(lines) == lines


def test_empty_input():
    assert sort_lines([]) == []


def test_count_out_of_order_none():
    assert count_out_of_order([L1, L2, L3]) == 0


def test_count_out_of_order_one():
    assert count_out_of_order([L1, L3, L2]) == 1


def test_count_out_of_order_ignores_untimed():
    assert count_out_of_order([L1, UNTIMED, L2]) == 0


# --- CLI helpers ---

def make_args(**kwargs):
    ns = argparse.Namespace(sort=False, sort_reverse=False, check_order=False)
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_add_sort_args_registers_flags():
    p = argparse.ArgumentParser()
    add_sort_args(p)
    args = p.parse_args(["--sort"])
    assert args.sort is True


def test_no_flags_passthrough():
    lines = [L3, L1]
    result = apply_sorting(make_args(), lines)
    assert result == lines


def test_sort_flag_sorts_ascending():
    result = apply_sorting(make_args(sort=True), [L3, L1, L2])
    assert result == [L1, L2, L3]


def test_sort_reverse_flag():
    result = apply_sorting(make_args(sort_reverse=True), [L1, L3, L2])
    assert result == [L3, L2, L1]


def test_check_order_prints_and_returns_unchanged(capsys):
    lines = [L3, L1]
    result = apply_sorting(make_args(check_order=True), lines)
    assert result == lines
    captured = capsys.readouterr()
    assert "Out-of-order" in captured.out
