"""sequencer.py – detect and report gaps or jumps in log line sequence numbers."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

_SEQ_RE = re.compile(r"(?:^|\s)(?:seq|sequence|seqno|#)[=:\s]*(\d+)", re.IGNORECASE)


@dataclass
class SequenceGap:
    expected: int
    found: int
    line: str

    @property
    def missing(self) -> int:
        return self.found - self.expected


@dataclass
class SequenceResult:
    total_lines: int = 0
    sequenced_lines: int = 0
    gaps: List[SequenceGap] = field(default_factory=list)

    @property
    def gap_count(self) -> int:
        return len(self.gaps)


def extract_seq(line: str) -> Optional[int]:
    """Return the first sequence number found in *line*, or None."""
    m = _SEQ_RE.search(line)
    if m:
        return int(m.group(1))
    return None


def check_sequence(
    lines: Iterable[str],
    *,
    step: int = 1,
    ignore_reset: bool = False,
) -> SequenceResult:
    """Scan *lines* for sequence-number gaps.

    Args:
        lines: Input log lines.
        step: Expected increment between consecutive sequence numbers.
        ignore_reset: When True, a sequence number smaller than the previous
            one is treated as a legitimate counter reset rather than a gap.

    Returns:
        A :class:`SequenceResult` describing what was found.
    """
    result = SequenceResult()
    prev: Optional[int] = None

    for line in lines:
        result.total_lines += 1
        seq = extract_seq(line)
        if seq is None:
            continue
        result.sequenced_lines += 1
        if prev is not None:
            expected = prev + step
            if seq != expected:
                if ignore_reset and seq < prev:
                    prev = seq
                    continue
                result.gaps.append(SequenceGap(expected=expected, found=seq, line=line.rstrip("\n")))
        prev = seq

    return result


def iter_gap_lines(result: SequenceResult) -> Iterator[str]:
    """Yield human-readable descriptions of each detected gap."""
    for gap in result.gaps:
        yield (
            f"GAP: expected seq {gap.expected}, found {gap.found} "
            f"(missing {gap.missing} step(s)) — {gap.line}\n"
        )


def format_sequence_report(result: SequenceResult) -> str:
    lines = [
        f"total lines    : {result.total_lines}",
        f"sequenced lines: {result.sequenced_lines}",
        f"gaps detected  : {result.gap_count}",
    ]
    for gap in result.gaps:
        lines.append(f"  expected={gap.expected} found={gap.found} missing={gap.missing}")
    return "\n".join(lines) + "\n"
