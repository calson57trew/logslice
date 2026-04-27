"""columnar.py – render log lines as fixed-width columns by splitting on a delimiter."""
from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional


def split_columns(line: str, delimiter: str = r"\s+", max_cols: Optional[int] = None) -> List[str]:
    """Split *line* into columns using *delimiter* (regex).  Strips trailing newline first."""
    text = line.rstrip("\n")
    parts = re.split(delimiter, text)
    if max_cols and len(parts) > max_cols:
        # merge overflow into the last column
        parts = parts[: max_cols - 1] + [re.split(delimiter, text, maxsplit=max_cols - 1)[-1]]
    return parts


def _widths(rows: List[List[str]]) -> List[int]:
    """Return the max character width for each column position across all rows."""
    if not rows:
        return []
    ncols = max(len(r) for r in rows)
    widths = [0] * ncols
    for row in rows:
        for i, cell in enumerate(row):
            if len(cell) > widths[i]:
                widths[i] = len(cell)
    return widths


def format_columns(
    lines: Iterable[str],
    delimiter: str = r"\s+",
    max_cols: Optional[int] = None,
    pad_char: str = " ",
    separator: str = "  ",
) -> Iterator[str]:
    """Yield lines formatted as aligned columns.

    All input lines are buffered so that column widths can be computed before
    any output is produced.
    """
    rows = [split_columns(ln, delimiter=delimiter, max_cols=max_cols) for ln in lines]
    widths = _widths(rows)
    for row in rows:
        cells = [
            cell.ljust(widths[i], pad_char) if i < len(widths) - 1 else cell
            for i, cell in enumerate(row)
        ]
        yield separator.join(cells) + "\n"


def count_columns(lines: Iterable[str], delimiter: str = r"\s+") -> int:
    """Return the maximum number of columns found across all lines."""
    maximum = 0
    for line in lines:
        n = len(split_columns(line, delimiter=delimiter))
        if n > maximum:
            maximum = n
    return maximum
