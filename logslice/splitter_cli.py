"""CLI integration for the splitter module."""
from __future__ import annotations

import argparse
from typing import List, Optional

from logslice.splitter import split_by_size, split_by_pattern


def add_split_args(parser: argparse.ArgumentParser) -> None:
    """Register splitter flags on *parser*."""
    grp = parser.add_argument_group("splitting")
    grp.add_argument(
        "--split-size",
        type=int,
        default=None,
        metavar="N",
        help="Split output into chunks of N lines each.",
    )
    grp.add_argument(
        "--split-pattern",
        default=None,
        metavar="PATTERN",
        help="Split output into chunks starting at lines matching PATTERN.",
    )


def apply_split(
    lines: List[str], args: argparse.Namespace
) -> List[List[str]]:
    """Return list of chunks according to split flags on *args*.

    If neither flag is set returns the original lines wrapped in a single chunk.
    """
    split_size: Optional[int] = getattr(args, "split_size", None)
    split_pattern: Optional[str] = getattr(args, "split_pattern", None)

    if split_size is not None:
        return list(split_by_size(lines, split_size))
    if split_pattern is not None:
        return list(split_by_pattern(lines, split_pattern))
    return [lines]
