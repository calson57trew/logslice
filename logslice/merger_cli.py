"""CLI helpers for the merge feature."""

import argparse
from typing import List


def add_merge_args(parser: argparse.ArgumentParser) -> None:
    """Add merge-related arguments to an argument parser."""
    parser.add_argument(
        "--merge",
        nargs="+",
        metavar="FILE",
        help="Additional log files to merge with the primary input.",
    )
    parser.add_argument(
        "--merge-sort",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Sort merged lines by timestamp (default: True).",
    )
    parser.add_argument(
        "--merge-label",
        action="store_true",
        default=False,
        help="Prefix each line with its source filename.",
    )


def apply_merge(args: argparse.Namespace, primary_lines: List[str]) -> List[str]:
    """Apply merge logic based on parsed CLI args.

    Returns merged lines if --merge files are specified, otherwise
    returns primary_lines unchanged.
    """
    if not getattr(args, "merge", None):
        return primary_lines

    from logslice.merger import merge_logs

    extra_sources = []
    for path in args.merge:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                extra_sources.append(list(fh))
        except OSError as exc:
            raise SystemExit(f"logslice: cannot open merge file '{path}': {exc}") from exc

    all_sources = [primary_lines] + extra_sources
    labels = ["<stdin>"] + list(args.merge)

    return list(
        merge_logs(
            all_sources,
            sort=args.merge_sort,
            label=args.merge_label,
            labels=labels,
        )
    )
