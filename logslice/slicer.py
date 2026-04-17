"""Core log slicing logic — filter lines by timestamp range."""

from datetime import datetime
from typing import IO, Iterator, Optional

from logslice.parser import extract_timestamp, parse_user_timestamp


def slice_logs(
    source: IO[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Iterator[str]:
    """
    Yield log lines whose timestamps fall within [start, end].

    Lines without a parseable timestamp are included only if they
    fall between timestamped lines that are in range (continuation lines).
    """
    start_dt: Optional[datetime] = parse_user_timestamp(start) if start else None
    end_dt: Optional[datetime] = parse_user_timestamp(end) if end else None

    in_range = start_dt is None  # if no start, begin immediately
    pending_continuation: list[str] = []

    for line in source:
        ts = extract_timestamp(line)

        if ts is not None:
            if end_dt and ts > end_dt:
                break
            if start_dt and ts < start_dt:
                in_range = False
                pending_continuation = []
                continue
            in_range = True
            pending_continuation = []

        if in_range:
            if ts is None:
                pending_continuation.append(line)
            else:
                yield from pending_continuation
                pending_continuation = []
                yield line
        else:
            pending_continuation = []

    if in_range:
        yield from pending_continuation
