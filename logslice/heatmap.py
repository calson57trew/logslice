"""Heatmap: bucket log lines by time interval and count activity."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from logslice.parser import extract_timestamp

_TS_MINUTE = re.compile(r"^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2})")
_TS_HOUR = re.compile(r"^(\d{4}-\d{2}-\d{2}[T ]\d{2})")


@dataclass
class HeatmapResult:
    buckets: Dict[str, int] = field(default_factory=dict)
    bucket_size: str = "minute"
    total_lines: int = 0
    timed_lines: int = 0


def _floor_bucket(ts: str, bucket_size: str) -> Optional[str]:
    """Truncate a timestamp string to the requested bucket granularity."""
    if bucket_size == "hour":
        m = _TS_HOUR.match(ts)
    else:
        m = _TS_MINUTE.match(ts)
    return m.group(1) if m else None


def build_heatmap(
    lines: Iterable[str],
    bucket_size: str = "minute",
    label_pattern: Optional[str] = None,
) -> HeatmapResult:
    """Count lines per time bucket.

    Args:
        lines: iterable of log lines.
        bucket_size: ``'minute'`` or ``'hour'``.
        label_pattern: optional regex; only lines matching it are counted.
    """
    if bucket_size not in ("minute", "hour"):
        raise ValueError(f"bucket_size must be 'minute' or 'hour', got {bucket_size!r}")

    label_re = re.compile(label_pattern) if label_pattern else None
    buckets: Dict[str, int] = defaultdict(int)
    total = timed = 0

    for line in lines:
        total += 1
        ts = extract_timestamp(line)
        if ts is None:
            continue
        timed += 1
        if label_re and not label_re.search(line):
            continue
        bucket = _floor_bucket(ts, bucket_size)
        if bucket:
            buckets[bucket] += 1

    return HeatmapResult(
        buckets=dict(sorted(buckets.items())),
        bucket_size=bucket_size,
        total_lines=total,
        timed_lines=timed,
    )


def format_heatmap(
    result: HeatmapResult,
    bar_width: int = 40,
    show_count: bool = True,
) -> List[str]:
    """Render a text bar-chart of the heatmap."""
    if not result.buckets:
        return ["(no timed lines found)\n"]
    max_val = max(result.buckets.values()) or 1
    rows: List[str] = []
    for bucket, count in result.buckets.items():
        bar_len = round(count / max_val * bar_width)
        bar = "#" * bar_len
        suffix = f"  {count}" if show_count else ""
        rows.append(f"{bucket}  |{bar:<{bar_width}}|{suffix}\n")
    return rows
