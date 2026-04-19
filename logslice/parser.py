"""Timestamp parsing utilities for logslice."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns
TIMESTAMP_PATTERNS = [
    (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?', '%Y-%m-%dT%H:%M:%S'),
    (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?', '%Y-%m-%d %H:%M:%S'),
    (r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}', '%d/%b/%Y:%H:%M:%S'),
    (r'\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2}', '%b %d %H:%M:%S'),
]


def extract_timestamp(line: str) -> Optional[datetime]:
    """Extract the first recognizable timestamp from a log line."""
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            raw = match.group(0)
            # Normalize ISO8601 with fractional seconds or timezone
            raw_clean = re.sub(r'\.\d+', '', raw)
            raw_clean = re.sub(r'(Z|[+-]\d{2}:\d{2})$', '', raw_clean)
            try:
                return datetime.strptime(raw_clean, fmt)
            except ValueError:
                continue
    return None


def parse_user_timestamp(ts_str: str) -> datetime:
    """Parse a user-supplied timestamp string into a datetime object."""
    formats = [
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized timestamp format: '{ts_str}'")


def is_line_in_range(
    line: str,
    start: Optional[datetime],
    end: Optional[datetime],
) -> Optional[bool]:
    """Check whether a log line's timestamp falls within [start, end].

    Returns True if within range, False if outside, or None if no timestamp
    could be extracted from the line.
    """
    ts = extract_timestamp(line)
    if ts is None:
        return None
    if start is not None and ts < start:
        return False
    if end is not None and ts > end:
        return False
    return True


def find_first_timestamp(lines: list[str]) -> Optional[datetime]:
    """Return the first extractable timestamp found across a list of log lines.

    Useful for inferring the time range covered by a log file without scanning
    every line.
    """
    for line in lines:
        ts = extract_timestamp(line)
        if ts is not None:
            return ts
    return None
