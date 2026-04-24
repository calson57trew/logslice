"""Normalize log lines: strip ANSI codes, collapse whitespace, unify line endings."""

import re
from typing import Iterable, Iterator

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_MULTI_SPACE = re.compile(r" {2,}")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def strip_ansi(line: str) -> str:
    """Remove ANSI escape sequences from *line*."""
    return _ANSI_ESCAPE.sub("", line)


def collapse_whitespace(line: str, *, preserve_indent: bool = False) -> str:
    """Collapse runs of spaces to a single space.

    If *preserve_indent* is True the leading whitespace is kept intact.
    """
    if preserve_indent:
        stripped = line.lstrip(" ")
        indent = line[: len(line) - len(stripped)]
        return indent + _MULTI_SPACE.sub(" ", stripped)
    return _MULTI_SPACE.sub(" ", line)


def strip_control_chars(line: str) -> str:
    """Remove non-printable control characters (excludes tab and newline)."""
    return _CONTROL_CHARS.sub("", line)


def normalize_line(
    line: str,
    *,
    ansi: bool = True,
    whitespace: bool = True,
    controls: bool = True,
    preserve_indent: bool = False,
) -> str:
    """Apply the requested normalization passes to a single log line.

    The trailing newline (if present) is preserved.
    """
    trailing_newline = line.endswith("\n")
    result = line.rstrip("\n")

    if ansi:
        result = strip_ansi(result)
    if controls:
        result = strip_control_chars(result)
    if whitespace:
        result = collapse_whitespace(result, preserve_indent=preserve_indent)
        result = result.strip(" ") if not preserve_indent else result.rstrip(" ")

    if trailing_newline:
        result += "\n"
    return result


def normalize_lines(
    lines: Iterable[str],
    *,
    ansi: bool = True,
    whitespace: bool = True,
    controls: bool = True,
    preserve_indent: bool = False,
) -> Iterator[str]:
    """Yield normalized versions of each line in *lines*."""
    for line in lines:
        yield normalize_line(
            line,
            ansi=ansi,
            whitespace=whitespace,
            controls=controls,
            preserve_indent=preserve_indent,
        )


def count_normalized(original: list[str], normalized: list[str]) -> int:
    """Return the number of lines that changed during normalization."""
    return sum(o != n for o, n in zip(original, normalized))
