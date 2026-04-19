"""Tests for logslice.differ."""
import pytest
from logslice.differ import diff_logs, format_diff, DiffResult


LEFT = [
    "2024-01-01T00:00:01Z INFO started\n",
    "2024-01-01T00:00:02Z ERROR boom\n",
    "2024-01-01T00:00:03Z INFO done\n",
]

RIGHT = [
    "2024-01-02T00:00:01Z INFO started\n",  # same message, different ts
    "2024-01-02T00:00:05Z WARN  slow\n",
    "2024-01-02T00:00:06Z INFO done\n",
]


def test_only_left_contains_error():
    result = diff_logs(LEFT, RIGHT)
    normalized_msgs = [l.strip() for l in result.only_left]
    assert any("ERROR" in m for m in normalized_msgs)


def test_only_right_contains_warn():
    result = diff_logs(LEFT, RIGHT)
    assert any("WARN" in l for l in result.only_right)


def test_common_contains_shared_messages():
    result = diff_logs(LEFT, RIGHT)
    # "started" and "done" normalize to same message
    assert len(result.common) >= 1


def test_empty_inputs():
    result = diff_logs([], [])
    assert result.only_left == []
    assert result.only_right == []
    assert result.common == []


def test_identical_inputs():
    result = diff_logs(LEFT, LEFT)
    assert result.only_left == []
    assert result.only_right == []
    assert len(result.common) == len(LEFT)


def test_format_diff_left_prefix():
    result = DiffResult(only_left=["ERROR boom\n"], only_right=[], common=[])
    out = list(format_diff(result, mode="left"))
    assert out == ["< ERROR boom\n"]


def test_format_diff_right_prefix():
    result = DiffResult(only_left=[], only_right=["WARN slow\n"], common=[])
    out = list(format_diff(result, mode="right"))
    assert out == ["> WARN slow\n"]


def test_format_diff_common_prefix():
    result = DiffResult(only_left=[], only_right=[], common=["INFO ok\n"])
    out = list(format_diff(result, mode="common"))
    assert out == ["= INFO ok\n"]


def test_format_diff_all_includes_all_sections():
    result = DiffResult(
        only_left=["ERROR x\n"],
        only_right=["WARN y\n"],
        common=["INFO z\n"],
    )
    out = list(format_diff(result, mode="all"))
    prefixes = {line[0] for line in out}
    assert prefixes == {"<", ">", "="}
