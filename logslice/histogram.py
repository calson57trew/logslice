"""Build and format a frequency histogram from log lines."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

_LEVEL_RE = re.compile(r"\b(ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE|CRITICAL|FATAL)\b", re.IGNORECASE)


@dataclass
class HistogramResult:
    buckets: Counter = field(default_factory=Counter)
    total: int = 0
    timed: int = 0


def _extract_key(line: str, pattern: Optional[re.Pattern]) -> Optional[str]:
    """Return the histogram key for *line* using *pattern* or log-level fallback."""
    if pattern is not None:
        m = pattern.search(line)
        if m:
            return m.group(1) if m.lastindex else m.group(0)
        return None
    m = _LEVEL_RE.search(line)
    return m.group(0).upper() if m else None


def build_histogram(
    lines: Iterable[str],
    pattern: Optional[re.Pattern] = None,
    bucket_other: bool = True,
) -> HistogramResult:
    """Count occurrences of each key across *lines*."""
    result = HistogramResult()
    for line in lines:
        result.total += 1
        key = _extract_key(line, pattern)
        if key:
            result.timed += 1
            result.buckets[key] += 1
        elif bucket_other:
            result.buckets["(other)"] += 1
    return result


def format_histogram(
    result: HistogramResult,
    bar_width: int = 40,
    show_count: bool = True,
) -> List[str]:
    """Render *result* as a list of bar-chart lines."""
    if not result.buckets:
        return ["(no data)\n"]
    max_count = max(result.buckets.values())
    label_w = max(len(k) for k in result.buckets) + 1
    out: List[str] = []
    for key, count in sorted(result.buckets.items(), key=lambda kv: -kv[1]):
        filled = round(bar_width * count / max_count) if max_count else 0
        bar = "#" * filled + "-" * (bar_width - filled)
        suffix = f"  {count}" if show_count else ""
        out.append(f"{key:<{label_w}} |{bar}|{suffix}\n")
    return out
