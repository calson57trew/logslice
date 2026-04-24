"""alerter.py — emit alerts when log lines match threshold conditions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.parser import extract_timestamp


@dataclass
class AlertRule:
    pattern: re.Pattern
    label: str
    threshold: int = 1  # number of matches before firing
    window_seconds: Optional[float] = None  # None = no windowing


@dataclass
class AlertEvent:
    label: str
    line: str
    count: int
    timestamp: Optional[str] = None


def compile_alert_rules(
    rules: List[Tuple[str, str, int]],
    ignore_case: bool = False,
) -> List[AlertRule]:
    """Compile (pattern, label, threshold) tuples into AlertRule objects."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled: List[AlertRule] = []
    for pattern, label, threshold in rules:
        compiled.append(AlertRule(re.compile(pattern, flags), label, threshold))
    return compiled


def alert_lines(
    lines: Iterable[str],
    rules: List[AlertRule],
) -> Iterator[Tuple[str, Optional[AlertEvent]]]:
    """Yield (line, alert_event_or_none) for every input line.

    An AlertEvent is emitted on the line that causes the match count to
    reach the rule's threshold.  Counts reset after each firing.
    """
    counts: List[int] = [0] * len(rules)
    for line in lines:
        fired: Optional[AlertEvent] = None
        for idx, rule in enumerate(rules):
            if rule.pattern.search(line):
                counts[idx] += 1
                if counts[idx] >= rule.threshold:
                    ts = extract_timestamp(line)
                    fired = AlertEvent(
                        label=rule.label,
                        line=line.rstrip("\n"),
                        count=counts[idx],
                        timestamp=ts,
                    )
                    counts[idx] = 0  # reset after firing
                    break  # first matching rule wins
        yield line, fired


def count_alerts(events: Iterable[Optional[AlertEvent]]) -> int:
    """Return the number of non-None alert events."""
    return sum(1 for e in events if e is not None)
