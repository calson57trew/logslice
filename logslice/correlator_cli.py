"""CLI integration for the correlator feature."""

from __future__ import annotations

import sys
from typing import List, Optional

from logslice.correlator import (
    compile_id_pattern,
    correlate_lines,
    format_correlation,
)


def add_correlate_args(parser) -> None:  # type: ignore[no-untyped-def]
    """Register --correlate-* flags on *parser*."""
    grp = parser.add_argument_group("correlation")
    grp.add_argument(
        "--correlate-id",
        metavar="PATTERN",
        default=None,
        help=(
            "Regex with one capturing group used to extract a correlation ID "
            "(e.g. request-id, trace-id) from each log line."
        ),
    )
    grp.add_argument(
        "--correlate-key",
        metavar="ID",
        default=None,
        help="When set, only emit lines belonging to this correlation ID.",
    )
    grp.add_argument(
        "--correlate-unmatched",
        action="store_true",
        default=False,
        help="Include lines that carry no correlation ID in the output.",
    )
    grp.add_argument(
        "--correlate-report",
        action="store_true",
        default=False,
        help="Replace output with a grouped correlation report.",
    )


def apply_correlation(
    args,  # type: ignore[no-untyped-def]
    lines: List[str],
    out=None,
) -> List[str]:
    """Apply correlation filtering/reporting to *lines* according to *args*.

    Returns the (possibly filtered) list of lines.  When *--correlate-report*
    is set the formatted report is written to *out* (default: stdout) and an
    empty list is returned so downstream stages receive nothing.
    """
    if out is None:
        out = sys.stdout

    pattern_str: Optional[str] = getattr(args, "correlate_id", None)
    if not pattern_str:
        return lines

    pattern = compile_id_pattern(pattern_str)
    include_unmatched: bool = getattr(args, "correlate_unmatched", False)
    groups = correlate_lines(lines, pattern, include_unmatched=include_unmatched)

    filter_key: Optional[str] = getattr(args, "correlate_key", None)
    if filter_key is not None:
        if filter_key in groups:
            lines = groups[filter_key].lines
        else:
            lines = []

    if getattr(args, "correlate_report", False):
        for rendered in format_correlation(groups):
            out.write(rendered)
        return []

    if filter_key is not None:
        return lines

    # No key filter and no report — return lines that matched any ID.
    result: List[str] = []
    for group in groups.values():
        result.extend(group.lines)
    return result
