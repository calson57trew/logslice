"""Diff two log streams, showing lines unique to each or common to both."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Iterator
from logslice.deduplicator import normalize_line


@dataclass
class DiffResult:
    only_left: list[str] = field(default_factory=list)
    only_right: list[str] = field(default_factory=list)
    common: list[str] = field(default_factory=list)


def _normalized_set(lines: Iterable[str]) -> dict[str, str]:
    """Return mapping of normalized -> first original line."""
    seen: dict[str, str] = {}
    for line in lines:
        key = normalize_line(line)
        if key not in seen:
            seen[key] = line
    return seen


def diff_logs(left: Iterable[str], right: Iterable[str]) -> DiffResult:
    """Compare two log sources by normalized message content."""
    left_map = _normalized_set(left)
    right_map = _normalized_set(right)

    left_keys = set(left_map)
    right_keys = set(right_map)

    return DiffResult(
        only_left=[left_map[k] for k in sorted(left_keys - right_keys)],
        only_right=[right_map[k] for k in sorted(right_keys - left_keys)],
        common=[left_map[k] for k in sorted(left_keys & right_keys)],
    )


def format_diff(result: DiffResult, mode: str = "all") -> Iterator[str]:
    """Yield annotated lines according to mode: all | left | right | common."""
    if mode in ("all", "left"):
        for line in result.only_left:
            yield "< " + line.rstrip("\n") + "\n"
    if mode in ("all", "right"):
        for line in result.only_right:
            yield "> " + line.rstrip("\n") + "\n"
    if mode in ("all", "common"):
        for line in result.common:
            yield "= " + line.rstrip("\n") + "\n"
