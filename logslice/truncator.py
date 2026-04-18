"""Truncate long log lines for display purposes."""

from typing import Iterable, Iterator

DEFAULT_MAX_LENGTH = 200
ELLIPSIS = "..."


def truncate_line(line: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """Truncate a single line to max_length, appending ellipsis if cut."""
    if max_length <= 0:
        raise ValueError("max_length must be a positive integer")
    line = line.rstrip("\n")
    if len(line) <= max_length:
        return line
    return line[:max_length - len(ELLIPSIS)] + ELLIPSIS


def truncate_lines(
    lines: Iterable[str],
    max_length: int = DEFAULT_MAX_LENGTH,
    only_long: bool = False,
) -> Iterator[str]:
    """Yield truncated lines from an iterable.

    Args:
        lines: Input log lines.
        max_length: Maximum character length per line.
        only_long: If True, yield only lines that were actually truncated.
    """
    for line in lines:
        original = line.rstrip("\n")
        result = truncate_line(original, max_length)
        if only_long and result == original:
            continue
        yield result


def count_truncated(lines: Iterable[str], max_length: int = DEFAULT_MAX_LENGTH) -> int:
    """Return the number of lines that exceed max_length."""
    return sum(1 for line in lines if len(line.rstrip("\n")) > max_length)
