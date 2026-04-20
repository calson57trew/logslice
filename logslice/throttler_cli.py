"""CLI integration for the throttler module."""

from __future__ import annotations

import argparse
from typing import List

from logslice.throttler import throttle_lines


def add_throttle_args(parser: argparse.ArgumentParser) -> None:
    """Register --throttle-max and --throttle-window flags on *parser*."""
    group = parser.add_argument_group("throttling")
    group.add_argument(
        "--throttle-max",
        type=int,
        default=None,
        metavar="N",
        help="Keep at most N timestamped lines per time window (default: off).",
    )
    group.add_argument(
        "--throttle-window",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Duration of the throttle window in seconds (default: 1.0).",
    )


def apply_throttling(
    lines: List[str], args: argparse.Namespace
) -> List[str]:
    """Apply throttling to *lines* if --throttle-max is set; return result."""
    max_per_window = getattr(args, "throttle_max", None)
    if not max_per_window:
        return lines

    window = getattr(args, "throttle_window", 1.0) or 1.0
    return list(throttle_lines(lines, max_per_window=max_per_window, window_seconds=window))
