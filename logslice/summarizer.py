"""Summarize log slices: count levels, first/last timestamp, unique messages."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from logslice.parser import extract_timestamp

LEVEL_RE = re.compile(r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE)


@dataclass
class LogSummary:
    total_lines: int = 0
    matched_lines: int = 0
    level_counts: Dict[str, int] = field(default_factory=dict)
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None
    unique_messages: int = 0


def _extract_level(line: str) -> Optional[str]:
    m = LEVEL_RE.search(line)
    if m:
        return m.group(1).upper().replace("WARNING", "WARN")
    return None


def summarize_lines(lines: Iterable[str], matched_only: bool = False) -> LogSummary:
    summary = LogSummary()
    seen: set = set()

    for line in lines:
        summary.total_lines += 1
        ts = extract_timestamp(line)
        if ts:
            if summary.first_timestamp is None:
                summary.first_timestamp = ts
            summary.last_timestamp = ts

        level = _extract_level(line)
        if level:
            summary.level_counts[level] = summary.level_counts.get(level, 0) + 1
            summary.matched_lines += 1
            normalized = LEVEL_RE.sub("", line).strip()
            seen.add(normalized)

    summary.unique_messages = len(seen)
    return summary


def format_summary(summary: LogSummary) -> List[str]:
    lines = [
        f"Total lines     : {summary.total_lines}",
        f"Lines with level: {summary.matched_lines}",
        f"Unique messages : {summary.unique_messages}",
        f"First timestamp : {summary.first_timestamp or 'n/a'}",
        f"Last timestamp  : {summary.last_timestamp or 'n/a'}",
    ]
    if summary.level_counts:
        lines.append("Level breakdown :")
        for lvl, cnt in sorted(summary.level_counts.items()):
            lines.append(f"  {lvl:<10} {cnt}")
    return lines
