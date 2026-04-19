"""CLI integration for log diffing."""
from __future__ import annotations
import argparse
from typing import Iterable, Iterator
from logslice.differ import diff_logs, format_diff


def add_diff_args(parser: argparse.ArgumentParser) -> None:
    """Register --diff-file and --diff-mode flags."""
    parser.add_argument(
        "--diff-file",
        metavar="FILE",
        default=None,
        help="Path to a second log file to diff against the primary input.",
    )
    parser.add_argument(
        "--diff-mode",
        choices=["all", "left", "right", "common"],
        default="all",
        help="Which diff sections to emit (default: all).",
    )


def apply_diff(
    args: argparse.Namespace,
    lines: Iterable[str],
) -> Iterator[str]:
    """If --diff-file is set, diff lines against that file and yield result."""
    if not args.diff_file:
        yield from lines
        return

    left = list(lines)
    try:
        with open(args.diff_file, "r", encoding="utf-8") as fh:
            right = fh.readlines()
    except OSError as exc:
        raise SystemExit(f"logslice: cannot open diff file: {exc}") from exc

    result = diff_logs(left, right)
    yield from format_diff(result, mode=args.diff_mode)
