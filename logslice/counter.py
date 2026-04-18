"""Line and match counting utilities for logslice."""

from dataclasses import dataclass, field
from typing import Iterable, Optional
import re


@dataclass
class SliceStats:
    total_lines: int = 0
    matched_lines: int = 0
    skipped_lines: int = 0
    pattern_hits: dict = field(default_factory=dict)

    def record(self, line: str, matched: bool, pattern: Optional[str] = None) -> None:
        self.total_lines += 1
        if matched:
            self.matched_lines += 1
            if pattern:
                self.pattern_hits[pattern] = self.pattern_hits.get(pattern, 0) + 1
        else:
            self.skipped_lines += 1

    def summary(self) -> str:
        lines = [
            f"Total lines processed : {self.total_lines}",
            f"Matched lines         : {self.matched_lines}",
            f"Skipped lines         : {self.skipped_lines}",
        ]
        if self.pattern_hits:
            lines.append("Pattern hits:")
            for pat, count in self.pattern_hits.items():
                lines.append(f"  {pat!r}: {count}")
        return "\n".join(lines)


def count_lines(
    lines: Iterable[str],
    pattern: Optional[str] = None,
) -> SliceStats:
    """Iterate over lines and collect stats, optionally tracking pattern matches."""
    stats = SliceStats()
    compiled = re.compile(pattern) if pattern else None
    for line in lines:
        matched = True
        if compiled:
            hit = bool(compiled.search(line))
            stats.record(line, matched=True, pattern=pattern if hit else None)
        else:
            stats.record(line, matched=matched)
    return stats
