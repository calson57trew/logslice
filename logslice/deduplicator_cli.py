"""CLI integration for the deduplicator module."""
from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import List

from logslice.deduplicator import deduplicate_lines, count_duplicates


def add_dedup_args(parser: ArgumentParser) -> None:
    """Register deduplication flags on *parser*."""
    group = parser.add_argument_group("deduplication")
    group.add_argument(
        "--dedup",
        action="store_true",
        default=False,
        help="Remove duplicate log lines.",
    )
    group.add_argument(
        "--dedup-consecutive",
        action="store_true",
        default=False,
        help="Suppress only consecutive duplicate lines (not global).",
    )
    group.add_argument(
        "--dedup-summary",
        action="store_true",
        default=False,
        help="Print a summary of how many duplicates were removed.",
    )


def apply_deduplication(
    args: Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Apply deduplication to *lines* based on *args*.

    Returns the (possibly deduplicated) list of lines.  When
    ``--dedup-summary`` is set a one-line report is written to *out*
    (defaults to stdout).
    """
    import sys

    if out is None:
        out = sys.stdout

    if not (getattr(args, "dedup", False) or getattr(args, "dedup_consecutive", False)):
        return lines

    consecutive_only: bool = getattr(args, "dedup_consecutive", False)
    result = deduplicate_lines(lines, consecutive_only=consecutive_only)

    if getattr(args, "dedup_summary", False):
        removed = count_duplicates(lines, result)
        mode = "consecutive" if consecutive_only else "global"
        out.write(f"[dedup] removed {removed} duplicate(s) ({mode} mode)\n")

    return result
