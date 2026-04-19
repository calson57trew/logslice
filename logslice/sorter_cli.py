"""CLI helpers for the sorter feature."""

import argparse
from typing import List
from logslice.sorter import sort_lines, count_out_of_order


def add_sort_args(parser: argparse.ArgumentParser) -> None:
    """Register --sort and --sort-reverse flags on *parser*."""
    group = parser.add_argument_group("sorting")
    group.add_argument(
        "--sort",
        action="store_true",
        default=False,
        help="Sort output lines by timestamp (ascending).",
    )
    group.add_argument(
        "--sort-reverse",
        action="store_true",
        default=False,
        help="Sort output lines by timestamp (descending).",
    )
    group.add_argument(
        "--check-order",
        action="store_true",
        default=False,
        help="Print the number of out-of-order lines and exit.",
    )


def apply_sorting(
    args: argparse.Namespace,
    lines: List[str],
) -> List[str]:
    """Apply sorting to *lines* based on parsed *args*.

    Returns the (possibly reordered) list of lines.
    If --check-order is set, prints a diagnostic and returns lines unchanged.
    """
    if args.check_order:
        n = count_out_of_order(lines)
        print(f"Out-of-order lines: {n}")
        return lines

    if args.sort_reverse:
        return sort_lines(lines, reverse=True)

    if args.sort:
        return sort_lines(lines, reverse=False)

    return lines
