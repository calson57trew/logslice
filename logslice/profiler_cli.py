"""CLI integration for the log profiler."""
from __future__ import annotations

import argparse
from datetime import timedelta
from typing import List, Optional

from logslice.profiler import format_profile, profile_lines


def add_profile_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("profiling")
    grp.add_argument(
        "--profile",
        action="store_true",
        default=False,
        help="Print a timing profile of the log stream and exit.",
    )
    grp.add_argument(
        "--profile-gap",
        metavar="SECONDS",
        type=float,
        default=None,
        help="Only report gaps larger than this many seconds (default: all gaps).",
    )
    grp.add_argument(
        "--profile-show-gaps",
        action="store_true",
        default=False,
        help="List each detected gap in the profile output.",
    )


def apply_profile(
    args: argparse.Namespace,
    lines: List[str],
    out,
) -> Optional[List[str]]:
    """If --profile is set, print profile to *out* and return None (halt pipeline).
    Otherwise return lines unchanged."""
    if not getattr(args, "profile", False):
        return lines

    threshold = None
    gap_sec = getattr(args, "profile_gap", None)
    if gap_sec is not None:
        threshold = timedelta(seconds=gap_sec)

    result = profile_lines(lines, gap_threshold=threshold)
    out.write(format_profile(result) + "\n")

    if getattr(args, "profile_show_gaps", False) and result.gaps:
        out.write("\nGaps:\n")
        for start, end, dur in result.gaps:
            out.write(f"  {start} -> {end}  ({dur})\n")

    return None
