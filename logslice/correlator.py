"""Correlate log lines across sources by shared identifiers (e.g. request IDs)."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class CorrelationGroup:
    key: str
    lines: List[str] = field(default_factory=list)


def compile_id_pattern(pattern: str) -> re.Pattern:
    """Compile a regex pattern used to extract a correlation ID from a line."""
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"Invalid correlation pattern {pattern!r}: {exc}") from exc
    if compiled.groups < 1:
        raise ValueError(
            f"Pattern {pattern!r} must contain at least one capturing group."
        )
    return compiled


def extract_id(line: str, pattern: re.Pattern) -> Optional[str]:
    """Return the first captured group from *line*, or None if no match."""
    m = pattern.search(line)
    if m:
        return m.group(1)
    return None


def correlate_lines(
    lines: Iterable[str],
    pattern: re.Pattern,
    *,
    include_unmatched: bool = False,
) -> Dict[str, CorrelationGroup]:
    """Group *lines* by the correlation ID extracted via *pattern*.

    Lines that carry no ID are placed in the special group ``"__unmatched__"``
    when *include_unmatched* is True, otherwise they are silently dropped.
    """
    groups: Dict[str, CorrelationGroup] = defaultdict(lambda: CorrelationGroup(key=""))
    for line in lines:
        cid = extract_id(line, pattern)
        if cid is None:
            if include_unmatched:
                key = "__unmatched__"
                if key not in groups:
                    groups[key] = CorrelationGroup(key=key)
                groups[key].lines.append(line)
        else:
            if cid not in groups:
                groups[cid] = CorrelationGroup(key=cid)
            groups[cid].lines.append(line)
    return dict(groups)


def count_correlated(groups: Dict[str, CorrelationGroup]) -> Tuple[int, int]:
    """Return (number_of_groups, total_lines_matched)."""
    total = sum(len(g.lines) for g in groups.values())
    return len(groups), total


def format_correlation(groups: Dict[str, CorrelationGroup]) -> List[str]:
    """Render correlation groups as labelled blocks suitable for output."""
    out: List[str] = []
    for key, group in sorted(groups.items()):
        out.append(f"=== {key} ({len(group.lines)} lines) ===\n")
        out.extend(group.lines)
    return out
