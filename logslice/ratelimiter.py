"""Rate-limit log lines to at most N lines per time bucket (e.g. per second/minute)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional

from logslice.parser import extract_timestamp

_UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "second": 1,
    "m": 60,
    "min": 60,
    "minute": 60,
    "h": 3600,
    "hr": 3600,
    "hour": 3600,
}


def parse_window(spec: str) -> int:
    """Parse a window spec like '1s', '30m', '2h' into seconds."""
    spec = spec.strip().lower()
    for suffix in sorted(_UNIT_SECONDS, key=len, reverse=True):
        if spec.endswith(suffix):
            number_part = spec[: -len(suffix)].strip()
            if number_part == "":
                number_part = "1"
            try:
                return int(number_part) * _UNIT_SECONDS[suffix]
            except ValueError:
                raise ValueError(f"Invalid window spec: {spec!r}")
    try:
        return int(spec)
    except ValueError:
        raise ValueError(f"Invalid window spec: {spec!r}")


@dataclass
class RateLimitStats:
    total: int = 0
    emitted: int = 0
    dropped: int = 0


def ratelimit_lines(
    lines: Iterable[str],
    max_lines: int,
    window_seconds: int = 1,
) -> Iterator[str]:
    """Yield at most *max_lines* timestamped lines per *window_seconds* bucket.

    Continuation lines (no timestamp) always follow their parent line.
    Lines without a timestamp are emitted unconditionally.
    """
    if max_lines < 1:
        raise ValueError("max_lines must be >= 1")
    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")

    current_bucket: Optional[int] = None
    bucket_count: int = 0
    parent_kept: bool = True

    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            # continuation — follow parent decision
            if parent_kept:
                yield line
            continue

        bucket = int(ts.timestamp()) // window_seconds
        if bucket != current_bucket:
            current_bucket = bucket
            bucket_count = 0

        if bucket_count < max_lines:
            bucket_count += 1
            parent_kept = True
            yield line
        else:
            parent_kept = False


def count_ratelimited(
    lines: Iterable[str],
    max_lines: int,
    window_seconds: int = 1,
) -> RateLimitStats:
    """Return stats about how many lines were emitted vs dropped."""
    stats = RateLimitStats()
    source = list(lines)
    stats.total = len(source)
    kept = list(ratelimit_lines(source, max_lines, window_seconds))
    stats.emitted = len(kept)
    stats.dropped = stats.total - stats.emitted
    return stats
