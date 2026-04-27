"""Tests for logslice.anomaly_cli."""

from __future__ import annotations

import argparse
import io

import pytest

from logslice.anomaly_cli import add_anomaly_args, apply_anomaly


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"anomaly_threshold": None, "anomaly_only": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _line(ts: str, msg: str = "event") -> str:
    return f"{ts} {msg}\n"


# ---------------------------------------------------------------------------
# add_anomaly_args
# ---------------------------------------------------------------------------

def test_add_anomaly_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_anomaly_args(parser)
    args = parser.parse_args(["--anomaly-threshold", "30", "--anomaly-only"])
    assert args.anomaly_threshold == pytest.approx(30.0)
    assert args.anomaly_only is True


def test_add_anomaly_args_defaults():
    parser = argparse.ArgumentParser()
    add_anomaly_args(parser)
    args = parser.parse_args([])
    assert args.anomaly_threshold is None
    assert args.anomaly_only is False


# ---------------------------------------------------------------------------
# apply_anomaly
# ---------------------------------------------------------------------------

def test_no_threshold_passthrough():
    lines = [_line("2024-01-01T00:00:00"), _line("2024-01-01T01:00:00")]
    out = io.StringIO()
    result = apply_anomaly(make_args(), lines, out=out)
    assert result is lines
    assert out.getvalue() == ""


def test_threshold_writes_report():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:10:00"),
    ]
    out = io.StringIO()
    result = apply_anomaly(make_args(anomaly_threshold=60.0), lines, out=out)
    report = out.getvalue()
    assert "Anomalies" in report
    assert result == lines  # lines still returned


def test_anomaly_only_returns_empty_list():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:10:00"),
    ]
    out = io.StringIO()
    result = apply_anomaly(
        make_args(anomaly_threshold=60.0, anomaly_only=True), lines, out=out
    )
    assert result == []
    assert "Anomalies" in out.getvalue()


def test_no_anomalies_report_still_written():
    lines = [
        _line("2024-01-01T00:00:00"),
        _line("2024-01-01T00:00:05"),
    ]
    out = io.StringIO()
    apply_anomaly(make_args(anomaly_threshold=60.0), lines, out=out)
    assert "Anomalies     : 0" in out.getvalue()
