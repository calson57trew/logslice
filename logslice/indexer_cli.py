"""CLI integration for the log indexer."""
from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.indexer import build_index, load_index, save_index, seek_to_timestamp, count_indexed


def add_index_args(parser: argparse.ArgumentParser) -> None:
    """Register --index-build, --index-file, and --index-seek flags."""
    parser.add_argument(
        "--index-build",
        metavar="LOG_FILE",
        default=None,
        help="Build a byte-offset index for LOG_FILE and write it to --index-file.",
    )
    parser.add_argument(
        "--index-file",
        metavar="INDEX_FILE",
        default=None,
        help="Path to the index file (used with --index-build or --index-seek).",
    )
    parser.add_argument(
        "--index-seek",
        metavar="TIMESTAMP",
        default=None,
        help="Print the byte offset of the first line with timestamp >= TIMESTAMP.",
    )
    parser.add_argument(
        "--index-stats",
        action="store_true",
        default=False,
        help="Print summary statistics for the loaded index.",
    )


def apply_index(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Execute index sub-commands; return *lines* unchanged."""
    if out is None:  # pragma: no cover
        out = sys.stdout

    if args.index_build:
        index = build_index(args.index_build)
        dest = args.index_file or (args.index_build + ".idx")
        save_index(index, dest)
        stats = count_indexed(index)
        out.write(
            f"Index written to {dest}: "
            f"{stats['total']} lines, {stats['timed']} timed.\n"
        )

    if args.index_seek:
        if not args.index_file:
            out.write("--index-file is required for --index-seek\n")
            return lines
        index = load_index(args.index_file)
        offset = seek_to_timestamp(index, args.index_seek)
        if offset is None:
            out.write(f"No entry found for timestamp >= {args.index_seek}\n")
        else:
            out.write(f"{offset}\n")

    if args.index_stats:
        if not args.index_file:
            out.write("--index-file is required for --index-stats\n")
            return lines
        index = load_index(args.index_file)
        stats = count_indexed(index)
        for key, val in stats.items():
            out.write(f"{key}: {val}\n")

    return lines
