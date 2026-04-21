"""CLI integration for the rate-limiter feature."""

from __future__ import annotations

import argparse
from typing import List

from logslice.ratelimiter import parse_window, ratelimit_lines


def add_ratelimit_args(parser: argparse.ArgumentParser) -> None:
    """Register --rate-limit and --rate-window flags on *parser*."""
    group = parser.add_argument_group("rate limiting")
    group.add_argument(
        "--rate-limit",
        metavar="N",
        type=int,
        default=None,
        help="Maximum number of log lines to emit per time window.",
    )
    group.add_argument(
        "--rate-window",
        metavar="WINDOW",
        default="1s",
        help=(
            "Time window for rate limiting (e.g. '1s', '30m', '2h'). "
            "Default: 1s."
        ),
    )


def apply_ratelimit(args: argparse.Namespace, lines: List[str]) -> List[str]:
    """Apply rate limiting to *lines* if --rate-limit is set.

    Returns the (possibly filtered) list of lines.
    Raises ValueError for bad --rate-window specs.
    """
    if not getattr(args, "rate_limit", None):
        return lines

    window_seconds = parse_window(getattr(args, "rate_window", "1s") or "1s")
    return list(ratelimit_lines(lines, args.rate_limit, window_seconds))
