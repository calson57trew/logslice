"""Score log lines by relevance based on keyword weights."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator


@dataclass
class ScoredLine:
    line: str
    score: float
    matched_terms: list[str] = field(default_factory=list)


def compile_score_rules(
    rules: list[tuple[str, float]], ignore_case: bool = True
) -> list[tuple[re.Pattern, float]]:
    """Compile (pattern, weight) pairs into (compiled_regex, weight) pairs."""
    flags = re.IGNORECASE if ignore_case else 0
    return [(re.compile(pat, flags), weight) for pat, weight in rules]


def score_line(
    line: str,
    compiled_rules: list[tuple[re.Pattern, float]],
) -> ScoredLine:
    """Return a ScoredLine with cumulative score from all matching rules."""
    total = 0.0
    matched: list[str] = []
    for pattern, weight in compiled_rules:
        if pattern.search(line):
            total += weight
            matched.append(pattern.pattern)
    return ScoredLine(line=line, score=total, matched_terms=matched)


def score_lines(
    lines: Iterable[str],
    compiled_rules: list[tuple[re.Pattern, float]],
    threshold: float = 0.0,
) -> Iterator[ScoredLine]:
    """Yield ScoredLine objects whose score meets or exceeds *threshold*."""
    for line in lines:
        result = score_line(line, compiled_rules)
        if result.score >= threshold:
            yield result


def top_lines(
    lines: Iterable[str],
    compiled_rules: list[tuple[re.Pattern, float]],
    n: int = 10,
) -> list[ScoredLine]:
    """Return the top-*n* lines by score (highest first)."""
    scored = [score_line(line, compiled_rules) for line in lines]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:n]


def count_scored(results: Iterable[ScoredLine]) -> dict[str, int]:
    """Return counts: total, above_zero, zero."""
    total = above_zero = 0
    for r in results:
        total += 1
        if r.score > 0:
            above_zero += 1
    return {"total": total, "above_zero": above_zero, "zero": total - above_zero}
