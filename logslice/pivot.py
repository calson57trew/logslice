"""pivot.py — group log lines into time-bucketed pivots for pattern frequency analysis."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from logslice.parser import extract_timestamp


@dataclass
class PivotTable:
    bucket_size: int  # seconds
    pattern: str
    buckets: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_matched: int = 0
    total_lines: int = 0


def _floor_to_bucket(ts: str, bucket_size: int) -> str:
    """Truncate an ISO-8601 timestamp string to the nearest bucket boundary."""
    # Parse seconds since epoch via simple regex — keep as string label
    m = re.match(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}):(\d{2}):(\d{2})", ts)
    if not m:
        return ts
    date, hh, mm, ss = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    total_secs = hh * 3600 + mm * 60 + ss
    floored = (total_secs // bucket_size) * bucket_size
    fh, rem = divmod(floored, 3600)
    fm, fs = divmod(rem, 60)
    return f"{date} {fh:02d}:{fm:02d}:{fs:02d}"


def build_pivot(
    lines: Iterable[str],
    pattern: str,
    bucket_size: int = 60,
    ignore_case: bool = False,
) -> PivotTable:
    """Scan *lines* and count how often *pattern* appears in each time bucket."""
    if bucket_size < 1:
        raise ValueError("bucket_size must be >= 1 second")
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)
    table = PivotTable(bucket_size=bucket_size, pattern=pattern)
    current_bucket: Optional[str] = None

    for line in lines:
        table.total_lines += 1
        ts = extract_timestamp(line)
        if ts:
            current_bucket = _floor_to_bucket(ts, bucket_size)
        if compiled.search(line):
            table.total_matched += 1
            bucket_key = current_bucket or "(no timestamp)"
            table.buckets[bucket_key] += 1

    return table


def format_pivot(table: PivotTable, top_n: int = 0) -> List[str]:
    """Render a PivotTable as human-readable lines.

    Args:
        table:  The pivot table to render.
        top_n:  If > 0, only emit the *top_n* busiest buckets.
    """
    rows: List[Tuple[str, int]] = sorted(
        table.buckets.items(), key=lambda kv: kv[0]
    )
    if top_n > 0:
        rows = sorted(table.buckets.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
        rows = sorted(rows, key=lambda kv: kv[0])

    out: List[str] = [
        f"# pivot  pattern={table.pattern!r}  bucket={table.bucket_size}s",
        f"# total_lines={table.total_lines}  matched={table.total_matched}",
        "",
    ]
    for bucket, count in rows:
        bar = "#" * min(count, 60)
        out.append(f"{bucket}  {count:>6}  {bar}")
    return out
