"""compressor.py — line-level run-length compression for repeated log lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List

from logslice.deduplicator import normalize_line


@dataclass
class CompressedLine:
    line: str
    count: int = 1

    def render(self, show_count: bool = True) -> str:
        """Return the line, optionally prefixed with a repeat count."""
        stripped = self.line.rstrip("\n")
        if show_count and self.count > 1:
            return f"[x{self.count}] {stripped}\n"
        return self.line if self.line.endswith("\n") else self.line + "\n"


def compress_lines(
    lines: List[str],
    *,
    consecutive_only: bool = True,
    min_repeat: int = 2,
) -> Iterator[CompressedLine]:
    """Yield CompressedLine objects, collapsing repeated lines.

    Args:
        lines: Input log lines.
        consecutive_only: When True only collapse consecutive duplicates;
            when False collapse all duplicates globally.
        min_repeat: Minimum repeat count before collapsing (default 2).
    """
    if min_repeat < 2:
        raise ValueError("min_repeat must be >= 2")

    if consecutive_only:
        yield from _compress_consecutive(lines, min_repeat)
    else:
        yield from _compress_global(lines, min_repeat)


def _compress_consecutive(
    lines: List[str], min_repeat: int
) -> Iterator[CompressedLine]:
    pending: CompressedLine | None = None
    for line in lines:
        key = normalize_line(line)
        if pending is None:
            pending = CompressedLine(line=line, count=1)
            pending._key = key  # type: ignore[attr-defined]
        elif key == pending._key:  # type: ignore[attr-defined]
            pending.count += 1
        else:
            if pending.count < min_repeat:
                for _ in range(pending.count):
                    yield CompressedLine(line=pending.line, count=1)
            else:
                yield pending
            pending = CompressedLine(line=line, count=1)
            pending._key = key  # type: ignore[attr-defined]
    if pending is not None:
        if pending.count < min_repeat:
            for _ in range(pending.count):
                yield CompressedLine(line=pending.line, count=1)
        else:
            yield pending


def _compress_global(
    lines: List[str], min_repeat: int
) -> Iterator[CompressedLine]:
    from collections import Counter, OrderedDict

    counts: Counter[str] = Counter(normalize_line(l) for l in lines)
    seen: set[str] = set()
    for line in lines:
        key = normalize_line(line)
        if counts[key] >= min_repeat:
            if key not in seen:
                seen.add(key)
                yield CompressedLine(line=line, count=counts[key])
        else:
            yield CompressedLine(line=line, count=1)


def count_compressed(lines: List[str], **kwargs) -> int:
    """Return the number of lines saved by compression."""
    original = len(lines)
    compressed = sum(1 for _ in compress_lines(lines, **kwargs))
    return original - compressed
