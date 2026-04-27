"""CLI integration for the heatmap feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.heatmap import build_heatmap, format_heatmap


def add_heatmap_args(parser: argparse.ArgumentParser) -> None:
    """Register --heatmap, --heatmap-bucket, --heatmap-pattern, --heatmap-width flags."""
    parser.add_argument(
        "--heatmap",
        action="store_true",
        default=False,
        help="Print a time-bucket activity heatmap and exit.",
    )
    parser.add_argument(
        "--heatmap-bucket",
        choices=["minute", "hour"],
        default="minute",
        dest="heatmap_bucket",
        help="Bucket granularity for the heatmap (default: minute).",
    )
    parser.add_argument(
        "--heatmap-pattern",
        default=None,
        dest="heatmap_pattern",
        metavar="REGEX",
        help="Only count lines matching REGEX in heatmap buckets.",
    )
    parser.add_argument(
        "--heatmap-width",
        type=int,
        default=40,
        dest="heatmap_width",
        metavar="N",
        help="Width of the bar chart (default: 40).",
    )


def apply_heatmap(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """If --heatmap is set, print the heatmap to *out* and return an empty list.

    Otherwise return *lines* unchanged.
    """
    if not getattr(args, "heatmap", False):
        return lines

    if out is None:  # pragma: no cover
        out = sys.stdout

    result = build_heatmap(
        lines,
        bucket_size=args.heatmap_bucket,
        label_pattern=args.heatmap_pattern,
    )
    rows = format_heatmap(result, bar_width=args.heatmap_width)
    for row in rows:
        out.write(row)
    return []
