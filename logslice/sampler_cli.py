"""CLI integration for the sampler module."""

from __future__ import annotations

import argparse
from typing import Iterable

from logslice.sampler import sample_every_n, sample_random


def add_sample_args(parser: argparse.ArgumentParser) -> None:
    """Register --sample-n and --sample-rate flags on *parser*."""
    grp = parser.add_argument_group("sampling")
    grp.add_argument(
        "--sample-n",
        metavar="N",
        type=int,
        default=None,
        help="Keep every Nth log entry (1 = keep all).",
    )
    grp.add_argument(
        "--sample-rate",
        metavar="RATE",
        type=float,
        default=None,
        help="Randomly keep each log entry with probability RATE (0 < RATE <= 1).",
    )
    grp.add_argument(
        "--sample-seed",
        metavar="SEED",
        type=int,
        default=None,
        help="Random seed for --sample-rate (for reproducibility).",
    )


def apply_sampling(args: argparse.Namespace, lines: Iterable[str]) -> Iterable[str]:
    """Apply sampling to *lines* based on parsed *args*.

    Returns the (possibly filtered) iterable unchanged when no sampling
    flags are set.  Raises ValueError if both flags are supplied.
    """
    has_n = args.sample_n is not None
    has_rate = args.sample_rate is not None

    if has_n and has_rate:
        raise ValueError("--sample-n and --sample-rate are mutually exclusive")

    if has_n:
        return sample_every_n(lines, args.sample_n)

    if has_rate:
        return sample_random(lines, args.sample_rate, seed=args.sample_seed)

    return lines
