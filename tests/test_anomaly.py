"""Tests for logslice.anomaly."""

from __future__ import annotations

import pytest

from logslice.anomaly import (
    AnomalyResult,
    detect_anomalies,
    format_anomalies,
)


def _line(ts: str, msg: str = "some event") -> str:
    return f"{ts} {msg}\n"


# ---------------------------------------------------------------------------
# detect_anomalies
# ---------------------------------------------------------------------------

def test_no_lines_returns_empty_result():
    result = detect_anomalies([])
    assert result.total_lines == 0
    assert result.timed_lines == 0
    assert result.anomaly_count == 0


def test_single_line_no_anomaly():
    result = detect_anomalies([_line("2024-01-01T00:00:00")])
    assert result.anomaly_count == 0
    assert result.timed_lines == 1


def test_gap_below_threshold_not_flagged():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:00:30"),
    ]
    result = detect_anomalies(lines, threshold_seconds=60.0)
    assert result.anomaly_count == 0


def test_gap_above_threshold_flagged():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:05:00"),
    ]
    result = detect_anomalies(lines, threshold_seconds=60.0)
    assert result.anomaly_count == 1
    assert result.events[0].gap_seconds == pytest.approx(300.0)


def test_multiple_anomalies_detected():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:05:00"),
        _line("2024-01-01T00:06:00"),
        _line("2024-01-01T01:00:00"),
    ]
    result = detect_anomalies(lines, threshold_seconds=60.0)
    assert result.anomaly_count == 2


def test_untimed_lines_counted_but_not_compared():
    lines = [
        _line("2024-01-01T00:00:00"),
        "continuation line without timestamp\n",
        _line("2024-01-01T00:00:10"),
    ]
    result = detect_anomalies(lines, threshold_seconds=5.0)
    assert result.total_lines == 3
    assert result.timed_lines == 2
    assert result.anomaly_count == 1  # 10s > 5s


def test_space_separated_timestamp_parsed():
    lines = [
        "2024-01-01 00:00:00 start\n",
        "2024-01-01 00:10:00 later\n",
    ]
    result = detect_anomalies(lines, threshold_seconds=60.0)
    assert result.anomaly_count == 1
    assert result.events[0].gap_seconds == pytest.approx(600.0)


def test_event_stores_prev_and_curr_timestamps():
    lines = [
        _line("2024-01-01T08:00:00"),
        _line("2024-01-01T09:00:00"),
    ]
    result = detect_anomalies(lines, threshold_seconds=10.0)
    ev = result.events[0]
    assert ev.prev_ts == "2024-01-01T08:00:00"
    assert ev.curr_ts == "2024-01-01T09:00:00"


# ---------------------------------------------------------------------------
# format_anomalies
# ---------------------------------------------------------------------------

def test_format_includes_counts():
    result = AnomalyResult(total_lines=10, timed_lines=8)
    out = format_anomalies(result)
    assert "Total lines" in out
    assert "10" in out
    assert "Timed lines" in out
    assert "8" in out


def test_format_lists_events():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:10:00"),
    ]
    result = detect_anomalies(lines, threshold_seconds=60.0)
    out = format_anomalies(result)
    assert "600.0s" in out
    assert "2024-01-01T00:00:00" in out
    assert "2024-01-01T00:10:00" in out
