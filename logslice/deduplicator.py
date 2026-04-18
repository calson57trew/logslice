"""Deduplication support for log slices."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Iterator


def normalize_line(line: str) -> str:
    """Strip timestamps and whitespace for comparison purposes."""
    import re
    # Remove common timestamp patterns before comparing
    line = re.sub(
        r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\s*',
        '',
        line,
    )
    return line.strip()


def deduplicate_lines(
    lines: Iterable[str],
    *,
    consecutive_only: bool = False,
    max_cache: int = 1024,
) -> Iterator[str]:
    """Yield lines with duplicates removed.

    Args:
        lines: Input log lines.
        consecutive_only: If True, only suppress immediately repeated lines.
        max_cache: Maximum number of normalized lines to remember (LRU eviction).
    """
    if consecutive_only:
        prev: str | None = None
        for line in lines:
            key = normalize_line(line)
            if key != prev:
                yield line
                prev = key
    else:
        seen: OrderedDict[str, None] = OrderedDict()
        for line in lines:
            key = normalize_line(line)
            if key in seen:
                seen.move_to_end(key)
                continue
            seen[key] = None
            if len(seen) > max_cache:
                seen.popitem(last=False)
            yield line


def count_duplicates(lines: Iterable[str], *, consecutive_only: bool = False) -> int:
    """Return the number of lines that would be suppressed by deduplication."""
    original = list(lines)
    deduped = list(deduplicate_lines(original, consecutive_only=consecutive_only))
    return len(original) - len(deduped)
