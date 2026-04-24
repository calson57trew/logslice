"""Replay log lines at a controlled speed, simulating real-time output."""

import time
from typing import Iterable, Iterator, Optional
from logslice.parser import extract_timestamp
from datetime import datetime


def _parse_dt(line: str) -> Optional[datetime]:
    ts = extract_timestamp(line)
    if ts is None:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def replay_realtime(
    lines: Iterable[str],
    speed: float = 1.0,
    max_gap: Optional[float] = None,
) -> Iterator[str]:
    """Yield lines with delays proportional to their timestamp gaps.

    Args:
        lines:    Input log lines.
        speed:    Multiplier; 2.0 = twice as fast, 0.5 = half speed.
        max_gap:  Cap on any single sleep in seconds (None = no cap).
    """
    if speed <= 0:
        raise ValueError("speed must be positive")

    prev_dt: Optional[datetime] = None

    for line in lines:
        dt = _parse_dt(line)
        if dt is not None and prev_dt is not None:
            gap = (dt - prev_dt).total_seconds()
            if gap > 0:
                delay = gap / speed
                if max_gap is not None:
                    delay = min(delay, max_gap)
                time.sleep(delay)
        if dt is not None:
            prev_dt = dt
        yield line


def replay_fixed(
    lines: Iterable[str],
    delay: float = 0.1,
) -> Iterator[str]:
    """Yield lines with a fixed delay between each.

    Args:
        lines: Input log lines.
        delay: Seconds to sleep between lines.
    """
    if delay < 0:
        raise ValueError("delay must be non-negative")
    for line in lines:
        time.sleep(delay)
        yield line


def count_replayed(lines: Iterable[str]) -> int:
    """Return the total number of lines in the iterable (consumes it)."""
    return sum(1 for _ in lines)
