"""chunker_cli.py – CLI integration for the time-bucket chunker."""
from __future__ import annotations

import argparse
from typing import IO, Iterable, List

from logslice.chunker import chunk_by_time


def add_chunk_args(parser: argparse.ArgumentParser) -> None:
    """Register --chunk-minutes flag on *parser*."""
    parser.add_argument(
        "--chunk-minutes",
        metavar="N",
        type=int,
        default=None,
        help="Split output into time buckets of N minutes (default: disabled).",
    )
    parser.add_argument(
        "--chunk-header",
        action="store_true",
        default=False,
        help="Print a header line before each time bucket.",
    )


def apply_chunking(
    args: argparse.Namespace,
    lines: Iterable[str],
    out: IO[str],
) -> List[str]:
    """If ``--chunk-minutes`` is set, write bucketed output to *out* and
    return an empty list (output already consumed).  Otherwise return
    *lines* unchanged as a list for downstream processing."""
    bucket_minutes: int | None = getattr(args, "chunk_minutes", None)
    show_header: bool = getattr(args, "chunk_header", False)

    if not bucket_minutes:
        return list(lines)

    collected: List[str] = list(lines)
    result: List[str] = []

    for chunk in chunk_by_time(collected, bucket_minutes):
        if show_header:
            out.write(f"=== {chunk.bucket} ===\n")
        for line in chunk.lines:
            out.write(line if line.endswith("\n") else line + "\n")
        result.extend(chunk.lines)

    return result
