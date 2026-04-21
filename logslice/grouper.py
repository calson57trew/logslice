"""Group log lines into named buckets by pattern or time window."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from logslice.parser import extract_timestamp


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    ungrouped: List[str] = field(default_factory=list)


def compile_group_rules(
    rules: List[Tuple[str, str]], ignore_case: bool = False
) -> List[Tuple[re.Pattern, str]]:
    """Compile (pattern, label) pairs into (compiled_re, label) pairs."""
    flags = re.IGNORECASE if ignore_case else 0
    return [(re.compile(pattern, flags), label) for pattern, label in rules]


def group_by_pattern(
    lines: Iterable[str],
    rules: List[Tuple[re.Pattern, str]],
    multi: bool = False,
) -> GroupResult:
    """Assign each line to one (or more) named groups based on regex rules.

    Args:
        lines: Input log lines.
        rules: Compiled (pattern, label) pairs.
        multi: If True, a line may appear in multiple groups.
    """
    result = GroupResult()
    for line in lines:
        matched = False
        for pattern, label in rules:
            if pattern.search(line):
                result.groups[label].append(line)
                matched = True
                if not multi:
                    break
        if not matched:
            result.ungrouped.append(line)
    return result


def group_by_hour(lines: Iterable[str]) -> GroupResult:
    """Group lines into buckets keyed by 'YYYY-MM-DD HH' (hour granularity)."""
    result = GroupResult()
    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            result.ungrouped.append(line)
        else:
            bucket = ts.strftime("%Y-%m-%d %H")
            result.groups[bucket].append(line)
    return result


def count_grouped(result: GroupResult) -> Dict[str, int]:
    """Return a dict mapping each group label to its line count."""
    counts: Dict[str, int] = {k: len(v) for k, v in result.groups.items()}
    if result.ungrouped:
        counts["(ungrouped)"] = len(result.ungrouped)
    return counts
