"""CLI integration for pattern-counting feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.pattern_counter import count_patterns, format_pattern_counts


def add_pattern_count_args(parser: argparse.ArgumentParser) -> None:
    """Register --count-pattern and related flags on *parser*."""
    parser.add_argument(
        "--count-pattern",
        metavar="PATTERN",
        dest="count_patterns",
        action="append",
        default=[],
        help="Count lines matching PATTERN (may be repeated).",
    )
    parser.add_argument(
        "--count-ignore-case",
        action="store_true",
        default=False,
        help="Match patterns case-insensitively when counting.",
    )
    parser.add_argument(
        "--count-examples",
        action="store_true",
        default=False,
        help="Show an example matching line for each pattern.",
    )
    parser.add_argument(
        "--count-only",
        action="store_true",
        default=False,
        help="Suppress normal output; print only the pattern-count report.",
    )


def apply_pattern_count(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Run pattern counting if --count-pattern flags are present.

    Writes the report to *out* (defaults to sys.stderr so normal output is
    unaffected).  Returns the original *lines* list unchanged unless
    ``--count-only`` is set, in which case an empty list is returned so
    downstream stages emit nothing.
    """
    if not getattr(args, "count_patterns", None):
        return lines

    if out is None:
        out = sys.stderr

    result = count_patterns(
        lines,
        patterns=args.count_patterns,
        ignore_case=getattr(args, "count_ignore_case", False),
    )
    report = format_pattern_counts(
        result,
        show_examples=getattr(args, "count_examples", False),
    )
    out.write(report + "\n")

    if getattr(args, "count_only", False):
        return []
    return lines
