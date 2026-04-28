"""Count occurrences of patterns across log lines."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Tuple


@dataclass
class PatternCount:
    pattern: str
    count: int
    example: Optional[str] = None


@dataclass
class PatternCountResult:
    counts: List[PatternCount] = field(default_factory=list)
    total_lines: int = 0
    matched_lines: int = 0


def compile_patterns(patterns: List[str], ignore_case: bool = False) -> List[Tuple[str, re.Pattern]]:
    """Compile a list of pattern strings into (label, regex) pairs."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = []
    for p in patterns:
        try:
            compiled.append((p, re.compile(p, flags)))
        except re.error as exc:
            raise ValueError(f"Invalid pattern {p!r}: {exc}") from exc
    return compiled


def count_patterns(
    lines: Iterable[str],
    patterns: List[str],
    ignore_case: bool = False,
) -> PatternCountResult:
    """Count how many lines match each pattern and return a summary result."""
    compiled = compile_patterns(patterns, ignore_case=ignore_case)
    tallies: dict[str, int] = {p: 0 for p, _ in compiled}
    examples: dict[str, Optional[str]] = {p: None for p, _ in compiled}
    total = 0
    matched = 0
    any_hit = False

    for line in lines:
        total += 1
        any_hit = False
        for label, regex in compiled:
            if regex.search(line):
                tallies[label] += 1
                if examples[label] is None:
                    examples[label] = line.rstrip("\n")
                any_hit = True
        if any_hit:
            matched += 1

    counts = [
        PatternCount(pattern=p, count=tallies[p], example=examples[p])
        for p, _ in compiled
    ]
    return PatternCountResult(counts=counts, total_lines=total, matched_lines=matched)


def iter_count_lines(
    lines: Iterable[str],
    patterns: List[str],
    ignore_case: bool = False,
) -> Iterator[str]:
    """Pass lines through unchanged; side-effect counting happens in count_patterns."""
    yield from lines


def format_pattern_counts(result: PatternCountResult, show_examples: bool = False) -> str:
    """Render a PatternCountResult as a human-readable string."""
    lines = [
        f"Total lines : {result.total_lines}",
        f"Matched lines: {result.matched_lines}",
        "",
    ]
    for pc in result.counts:
        line = f"  {pc.count:>6}  {pc.pattern}"
        lines.append(line)
        if show_examples and pc.example:
            lines.append(f"           example: {pc.example}")
    return "\n".join(lines)
