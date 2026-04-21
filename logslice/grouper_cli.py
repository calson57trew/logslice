"""CLI integration for the grouper feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.grouper import (
    GroupResult,
    compile_group_rules,
    count_grouped,
    group_by_hour,
    group_by_pattern,
)


def add_group_args(parser: argparse.ArgumentParser) -> None:
    """Register grouping flags onto an existing ArgumentParser."""
    grp = parser.add_argument_group("grouping")
    grp.add_argument(
        "--group",
        metavar="PATTERN:LABEL",
        action="append",
        dest="group_rules",
        default=[],
        help="Group lines matching PATTERN into LABEL bucket (repeatable).",
    )
    grp.add_argument(
        "--group-by-hour",
        action="store_true",
        default=False,
        help="Group lines into hourly buckets based on their timestamps.",
    )
    grp.add_argument(
        "--group-multi",
        action="store_true",
        default=False,
        help="Allow a line to appear in multiple groups.",
    )
    grp.add_argument(
        "--group-summary",
        action="store_true",
        default=False,
        help="Print group counts to stderr instead of passing lines through.",
    )


def apply_grouping(
    args: argparse.Namespace, lines: List[str]
) -> List[str]:
    """Apply grouping based on parsed CLI args; returns lines unchanged if no
    grouping flags are active, otherwise prints group summary to stderr."""
    has_pattern_rules = bool(getattr(args, "group_rules", []))
    by_hour = getattr(args, "group_by_hour", False)

    if not has_pattern_rules and not by_hour:
        return lines

    if by_hour:
        result = group_by_hour(lines)
    else:
        raw_rules = []
        for spec in args.group_rules:
            if ":" not in spec:
                raise ValueError(f"--group value must be PATTERN:LABEL, got: {spec!r}")
            pattern, _, label = spec.partition(":")
            raw_rules.append((pattern, label))
        compiled = compile_group_rules(raw_rules)
        result = group_by_pattern(lines, compiled, multi=args.group_multi)

    counts = count_grouped(result)
    for label, n in sorted(counts.items()):
        print(f"[group] {label}: {n} line(s)", file=sys.stderr)

    if getattr(args, "group_summary", False):
        return []

    # Return lines in group order, ungrouped last
    out: List[str] = []
    for label in sorted(result.groups):
        out.extend(result.groups[label])
    out.extend(result.ungrouped)
    return out
