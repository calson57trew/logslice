"""Anomaly detection: flag lines whose gap from the previous timed line
exceeds a configurable threshold (in seconds)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, Iterator, List, Optional

_TS_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
)


@dataclass
class AnomalyEvent:
    line: str
    prev_ts: Optional[str]
    curr_ts: str
    gap_seconds: float


@dataclass
class AnomalyResult:
    events: List[AnomalyEvent] = field(default_factory=list)
    total_lines: int = 0
    timed_lines: int = 0

    @property
    def anomaly_count(self) -> int:
        return len(self.events)


def _parse_dt(ts: str) -> Optional[datetime]:
    ts_clean = ts.rstrip("Z").replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(ts_clean[:len(fmt) + 3], fmt).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            continue
    return None


def detect_anomalies(
    lines: Iterable[str],
    threshold_seconds: float = 60.0,
) -> AnomalyResult:
    """Scan *lines* and record any gap larger than *threshold_seconds*."""
    result = AnomalyResult()
    prev_dt: Optional[datetime] = None
    prev_ts: Optional[str] = None

    for line in lines:
        result.total_lines += 1
        m = _TS_RE.search(line)
        if not m:
            continue
        result.timed_lines += 1
        curr_ts = m.group(1)
        curr_dt = _parse_dt(curr_ts)
        if curr_dt is None:
            continue
        if prev_dt is not None:
            gap = (curr_dt - prev_dt).total_seconds()
            if gap > threshold_seconds:
                result.events.append(
                    AnomalyEvent(
                        line=line,
                        prev_ts=prev_ts,
                        curr_ts=curr_ts,
                        gap_seconds=gap,
                    )
                )
        prev_dt = curr_dt
        prev_ts = curr_ts

    return result


def format_anomalies(result: AnomalyResult) -> str:
    """Return a human-readable summary of detected anomalies."""
    lines = [
        f"Total lines   : {result.total_lines}",
        f"Timed lines   : {result.timed_lines}",
        f"Anomalies     : {result.anomaly_count}",
    ]
    for ev in result.events:
        lines.append(
            f"  gap {ev.gap_seconds:.1f}s  [{ev.prev_ts} -> {ev.curr_ts}]  {ev.line.rstrip()}"
        )
    return "\n".join(lines) + "\n"
