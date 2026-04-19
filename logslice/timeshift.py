"""Shift timestamps in log lines by a fixed delta."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Iterator

from logslice.parser import extract_timestamp

_ISO_RE = re.compile(
    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
)


def _shift_timestamp_str(ts_str: str, delta: timedelta) -> str:
    """Parse an ISO-8601 timestamp string, shift it, and return the new string."""
    fmt_frac = "." in ts_str
    ts_str_clean = ts_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(ts_str_clean)
    except ValueError:
        return ts_str
    shifted = dt + delta
    if fmt_frac:
        result = shifted.strftime("%Y-%m-%dT%H:%M:%S.%f")
    else:
        result = shifted.strftime("%Y-%m-%dT%H:%M:%S")
    if dt.tzinfo is not None:
        offset = shifted.strftime("%z")
        result += offset[:3] + ":" + offset[3:]
    return result


def shift_line(line: str, delta: timedelta) -> str:
    """Return *line* with its leading timestamp shifted by *delta*."""
    m = _ISO_RE.search(line)
    if not m:
        return line
    original = m.group(1)
    shifted = _shift_timestamp_str(original, delta)
    return line[: m.start()] + shifted + line[m.end() :]


def shift_lines(
    lines: Iterator[str], delta: timedelta
) -> Iterator[str]:
    """Yield each line with its timestamp shifted by *delta*."""
    for line in lines:
        yield shift_line(line, delta)


def parse_delta(spec: str) -> timedelta:
    """Parse a delta spec like '+3600', '-90m', '+2h', '-1d'.

    Supported suffixes: s (seconds, default), m (minutes), h (hours), d (days).
    Leading '+'/'-' sets direction.
    """
    spec = spec.strip()
    if not spec:
        raise ValueError("Empty delta spec")
    sign = 1
    if spec[0] in ('+', '-'):
        sign = -1 if spec[0] == '-' else 1
        spec = spec[1:]
    if not spec:
        raise ValueError("Delta spec has no magnitude")
    suffix_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if spec[-1].lower() in suffix_map:
        multiplier = suffix_map[spec[-1].lower()]
        value = int(spec[:-1])
    else:
        multiplier = 1
        value = int(spec)
    return timedelta(seconds=sign * value * multiplier)
