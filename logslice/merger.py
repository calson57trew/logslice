"""Merge and sort log lines from multiple sources by timestamp."""

import heapq
from typing import Iterable, Iterator, List, Tuple
from logslice.parser import extract_timestamp
from datetime import datetime


def _source_lines(source_id: int, lines: Iterable[str]):
    """Yield (timestamp_or_none, source_id, line) tuples."""
    for line in lines:
        ts = extract_timestamp(line)
        yield (ts, source_id, line)


def merge_logs(
    sources: List[Iterable[str]],
    sort: bool = True,
    label: bool = False,
    labels: List[str] = None,
) -> Iterator[str]:
    """Merge log lines from multiple sources.

    If sort=True, interleave lines by timestamp (lines without timestamps
    are emitted before timestamped lines in their natural order).
    If label=True, prepend each line with its source label.
    """
    if not sources:
        return

    if labels is None:
        labels = [f"source{i}" for i in range(len(sources))]

    def _prefix(line: str, idx: int) -> str:
        if label:
            return f"[{labels[idx]}] {line}"
        return line

    if not sort:
        for idx, source in enumerate(sources):
            for line in source:
                yield _prefix(line, idx)
        return

    # Separate timestamped from non-timestamped per source
    heap: List[Tuple] = []
    untimed: List[Tuple[int, str]] = []

    for idx, source in enumerate(sources):
        for line in source:
            ts = extract_timestamp(line)
            if ts is not None:
                heapq.heappush(heap, (ts, idx, line))
            else:
                untimed.append((idx, line))

    for idx, line in untimed:
        yield _prefix(line, idx)

    while heap:
        ts, idx, line = heapq.heappop(heap)
        yield _prefix(line, idx)


def merge_files(paths: List[str], sort: bool = True, label: bool = False) -> Iterator[str]:
    """Open files and merge their log lines."""
    handles = [open(p, "r", encoding="utf-8", errors="replace") for p in paths]
    try:
        all_lines = [list(h) for h in handles]
        yield from merge_logs(all_lines, sort=sort, label=label, labels=paths)
    finally:
        for h in handles:
            h.close()
