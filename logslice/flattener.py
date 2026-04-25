"""Flatten multi-line log entries into single lines."""
from __future__ import annotations

import re
from typing import Iterable, Iterator

from logslice.parser import extract_timestamp

_DEFAULT_SEP = " | "


def is_continuation(line: str) -> bool:
    """Return True if *line* has no leading timestamp (continuation line)."""
    return extract_timestamp(line) is None


def flatten_lines(
    lines: Iterable[str],
    sep: str = _DEFAULT_SEP,
    strip_newlines: bool = True,
) -> Iterator[str]:
    """Merge continuation lines into their parent log entry.

    Each group of lines sharing a single timestamped header is joined
    with *sep* and emitted as one line.  A trailing newline is always
    appended to the result.

    Args:
        lines: Input log lines (may include trailing newlines).
        sep: Separator inserted between merged pieces.
        strip_newlines: If True, strip newlines from each piece before joining.
    """
    buffer: list[str] = []

    def _flush() -> str:
        pieces = [l.rstrip("\n") if strip_newlines else l for l in buffer]
        return sep.join(pieces) + "\n"

    for line in lines:
        if not is_continuation(line):
            if buffer:
                yield _flush()
            buffer = [line]
        else:
            buffer.append(line)

    if buffer:
        yield _flush()


def count_flattened(lines: Iterable[str], sep: str = _DEFAULT_SEP) -> dict[str, int]:
    """Return statistics about a flattening pass.

    Keys:
        ``input_lines``  – total lines consumed.
        ``output_lines`` – number of merged entries emitted.
        ``merged_lines`` – continuation lines that were folded in.
    """
    stats = {"input_lines": 0, "output_lines": 0, "merged_lines": 0}
    for entry in flatten_lines(lines, sep=sep):
        occurrences = entry.count(sep)
        stats["output_lines"] += 1
        stats["merged_lines"] += occurrences
        stats["input_lines"] += occurrences + 1
    return stats
