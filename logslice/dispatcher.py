"""Dispatch log lines to multiple named output channels based on routing rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Tuple


@dataclass
class DispatchRule:
    channel: str
    pattern: re.Pattern
    stop: bool = True  # stop matching further rules once this fires


@dataclass
class DispatchResult:
    channels: Dict[str, List[str]] = field(default_factory=dict)
    default: List[str] = field(default_factory=list)
    total: int = 0
    dispatched: int = 0

    def all_channels(self) -> List[str]:
        return sorted(self.channels.keys())


def compile_dispatch_rules(
    rules: List[Tuple[str, str]],
    ignore_case: bool = False,
    stop: bool = True,
) -> List[DispatchRule]:
    """Compile (channel, pattern_str) pairs into DispatchRule objects."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = []
    for channel, pattern_str in rules:
        compiled.append(
            DispatchRule(
                channel=channel,
                pattern=re.compile(pattern_str, flags),
                stop=stop,
            )
        )
    return compiled


def dispatch_line(
    line: str,
    rules: List[DispatchRule],
) -> Optional[str]:
    """Return the first matching channel name, or None if no rule matches."""
    for rule in rules:
        if rule.pattern.search(line):
            return rule.channel
    return None


def dispatch_lines(
    lines: Iterable[str],
    rules: List[DispatchRule],
    default_channel: Optional[str] = None,
) -> DispatchResult:
    """Route each line into a channel bucket according to rules."""
    result = DispatchResult()
    for line in lines:
        result.total += 1
        channel = dispatch_line(line, rules)
        if channel is not None:
            result.channels.setdefault(channel, []).append(line)
            result.dispatched += 1
        else:
            if default_channel is not None:
                result.channels.setdefault(default_channel, []).append(line)
            else:
                result.default.append(line)
    return result


def iter_channel(
    result: DispatchResult, channel: str
) -> Iterator[str]:
    """Yield lines belonging to a specific channel."""
    yield from result.channels.get(channel, [])


def count_dispatched(result: DispatchResult) -> int:
    return result.dispatched
