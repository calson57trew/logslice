"""Tests for logslice.slicer slice_logs function."""

import io
import pytest
from logslice.slicer import slice_logs

SAMPLE_LOG = """2024-03-12 09:58:00 INFO  pre-start check
2024-03-12 10:00:00 INFO  server started
    listening on port 8080
2024-03-12 10:01:30 DEBUG request received
2024-03-12 10:05:00 WARN  high memory usage
2024-03-12 10:10:00 ERROR out of memory
"""


def make_source(text: str) -> io.StringIO:
    return io.StringIO(text)


def test_start_only():
    lines = list(slice_logs(make_source(SAMPLE_LOG), start='2024-03-12 10:01:00'))
    assert any('request received' in l for l in lines)
    assert not any('server started' in l for l in lines)


def test_end_only():
    lines = list(slice_logs(make_source(SAMPLE_LOG), end='2024-03-12 10:01:00'))
    assert any('server started' in l for l in lines)
    assert not any('high memory' in l for l in lines)


def test_start_and_end():
    lines = list(slice_logs(make_source(SAMPLE_LOG),
                            start='2024-03-12 10:00:00',
                            end='2024-03-12 10:05:00'))
    assert any('server started' in l for l in lines)
    assert any('high memory' in l for l in lines)
    assert not any('out of memory' in l for l in lines)
    assert not any('pre-start' in l for l in lines)


def test_continuation_lines_included():
    lines = list(slice_logs(make_source(SAMPLE_LOG),
                            start='2024-03-12 10:00:00',
                            end='2024-03-12 10:02:00'))
    assert any('listening on port 8080' in l for l in lines)


def test_no_match_returns_empty():
    lines = list(slice_logs(make_source(SAMPLE_LOG),
                            start='2025-01-01 00:00:00'))
    assert lines == []


def test_invalid_start_raises():
    with pytest.raises(ValueError):
        list(slice_logs(make_source(SAMPLE_LOG), start='bad-date'))
