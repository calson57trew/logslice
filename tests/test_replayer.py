"""Tests for logslice.replayer."""

import pytest
from unittest.mock import patch
from logslice.replayer import replay_realtime, replay_fixed, count_replayed


TIMED_LINES = [
    "2024-01-01T00:00:00 INFO  start\n",
    "2024-01-01T00:00:02 INFO  two seconds later\n",
    "2024-01-01T00:00:03 INFO  one second later\n",
]

UNTIMED_LINES = [
    "no timestamp here\n",
    "also no timestamp\n",
]


# ---------------------------------------------------------------------------
# replay_fixed
# ---------------------------------------------------------------------------

def test_fixed_yields_all_lines():
    with patch("time.sleep"):
        result = list(replay_fixed(TIMED_LINES, delay=0.0))
    assert result == TIMED_LINES


def test_fixed_sleeps_between_each_line():
    with patch("time.sleep") as mock_sleep:
        list(replay_fixed(["a\n", "b\n", "c\n"], delay=0.1))
    assert mock_sleep.call_count == 3
    mock_sleep.assert_called_with(0.1)


def test_fixed_negative_delay_raises():
    with pytest.raises(ValueError):
        list(replay_fixed(["a\n"], delay=-1.0))


def test_fixed_zero_delay_allowed():
    with patch("time.sleep"):
        result = list(replay_fixed(["a\n"], delay=0.0))
    assert result == ["a\n"]


# ---------------------------------------------------------------------------
# replay_realtime
# ---------------------------------------------------------------------------

def test_realtime_yields_all_lines():
    with patch("time.sleep"):
        result = list(replay_realtime(TIMED_LINES, speed=1.0))
    assert result == TIMED_LINES


def test_realtime_sleeps_proportional_to_gap():
    with patch("time.sleep") as mock_sleep:
        list(replay_realtime(TIMED_LINES, speed=1.0))
    # First line: no previous → no sleep
    # Second line: 2 s gap → sleep(2.0)
    # Third line: 1 s gap → sleep(1.0)
    sleep_vals = [c.args[0] for c in mock_sleep.call_args_list]
    assert len(sleep_vals) == 2
    assert abs(sleep_vals[0] - 2.0) < 0.01
    assert abs(sleep_vals[1] - 1.0) < 0.01


def test_realtime_speed_doubles_halves_delay():
    with patch("time.sleep") as mock_sleep:
        list(replay_realtime(TIMED_LINES, speed=2.0))
    sleep_vals = [c.args[0] for c in mock_sleep.call_args_list]
    assert abs(sleep_vals[0] - 1.0) < 0.01


def test_realtime_max_gap_caps_sleep():
    with patch("time.sleep") as mock_sleep:
        list(replay_realtime(TIMED_LINES, speed=1.0, max_gap=0.5))
    sleep_vals = [c.args[0] for c in mock_sleep.call_args_list]
    assert all(v <= 0.5 for v in sleep_vals)


def test_realtime_invalid_speed_raises():
    with pytest.raises(ValueError):
        list(replay_realtime(["a\n"], speed=0.0))


def test_realtime_untimed_lines_no_sleep():
    with patch("time.sleep") as mock_sleep:
        result = list(replay_realtime(UNTIMED_LINES, speed=1.0))
    mock_sleep.assert_not_called()
    assert result == UNTIMED_LINES


# ---------------------------------------------------------------------------
# count_replayed
# ---------------------------------------------------------------------------

def test_count_replayed():
    assert count_replayed(iter(["a\n", "b\n", "c\n"])) == 3


def test_count_replayed_empty():
    assert count_replayed(iter([])) == 0
