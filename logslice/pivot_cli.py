"""pivot_cli.py — CLI integration for the pivot / frequency-bucketing feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.pivot import build_pivot, format_pivot


def add_pivot_args(parser: argparse.ArgumentParser) -> None:
    """Register --pivot-pattern, --pivot-bucket, --pivot-top, --pivot-ignore-case."""
    grp = parser.add_argument_group("pivot (frequency bucketing)")
    grp.add_argument(
        "--pivot-pattern",
        metavar="REGEX",
        default=None,
        help="Pattern to count per time bucket.",
    )
    grp.add_argument(
        "--pivot-bucket",
        metavar="SECONDS",
        type=int,
        default=60,
        help="Bucket width in seconds (default: 60).",
    )
    grp.add_argument(
        "--pivot-top",
        metavar="N",
        type=int,
        default=0,
        help="Show only the top N busiest buckets (0 = all).",
    )
    grp.add_argument(
        "--pivot-ignore-case",
        action="store_true",
        default=False,
        help="Case-insensitive pattern matching for pivot.",
    )


def apply_pivot(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """If --pivot-pattern is set, print the pivot table and return original lines.

    The pivot report is written to *out* (defaults to stdout).  The original
    line list is always returned unchanged so downstream stages still work.
    """
    if not getattr(args, "pivot_pattern", None):
        return lines

    if out is None:  # pragma: no cover
        out = sys.stdout

    table = build_pivot(
        lines,
        pattern=args.pivot_pattern,
        bucket_size=args.pivot_bucket,
        ignore_case=args.pivot_ignore_case,
    )
    report = format_pivot(table, top_n=args.pivot_top)
    for row in report:
        out.write(row + "\n")

    return lines
