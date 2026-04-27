"""CLI integration for the histogram feature."""
from __future__ import annotations

import re
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from .histogram import build_histogram, format_histogram


def add_histogram_args(parser: ArgumentParser) -> None:
    """Register --histogram-* flags on *parser*."""
    g = parser.add_argument_group("histogram")
    g.add_argument(
        "--histogram",
        metavar="PATTERN",
        nargs="?",
        const="",
        default=None,
        help="Build a frequency histogram. Optionally supply a capturing regex.",
    )
    g.add_argument(
        "--histogram-bar-width",
        type=int,
        default=40,
        metavar="N",
        help="Width of histogram bars (default: 40).",
    )
    g.add_argument(
        "--histogram-no-other",
        action="store_true",
        default=False,
        help="Omit lines that do not match any bucket.",
    )
    g.add_argument(
        "--histogram-only",
        action="store_true",
        default=False,
        help="Write histogram and suppress normal output.",
    )


def apply_histogram(
    args: Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """If histogram flags are set, build and emit the histogram report."""
    if args.histogram is None:
        return lines

    if out is None:  # pragma: no cover
        out = sys.stderr

    pattern: re.Pattern | None = None
    if args.histogram:
        try:
            pattern = re.compile(args.histogram)
        except re.error as exc:
            raise ValueError(f"Invalid histogram pattern: {exc}") from exc

    result = build_histogram(
        lines,
        pattern=pattern,
        bucket_other=not args.histogram_no_other,
    )
    report = format_histogram(result, bar_width=args.histogram_bar_width)
    for row in report:
        out.write(row)

    return [] if args.histogram_only else lines
