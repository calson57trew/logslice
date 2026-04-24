"""Tests for logslice.watchdog and logslice.watchdog_cli."""

from __future__ import annotations

import io
import sys
import tempfile
import time
import threading
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pytest

from logslice.watchdog import watch_lines, count_watched, tail_lines
from logslice.watchdog_cli import add_watch_args, apply_watch


# ---------------------------------------------------------------------------
# watch_lines
# ---------------------------------------------------------------------------

def test_watch_lines_passthrough():
    lines = ["INFO start\n", "ERROR boom\n", "INFO end\n"]
    result = watch_lines(lines, lambda ln: False, lambda ln: None)
    assert result == lines


def test_watch_lines_calls_on_match():
    matched: list[str] = []
    lines = ["INFO ok\n", "ERROR bad\n", "WARN meh\n"]
    watch_lines(lines, lambda ln: "ERROR" in ln, matched.append)
    assert matched == ["ERROR bad\n"]


def test_watch_lines_multiple_matches():
    matched: list[str] = []
    lines = ["ERROR a\n", "ERROR b\n", "INFO c\n"]
    watch_lines(lines, lambda ln: ln.startswith("ERROR"), matched.append)
    assert len(matched) == 2


# ---------------------------------------------------------------------------
# count_watched
# ---------------------------------------------------------------------------

def test_count_watched_none():
    assert count_watched(["INFO a\n", "INFO b\n"], lambda ln: "ERROR" in ln) == 0


def test_count_watched_some():
    lines = ["ERROR x\n", "INFO y\n", "ERROR z\n"]
    assert count_watched(lines, lambda ln: "ERROR" in ln) == 2


# ---------------------------------------------------------------------------
# tail_lines (file-based)
# ---------------------------------------------------------------------------

def test_tail_lines_reads_appended_content():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        tmp = Path(f.name)
        f.write("first line\n")

    collected: list[str] = []

    def _write_later():
        time.sleep(0.05)
        with tmp.open("a") as fh:
            fh.write("second line\n")
        time.sleep(0.05)
        with tmp.open("a") as fh:
            fh.write("third line\n")

    t = threading.Thread(target=_write_later, daemon=True)
    t.start()
    for ln in tail_lines(tmp, poll_interval=0.02, max_iterations=20):
        collected.append(ln)
        if len(collected) >= 2:
            break
    t.join(timeout=2)
    tmp.unlink(missing_ok=True)

    assert collected[0] == "second line\n"
    assert collected[1] == "third line\n"


# ---------------------------------------------------------------------------
# watchdog_cli
# ---------------------------------------------------------------------------

def make_args(**kwargs) -> Namespace:
    defaults = {"watch_pattern": None, "watch_ignore_case": False, "watch_prefix": "[WATCH]"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_add_watch_args_registers_flags():
    p = ArgumentParser()
    add_watch_args(p)
    args = p.parse_args(["--watch-pattern", "ERR", "--watch-ignore-case"])
    assert args.watch_pattern == "ERR"
    assert args.watch_ignore_case is True


def test_no_watch_pattern_passthrough():
    lines = ["INFO a\n", "ERROR b\n"]
    result = apply_watch(make_args(), lines)
    assert result == lines


def test_apply_watch_emits_alert_to_stderr(capsys):
    lines = ["INFO ok\n", "ERROR boom\n"]
    result = apply_watch(make_args(watch_pattern="ERROR"), lines)
    assert result == lines
    captured = capsys.readouterr()
    assert "ERROR boom" in captured.err
    assert "[WATCH]" in captured.err


def test_apply_watch_custom_prefix(capsys):
    lines = ["CRITICAL meltdown\n"]
    apply_watch(make_args(watch_pattern="CRITICAL", watch_prefix="!!!"), lines)
    captured = capsys.readouterr()
    assert captured.err.startswith("!!!")


def test_apply_watch_ignore_case(capsys):
    lines = ["error lowercase\n"]
    apply_watch(make_args(watch_pattern="ERROR", watch_ignore_case=True), lines)
    captured = capsys.readouterr()
    assert "error lowercase" in captured.err
