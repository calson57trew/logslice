"""Output formatting for logslice results."""

from typing import Iterable, Optional
import json


def format_lines_plain(lines: Iterable[str]) -> Iterable[str]:
    """Yield lines as-is (plain text output)."""
    for line in lines:
        yield line


def format_lines_json(lines: Iterable[str]) -> Iterable[str]:
    """Wrap each line in a JSON object with an index and text field."""
    for i, line in enumerate(lines):
        yield json.dumps({"index": i, "line": line.rstrip("\n")})


def format_lines_numbered(lines: Iterable[str], start: int = 1) -> Iterable[str]:
    """Yield lines prefixed with line numbers."""
    for i, line in enumerate(lines, start=start):
        yield f"{i:>6}  {line}"


FORMATS = {
    "plain": format_lines_plain,
    "json": format_lines_json,
    "numbered": format_lines_numbered,
}


def get_formatter(fmt: str):
    """Return a formatter callable by name, defaulting to plain."""
    if fmt not in FORMATS:
        raise ValueError(
            f"Unknown format {fmt!r}. Choose from: {', '.join(FORMATS)}"
        )
    return FORMATS[fmt]


def write_output(lines: Iterable[str], fmt: str = "plain", output=None) -> int:
    """Format and write lines to output (file-like or stdout).

    Returns the number of lines written.
    """
    import sys

    out = output or sys.stdout
    formatter = get_formatter(fmt)
    count = 0
    for formatted in formatter(lines):
        out.write(formatted)
        if not formatted.endswith("\n"):
            out.write("\n")
        count += 1
    return count
