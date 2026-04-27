"""windower.py – sliding/tumbling window aggregation over timestamped log lines."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

_TS_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"
)


@dataclass
class WindowResult:
    start: str
    end: str
    lines: List[str] = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return len(self.lines)


def _parse_ts(line: str) -> Optional[datetime]:
    m = _TS_RE.search(line)
    if not m:
        return None
    raw = m.group(1).replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _floor(dt: datetime, seconds: int) -> datetime:
    epoch = datetime(1970, 1, 1)
    total = int((dt - epoch).total_seconds())
    floored = (total // seconds) * seconds
    return epoch + timedelta(seconds=floored)


def tumbling_windows(
    lines: List[str],
    window_seconds: int = 60,
) -> Iterator[WindowResult]:
    """Yield non-overlapping tumbling windows of *window_seconds* duration."""
    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")

    buckets: dict[datetime, WindowResult] = {}

    for line in lines:
        ts = _parse_ts(line)
        if ts is None:
            # attach to last bucket if one exists, else skip
            if buckets:
                last_key = max(buckets)
                buckets[last_key].lines.append(line)
            continue
        key = _floor(ts, window_seconds)
        if key not in buckets:
            end_dt = key + timedelta(seconds=window_seconds)
            buckets[key] = WindowResult(
                start=key.strftime("%Y-%m-%d %H:%M:%S"),
                end=end_dt.strftime("%Y-%m-%d %H:%M:%S"),
            )
        buckets[key].lines.append(line)

    for key in sorted(buckets):
        yield buckets[key]


def count_windows(lines: List[str], window_seconds: int = 60) -> int:
    """Return the number of tumbling windows produced from *lines*."""
    return sum(1 for _ in tumbling_windows(lines, window_seconds))
