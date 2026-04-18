"""Split log lines into chunks by size or pattern boundary."""
from __future__ import annotations

import re
from typing import Iterator, List


def split_by_size(lines: List[str], chunk_size: int) -> Iterator[List[str]]:
    """Yield successive chunks of at most chunk_size lines."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    for i in range(0, len(lines), chunk_size):
        yield lines[i : i + chunk_size]


def split_by_pattern(
    lines: List[str], pattern: str, flags: int = re.IGNORECASE
) -> Iterator[List[str]]:
    """Yield chunks where each chunk starts at a line matching *pattern*.

    Lines before the first match are yielded as a leading chunk (if non-empty).
    """
    compiled = re.compile(pattern, flags)
    current: List[str] = []
    for line in lines:
        if compiled.search(line) and current:
            yield current
            current = []
        current.append(line)
    if current:
        yield current


def chunk_count(lines: List[str], chunk_size: int) -> int:
    """Return number of chunks produced by split_by_size."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    return (len(lines) + chunk_size - 1) // chunk_size
