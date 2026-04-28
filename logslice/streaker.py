"""streaker.py – detect and report consecutive-run streaks in log lines.

A "streak" is a maximal consecutive sequence of lines that all match a given
predicate (e.g. the same log level, or a fixed pattern).  The module exposes
helpers to find streaks, measure their length, and summarise the longest ones.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


@dataclass
class Streak:
    """A consecutive run of matching log lines."""
    lines: List[str] = field(default_factory=list)
    start_ts: Optional[str] = None
    end_ts: Optional[str] = None

    def __len__(self) -> int:  # noqa: D105
        return len(self.lines)


def compile_predicate(pattern: str, ignore_case: bool = True) -> Callable[[str], bool]:
    """Return a callable that tests whether a line matches *pattern*."""
    flags = re.IGNORECASE if ignore_case else 0
    rx = re.compile(pattern, flags)
    return lambda line: bool(rx.search(line))


def find_streaks(
    lines: Iterable[str],
    predicate: Callable[[str], bool],
    min_length: int = 2,
) -> Iterator[Streak]:
    """Yield every streak of consecutive matching lines with length >= *min_length*."""
    current: List[str] = []

    def _flush() -> Optional[Streak]:
        if len(current) >= min_length:
            ts_first = extract_timestamp(current[0])
            ts_last = extract_timestamp(current[-1])
            return Streak(
                lines=list(current),
                start_ts=ts_first,
                end_ts=ts_last,
            )
        return None

    for line in lines:
        if predicate(line):
            current.append(line)
        else:
            result = _flush()
            if result is not None:
                yield result
            current.clear()

    result = _flush()
    if result is not None:
        yield result


def longest_streak(streaks: Iterable[Streak]) -> Optional[Streak]:
    """Return the longest streak, or *None* if the iterable is empty."""
    best: Optional[Streak] = None
    for s in streaks:
        if best is None or len(s) > len(best):
            best = s
    return best


def count_streaks(streaks: Iterable[Streak]) -> int:
    """Return the total number of streaks."""
    return sum(1 for _ in streaks)


def format_streak_summary(streaks: List[Streak]) -> str:
    """Return a human-readable summary of all streaks."""
    if not streaks:
        return "No streaks found."
    lines = [f"Streaks found: {len(streaks)}"]
    for i, s in enumerate(streaks, 1):
        ts_info = ""
        if s.start_ts:
            ts_info = f"  [{s.start_ts} … {s.end_ts or s.start_ts}]"
        lines.append(f"  #{i}: {len(s)} lines{ts_info}")
    return "\n".join(lines)
