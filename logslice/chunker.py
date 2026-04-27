"""chunker.py – split a log stream into fixed-duration time buckets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


@dataclass
class TimeChunk:
    bucket: str
    lines: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.lines)


def _floor_bucket(ts: str, bucket_minutes: int) -> Optional[str]:
    """Return 'YYYY-MM-DD HH:MM' floored to *bucket_minutes* granularity."""
    # ts is expected to start with YYYY-MM-DD HH:MM or YYYY-MM-DDTHH:MM
    ts = ts.replace("T", " ")
    if len(ts) < 16:
        return None
    try:
        date_part, time_part = ts[:10], ts[11:16]
        hour, minute = int(time_part[:2]), int(time_part[3:5])
        floored = (minute // bucket_minutes) * bucket_minutes
        return f"{date_part} {hour:02d}:{floored:02d}"
    except (ValueError, IndexError):
        return None


def chunk_by_time(
    lines: Iterable[str],
    bucket_minutes: int = 5,
) -> Iterator[TimeChunk]:
    """Yield :class:`TimeChunk` objects, one per time bucket.

    Lines without a recognisable timestamp are appended to the most recent
    bucket, or to an ``(unassigned)`` bucket if no bucket has been opened yet.
    """
    if bucket_minutes < 1:
        raise ValueError("bucket_minutes must be >= 1")

    buckets: Dict[str, TimeChunk] = {}
    order: List[str] = []
    current_bucket: Optional[str] = None

    for line in lines:
        ts = extract_timestamp(line)
        if ts:
            key = _floor_bucket(ts, bucket_minutes)
        else:
            key = None

        if key is None:
            key = current_bucket or "(unassigned)"

        if key not in buckets:
            buckets[key] = TimeChunk(bucket=key)
            order.append(key)

        buckets[key].lines.append(line)
        current_bucket = key

    for k in order:
        yield buckets[k]


def count_chunks(lines: Iterable[str], bucket_minutes: int = 5) -> int:
    """Return the number of time buckets produced."""
    return sum(1 for _ in chunk_by_time(lines, bucket_minutes))
