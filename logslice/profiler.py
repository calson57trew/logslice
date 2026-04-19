"""Profile log streams: measure line rates and gap detection."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


@dataclass
class ProfileResult:
    total_lines: int = 0
    timed_lines: int = 0
    first_ts: Optional[datetime] = None
    last_ts: Optional[datetime] = None
    max_gap: Optional[timedelta] = None
    max_gap_at: Optional[datetime] = None
    gaps: List[tuple] = field(default_factory=list)  # (start, end, duration)

    @property
    def duration(self) -> Optional[timedelta]:
        if self.first_ts and self.last_ts:
            return self.last_ts - self.first_ts
        return None

    @property
    def lines_per_second(self) -> Optional[float]:
        if self.duration and self.duration.total_seconds() > 0:
            return self.timed_lines / self.duration.total_seconds()
        return None


def profile_lines(
    lines: Iterable[str],
    gap_threshold: Optional[timedelta] = None,
) -> ProfileResult:
    result = ProfileResult()
    prev_ts: Optional[datetime] = None

    for line in lines:
        result.total_lines += 1
        ts = extract_timestamp(line)
        if ts is None:
            continue
        result.timed_lines += 1
        if result.first_ts is None:
            result.first_ts = ts
        result.last_ts = ts

        if prev_ts is not None and ts >= prev_ts:
            gap = ts - prev_ts
            if gap_threshold is None or gap >= gap_threshold:
                result.gaps.append((prev_ts, ts, gap))
            if result.max_gap is None or gap > result.max_gap:
                result.max_gap = gap
                result.max_gap_at = ts
        prev_ts = ts

    return result


def format_profile(result: ProfileResult) -> str:
    lines = [
        f"Total lines    : {result.total_lines}",
        f"Timed lines    : {result.timed_lines}",
        f"First timestamp: {result.first_ts or 'N/A'}",
        f"Last timestamp : {result.last_ts or 'N/A'}",
        f"Duration       : {result.duration or 'N/A'}",
        f"Lines/sec      : {result.lines_per_second:.2f}" if result.lines_per_second is not None else "Lines/sec      : N/A",
        f"Largest gap    : {result.max_gap or 'N/A'}",
        f"Gap at         : {result.max_gap_at or 'N/A'}",
        f"Gaps detected  : {len(result.gaps)}",
    ]
    return "\n".join(lines)
