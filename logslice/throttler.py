"""Rate-based line throttling: keep at most N lines per time window."""

from __future__ import annotations

from datetime import timedelta
from typing import Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


def throttle_lines(
    lines: Iterable[str],
    max_per_window: int,
    window_seconds: float = 1.0,
) -> Iterator[str]:
    """Yield at most *max_per_window* timestamped lines per *window_seconds*.

    Lines without a timestamp are always passed through unchanged.
    Continuation lines (no timestamp) travel with their parent.
    """
    if max_per_window < 1:
        raise ValueError("max_per_window must be >= 1")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")

    window = timedelta(seconds=window_seconds)
    window_start: Optional[object] = None  # datetime
    count_in_window: int = 0
    emit_current: bool = True  # whether the current timed block is emitted

    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            # Continuation or header-less line — follow parent decision
            if emit_current:
                yield line
            continue

        # New timestamped line
        if window_start is None or (ts - window_start) >= window:
            # Start a fresh window
            window_start = ts
            count_in_window = 0

        count_in_window += 1
        emit_current = count_in_window <= max_per_window
        if emit_current:
            yield line


def count_throttled(
    lines: Iterable[str],
    max_per_window: int,
    window_seconds: float = 1.0,
) -> dict:
    """Return a summary dict with 'kept' and 'dropped' counts."""
    all_lines: List[str] = list(lines)
    kept = list(throttle_lines(all_lines, max_per_window, window_seconds))
    kept_set = set(id(l) for l in kept)  # noqa: not reliable for strings
    # Re-run to count properly
    kept_count = sum(1 for _ in throttle_lines(all_lines, max_per_window, window_seconds))
    total = len(all_lines)
    return {"total": total, "kept": kept_count, "dropped": total - kept_count}
