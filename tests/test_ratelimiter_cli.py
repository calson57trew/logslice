"""Tests for logslice.ratelimiter_cli."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

import pytest

from logslice.ratelimiter_cli import add_ratelimit_args, apply_ratelimit


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"rate_limit": None, "rate_window": "1s"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _ts(second: int) -> str:
    dt = datetime(1970, 1, 1, 0, 0, second % 60, tzinfo=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + " message"


# ---------------------------------------------------------------------------
# add_ratelimit_args
# ---------------------------------------------------------------------------

def test_add_ratelimit_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_ratelimit_args(parser)
    args = parser.parse_args(["--rate-limit", "10", "--rate-window", "30s"])
    assert args.rate_limit == 10
    assert args.rate_window == "30s"


def test_rate_limit_default_is_none():
    parser = argparse.ArgumentParser()
    add_ratelimit_args(parser)
    args = parser.parse_args([])
    assert args.rate_limit is None


def test_rate_window_default_is_1s():
    parser = argparse.ArgumentParser()
    add_ratelimit_args(parser)
    args = parser.parse_args([])
    assert args.rate_window == "1s"


# ---------------------------------------------------------------------------
# apply_ratelimit
# ---------------------------------------------------------------------------

def test_no_rate_limit_passthrough():
    lines = [_ts(0), _ts(1), _ts(2)]
    result = apply_ratelimit(make_args(rate_limit=None), lines)
    assert result == lines


def test_rate_limit_applied():
    lines = [_ts(0)] * 6
    result = apply_ratelimit(make_args(rate_limit=3, rate_window="1s"), lines)
    assert len(result) == 3


def test_invalid_window_raises():
    lines = [_ts(0)]
    with pytest.raises(ValueError):
        apply_ratelimit(make_args(rate_limit=1, rate_window="bad"), lines)


def test_returns_list():
    lines = [_ts(0), _ts(1)]
    result = apply_ratelimit(make_args(rate_limit=5, rate_window="1s"), lines)
    assert isinstance(result, list)
