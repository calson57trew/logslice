"""CLI helpers for the --summarize flag."""

from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.summarizer import summarize_lines, format_summary


def add_summarize_args(parser: argparse.ArgumentParser) -> None:
    """Register --summarize flag on an existing ArgumentParser."""
    parser.add_argument(
        "--summarize",
        action="store_true",
        default=False,
        help="Print a summary of log levels and timestamps instead of log lines.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        default=False,
        help="Suppress log output; print only the summary (implies --summarize).",
    )


def apply_summarize(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Optionally summarize lines.  Returns lines to pass downstream.

    If --summary-only, writes summary to *out* and returns empty list.
    If --summarize, writes summary to *out* and returns original lines.
    Otherwise returns lines unchanged.
    """
    if out is None:
        out = sys.stdout

    summarize = getattr(args, "summarize", False)
    summary_only = getattr(args, "summary_only", False)

    if summarize or summary_only:
        s = summarize_lines(lines)
        for row in format_summary(s):
            out.write(row + "\n")

    if summary_only:
        return []
    return lines
