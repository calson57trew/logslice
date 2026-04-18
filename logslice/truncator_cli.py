"""CLI integration for line truncation."""

import argparse
from typing import List, Iterator

from logslice.truncator import truncate_lines, DEFAULT_MAX_LENGTH


def add_truncate_args(parser: argparse.ArgumentParser) -> None:
    """Register truncation flags on an existing argument parser."""
    group = parser.add_argument_group("truncation")
    group.add_argument(
        "--max-line-length",
        type=int,
        default=None,
        metavar="N",
        help=f"Truncate lines longer than N characters (default: no truncation)",
    )
    group.add_argument(
        "--truncate-only-long",
        action="store_true",
        default=False,
        help="When truncating, only emit lines that were actually truncated",
    )


def apply_truncation(
    args: argparse.Namespace, lines: List[str]
) -> List[str]:
    """Apply truncation settings from parsed args to a list of lines.

    Returns the original list unchanged if --max-line-length is not set.
    """
    if args.max_line_length is None:
        return lines
    truncated = truncate_lines(
        lines,
        max_length=args.max_line_length,
        only_long=args.truncate_only_long,
    )
    return list(truncated)
