"""Sort log lines by timestamp, optionally reversing order."""

from typing import Iterable, List
from logslice.parser import extract_timestamp


def sort_lines(
    lines: Iterable[str],
    reverse: bool = False,
) -> List[str]:
    """Return lines sorted by extracted timestamp.

    Lines without a timestamp are placed before timestamped lines
    (or after, when reverse=True) and preserve their relative order.
    Continuation lines (no timestamp) are attached to the preceding
    timestamped line and travel with it as a group.
    """
    groups: List[tuple] = []  # (timestamp | None, [lines])

    for line in lines:
        ts = extract_timestamp(line)
        if ts is not None:
            groups.append((ts, [line]))
        else:
            if groups:
                groups[-1][1].append(line)
            else:
                # leading continuation lines – create a sentinel group
                groups.append((None, [line]))

    timed = [(ts, grp) for ts, grp in groups if ts is not None]
    untimed = [(ts, grp) for ts, grp in groups if ts is None]

    timed.sort(key=lambda x: x[0], reverse=reverse)

    ordered = (untimed + timed) if not reverse else (timed + untimed)
    result: List[str] = []
    for _, grp in ordered:
        result.extend(grp)
    return result


def count_out_of_order(lines: Iterable[str]) -> int:
    """Count timestamped lines that are out of ascending order."""
    prev = None
    count = 0
    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            continue
        if prev is not None and ts < prev:
            count += 1
        else:
            prev = ts
    return count
