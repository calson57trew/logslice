"""Context window extraction: include N lines before/after each matched line."""

from typing import Iterable, Iterator, List, Optional
from collections import deque

from logslice.parser import extract_timestamp


def context_window(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
    predicate=None,
) -> Iterator[str]:
    """Yield lines that match *predicate* plus up to *before* preceding lines
    and *after* following lines.  Overlapping windows are merged without
    duplicating lines.

    If *predicate* is None every line is yielded unchanged.
    """
    if predicate is None:
        yield from lines
        return

    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative integers")

    buf: deque[str] = deque(maxlen=before + 1)  # ring buffer of recent lines
    pending: List[str] = []   # lines queued for "after" emission
    after_remaining: int = 0
    emitted_index: int = -1   # global index of last emitted line
    all_lines: List[str] = list(lines)

    i = 0
    while i < len(all_lines):
        line = all_lines[i]
        if predicate(line):
            # Emit before-context (may overlap with already-emitted lines)
            start = max(0, i - before)
            for j in range(start, i):
                if j > emitted_index:
                    yield all_lines[j]
                    emitted_index = j
            # Emit the matched line itself
            if i > emitted_index:
                yield line
                emitted_index = i
            # Emit after-context eagerly
            for j in range(i + 1, min(i + after + 1, len(all_lines))):
                if j > emitted_index:
                    yield all_lines[j]
                    emitted_index = j
        i += 1


def count_context_lines(
    lines: Iterable[str],
    before: int = 0,
    after: int = 0,
    predicate=None,
) -> int:
    """Return the number of lines that would be emitted by context_window."""
    return sum(1 for _ in context_window(lines, before, after, predicate))
