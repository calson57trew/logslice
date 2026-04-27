"""Tests for logslice/baseliner.py"""
import json
import os
import pytest

from logslice.baseliner import (
    BaselineResult,
    compare_to_baseline,
    format_baseline_summary,
    iter_new_lines,
    load_baseline,
    save_baseline,
)


LINES = [
    "2024-01-01 00:00:01 INFO  server started\n",
    "2024-01-01 00:00:02 ERROR disk full\n",
    "2024-01-01 00:00:03 WARN  high memory\n",
]


@pytest.fixture()
def baseline_path(tmp_path):
    return str(tmp_path / "baseline.json")


def test_load_missing_file_returns_empty(baseline_path):
    result = load_baseline(baseline_path)
    assert result == set()


def test_save_and_load_roundtrip(baseline_path):
    count = save_baseline(baseline_path, LINES)
    assert count == len(LINES)
    loaded = load_baseline(baseline_path)
    assert len(loaded) == len(LINES)


def test_load_invalid_json_type(baseline_path):
    with open(baseline_path, "w") as fh:
        json.dump({"bad": "type"}, fh)
    with pytest.raises(ValueError, match="JSON array"):
        load_baseline(baseline_path)


def test_compare_all_new_when_baseline_empty():
    result = compare_to_baseline(LINES, set())
    assert result.new_count == len(LINES)
    assert result.known_count == 0


def test_compare_all_known_when_baseline_full(baseline_path):
    save_baseline(baseline_path, LINES)
    baseline = load_baseline(baseline_path)
    result = compare_to_baseline(LINES, baseline)
    assert result.known_count == len(LINES)
    assert result.new_count == 0


def test_compare_partial_match(baseline_path):
    save_baseline(baseline_path, LINES[:1])
    baseline = load_baseline(baseline_path)
    result = compare_to_baseline(LINES, baseline)
    assert result.new_count == 2
    assert result.known_count == 1


def test_iter_new_lines_yields_only_new(baseline_path):
    save_baseline(baseline_path, LINES[:1])
    baseline = load_baseline(baseline_path)
    result = compare_to_baseline(LINES, baseline)
    new = list(iter_new_lines(result))
    assert new == LINES[1:]


def test_format_baseline_summary_contains_counts():
    result = BaselineResult(new_lines=LINES[:2], known_lines=LINES[2:], baseline_size=5)
    summary = format_baseline_summary(result)
    assert "2" in summary
    assert "1" in summary
    assert "5" in summary


def test_baseline_size_reflects_loaded_set():
    result = compare_to_baseline(LINES, {"x", "y"})
    assert result.baseline_size == 2
