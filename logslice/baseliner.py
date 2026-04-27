"""Baseline comparison: compare current log lines against a saved baseline."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

from logslice.deduplicator import normalize_line


@dataclass
class BaselineResult:
    new_lines: List[str] = field(default_factory=list)
    known_lines: List[str] = field(default_factory=list)
    baseline_size: int = 0

    @property
    def new_count(self) -> int:
        return len(self.new_lines)

    @property
    def known_count(self) -> int:
        return len(self.known_lines)


def load_baseline(path: str) -> set:
    """Load a set of normalised message fingerprints from *path*."""
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"Baseline file must contain a JSON array, got {type(data).__name__}")
    return set(data)


def save_baseline(path: str, lines: Iterable[str]) -> int:
    """Persist normalised fingerprints of *lines* to *path*. Returns count saved."""
    fingerprints = sorted({normalize_line(l) for l in lines if l.strip()})
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(fingerprints, fh, indent=2)
    return len(fingerprints)


def compare_to_baseline(
    lines: Iterable[str],
    baseline: set,
    *,
    emit_known: bool = False,
) -> BaselineResult:
    """Yield lines not present in *baseline* and collect statistics."""
    result = BaselineResult(baseline_size=len(baseline))
    for line in lines:
        fp = normalize_line(line)
        if fp in baseline:
            result.known_lines.append(line)
        else:
            result.new_lines.append(line)
    return result


def iter_new_lines(result: BaselineResult) -> Iterator[str]:
    """Iterate over lines that were not present in the baseline."""
    yield from result.new_lines


def format_baseline_summary(result: BaselineResult) -> str:
    lines = [
        f"Baseline size : {result.baseline_size} fingerprints",
        f"New lines     : {result.new_count}",
        f"Known lines   : {result.known_count}",
    ]
    return "\n".join(lines)
