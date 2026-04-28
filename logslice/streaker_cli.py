"""streaker_cli.py – CLI integration for the streak-detection feature."""
from __future__ import annotations

import sys
from typing import List

from logslice.streaker import (
    Streak,
    compile_predicate,
    find_streaks,
    format_streak_summary,
)


def add_streak_args(parser) -> None:  # type: ignore[type-arg]
    """Register streak-related flags on *parser*."""
    grp = parser.add_argument_group("streak detection")
    grp.add_argument(
        "--streak-pattern",
        metavar="PATTERN",
        default=None,
        help="Regex pattern; report consecutive runs of matching lines.",
    )
    grp.add_argument(
        "--streak-min",
        metavar="N",
        type=int,
        default=2,
        help="Minimum streak length to report (default: 2).",
    )
    grp.add_argument(
        "--streak-case-sensitive",
        action="store_true",
        default=False,
        help="Make --streak-pattern case-sensitive.",
    )
    grp.add_argument(
        "--streak-summary-only",
        action="store_true",
        default=False,
        help="Print streak summary to stderr and suppress matched lines from output.",
    )


def apply_streaking(
    args,  # type: ignore[type-arg]
    lines: List[str],
    out=None,
) -> List[str]:
    """Apply streak detection according to *args*; return lines unchanged.

    When ``--streak-pattern`` is set the streaks are collected and a summary
    is written to *out* (defaults to ``sys.stderr``).  The original *lines*
    list is always returned so downstream pipeline stages are unaffected.
    """
    if out is None:
        out = sys.stderr

    pattern: str | None = getattr(args, "streak_pattern", None)
    if not pattern:
        return lines

    min_len: int = getattr(args, "streak_min", 2)
    case_sensitive: bool = getattr(args, "streak_case_sensitive", False)
    summary_only: bool = getattr(args, "streak_summary_only", False)

    predicate = compile_predicate(pattern, ignore_case=not case_sensitive)
    streaks: List[Streak] = list(find_streaks(lines, predicate, min_length=min_len))

    summary = format_streak_summary(streaks)
    print(summary, file=out)

    if summary_only:
        return []
    return lines
