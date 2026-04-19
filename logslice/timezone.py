"""Timezone conversion utilities for log timestamps."""

from datetime import datetime, timezone, timedelta
import re
from typing import Optional

from logslice.parser import extract_timestamp

_OFFSET_RE = re.compile(r'^([+-])(\d{1,2}):(\d{2})$')


def parse_tzoffset(tz_str: str) -> timezone:
    """Parse a timezone string like '+05:30', '-08:00', or 'UTC' into a timezone."""
    if tz_str.upper() in ('UTC', 'Z'):
        return timezone.utc
    m = _OFFSET_RE.match(tz_str)
    if not m:
        raise ValueError(f"Unrecognised timezone offset: {tz_str!r}")
    sign, hours, minutes = m.groups()
    delta = timedelta(hours=int(hours), minutes=int(minutes))
    if sign == '-':
        delta = -delta
    return timezone(delta)


def convert_timestamp(ts: datetime, target_tz: timezone) -> datetime:
    """Convert a datetime to the target timezone. Assumes UTC if naive."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(target_tz)


def convert_line(line: str, target_tz: timezone) -> str:
    """Replace the timestamp in a log line with one converted to target_tz."""
    ts_str = extract_timestamp(line)
    if ts_str is None:
        return line
    try:
        from logslice.parser import parse_user_timestamp
        ts = parse_user_timestamp(ts_str)
    except Exception:
        return line
    converted = convert_timestamp(ts, target_tz)
    new_ts = converted.strftime('%Y-%m-%dT%H:%M:%S%z')
    # Insert colon into +HHMM -> +HH:MM
    if len(new_ts) > 19 and new_ts[-5] in '+-':
        new_ts = new_ts[:-2] + ':' + new_ts[-2:]
    return line.replace(ts_str, new_ts, 1)


def convert_lines(lines: list, target_tz: timezone) -> list:
    """Convert timestamps in all lines to the target timezone."""
    return [convert_line(line, target_tz) for line in lines]


def count_converted(original: list, converted: list) -> int:
    """Count how many lines had their timestamp changed."""
    return sum(1 for a, b in zip(original, converted) if a != b)
