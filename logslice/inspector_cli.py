"""CLI integration for the inspector module."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.inspector import format_inspect, inspect_lines


def add_inspect_args(parser: argparse.ArgumentParser) -> None:
    """Register --inspect and --inspect-samples flags on *parser*."""
    parser.add_argument(
        "--inspect",
        action="store_true",
        default=False,
        help="Print a structural summary of the log lines and exit.",
    )
    parser.add_argument(
        "--inspect-samples",
        type=int,
        default=5,
        metavar="N",
        dest="inspect_samples",
        help="Number of sample lines to collect during inspection (default: 5).",
    )


def apply_inspect(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """If --inspect is set, print the report to *out* and return an empty list.

    Otherwise return *lines* unchanged.
    """
    if not getattr(args, "inspect", False):
        return lines

    if out is None:  # pragma: no cover
        out = sys.stdout

    samples = getattr(args, "inspect_samples", 5)
    result = inspect_lines(iter(lines), max_samples=samples)
    report = format_inspect(result)
    out.write(report)

    if result.sample_lines:
        out.write("\nsamples:\n")
        for s in result.sample_lines:
            out.write(f"  {s}\n")

    return []
