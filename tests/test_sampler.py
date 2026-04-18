"""Tests for logslice.sampler and logslice.sampler_cli."""

from __future__ import annotations

import argparse
import pytest

from logslice.sampler import sample_every_n, sample_random, count_sampled
from logslice.sampler_cli import add_sample_args, apply_sampling

ANCHOR = "2024-01-01T00:00:0{i}Z level=INFO msg=hello\n"
CONT = "    continuation line\n"


def make_log(n: int, with_cont: bool = False) -> list[str]:
    lines = []
    for i in range(n):
        lines.append(f"2024-01-01T00:00:{i:02d}Z level=INFO msg=line{i}\n")
        if with_cont:
            lines.append(CONT)
    return lines


def test_every_n_basic():
    log = make_log(6)
    result = list(sample_every_n(log, 2))
    assert len(result) == 3
    assert "line1" in result[0]
    assert "line3" in result[1]
    assert "line5" in result[2]


def test_every_n_keeps_continuations():
    log = make_log(4, with_cont=True)  # 8 lines total
    result = list(sample_every_n(log, 2))
    # entries 2 and 4 kept, each has a continuation
    assert len(result) == 4
    assert result[1] == CONT


def test_every_n_invalid_raises():
    with pytest.raises(ValueError):
        list(sample_every_n([], 0))


def test_random_rate_one_keeps_all():
    log = make_log(10)
    result = list(sample_random(log, 1.0, seed=42))
    assert result == log


def test_random_rate_reproducible():
    log = make_log(20)
    r1 = list(sample_random(log, 0.5, seed=7))
    r2 = list(sample_random(log, 0.5, seed=7))
    assert r1 == r2


def test_random_invalid_rate_raises():
    with pytest.raises(ValueError):
        list(sample_random([], 0.0))
    with pytest.raises(ValueError):
        list(sample_random([], 1.1))


def test_count_sampled():
    log = make_log(3, with_cont=True)
    stats = count_sampled(log)
    assert stats["anchors"] == 3
    assert stats["total"] == 6


# --- CLI ---

def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"sample_n": None, "sample_rate": None, "sample_seed": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_sample_args_registers_flags():
    p = argparse.ArgumentParser()
    add_sample_args(p)
    args = p.parse_args(["--sample-n", "3"])
    assert args.sample_n == 3


def test_apply_sampling_passthrough():
    lines = make_log(4)
    result = list(apply_sampling(make_args(), lines))
    assert result == lines


def test_apply_sampling_n():
    lines = make_log(6)
    result = list(apply_sampling(make_args(sample_n=3), lines))
    assert len(result) == 2


def test_apply_sampling_mutual_exclusion():
    with pytest.raises(ValueError):
        apply_sampling(make_args(sample_n=2, sample_rate=0.5), [])
