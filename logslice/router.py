"""Route log lines to different output sinks based on pattern rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple


@dataclass
class RouteRule:
    pattern: re.Pattern
    sink: str


@dataclass
class RoutedLine:
    line: str
    sink: str


def compile_route_rules(
    rules: List[Tuple[str, str]], ignore_case: bool = False
) -> List[RouteRule]:
    """Compile (pattern, sink) pairs into RouteRule objects."""
    flags = re.IGNORECASE if ignore_case else 0
    return [RouteRule(pattern=re.compile(p, flags), sink=s) for p, s in rules]


def route_line(
    line: str,
    rules: List[RouteRule],
    default_sink: str = "default",
) -> RoutedLine:
    """Return a RoutedLine assigning *line* to the first matching sink."""
    for rule in rules:
        if rule.pattern.search(line):
            return RoutedLine(line=line, sink=rule.sink)
    return RoutedLine(line=line, sink=default_sink)


def route_lines(
    lines: Iterable[str],
    rules: List[RouteRule],
    default_sink: str = "default",
) -> Iterator[RoutedLine]:
    """Yield RoutedLine for every input line."""
    for line in lines:
        yield route_line(line, rules, default_sink)


def collect_sinks(
    routed: Iterable[RoutedLine],
) -> Dict[str, List[str]]:
    """Group lines by sink name and return a mapping of sink -> [lines]."""
    result: Dict[str, List[str]] = {}
    for rl in routed:
        result.setdefault(rl.sink, []).append(rl.line)
    return result


def count_routed(routed: Iterable[RoutedLine]) -> Dict[str, int]:
    """Return a mapping of sink -> line count."""
    counts: Dict[str, int] = {}
    for rl in routed:
        counts[rl.sink] = counts.get(rl.sink, 0) + 1
    return counts
