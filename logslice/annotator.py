"""Annotate log lines with a prefix tag or inline label."""
from __future__ import annotations

import re
from typing import Iterable, Iterator

from logslice.parser import extract_timestamp

_LEVEL_RE = re.compile(r'\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\b', re.IGNORECASE)


def annotate_line(line: str, tag: str, inline: bool = False) -> str:
    """Prepend *tag* to *line*.

    If *inline* is True the tag is inserted right after the timestamp
    (if one is found), otherwise it is prepended to the whole line.
    """
    line_stripped = line.rstrip('\n')
    suffix = '\n' if line.endswith('\n') else ''
    label = f'[{tag}]'

    if inline:
        ts = extract_timestamp(line_stripped)
        if ts is not None:
            ts_str = ts.strftime('%Y-%m-%dT%H:%M:%S') if hasattr(ts, 'strftime') else str(ts)
            # find end of timestamp in line
            idx = line_stripped.find(ts_str)
            if idx != -1:
                end = idx + len(ts_str)
                return line_stripped[:end] + ' ' + label + line_stripped[end:] + suffix
    return label + ' ' + line_stripped + suffix


def annotate_lines(
    lines: Iterable[str],
    tag: str,
    inline: bool = False,
    skip_continuations: bool = True,
) -> Iterator[str]:
    """Yield annotated versions of *lines*.

    Continuation lines (no leading timestamp and not first line) are
    passed through unchanged when *skip_continuations* is True.
    """
    first = True
    for line in lines:
        is_continuation = (not first) and extract_timestamp(line) is None
        if skip_continuations and is_continuation:
            yield line
        else:
            yield annotate_line(line, tag, inline=inline)
        first = False


def count_annotated(original: list[str], annotated: list[str]) -> int:
    """Return number of lines that were actually modified."""
    return sum(1 for o, a in zip(original, annotated) if o != a)
