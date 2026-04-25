"""Field extraction: pull named fields from structured log lines."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

# Matches key=value or key="value with spaces"
_FIELD_RE = re.compile(r'(\w+)=(?:"([^"]*)"|([^\s]*))')


def extract_fields(line: str) -> Dict[str, str]:
    """Return a dict of key=value pairs found in *line*."""
    result: Dict[str, str] = {}
    for m in _FIELD_RE.finditer(line):
        key = m.group(1)
        value = m.group(2) if m.group(2) is not None else m.group(3)
        result[key] = value
    return result


def pick_fields(
    line: str,
    fields: List[str],
    missing: str = "",
) -> Dict[str, str]:
    """Return only the requested *fields* from *line*.

    Fields absent in the line are set to *missing*.
    """
    all_fields = extract_fields(line)
    return {f: all_fields.get(f, missing) for f in fields}


def project_lines(
    lines: Iterable[str],
    fields: List[str],
    separator: str = "\t",
    missing: str = "",
) -> Iterator[str]:
    """Yield tab-separated (or *separator*-separated) field values for each line.

    Lines that contain no matching fields are yielded as a row of *missing* values.
    """
    for line in lines:
        values = pick_fields(line.rstrip("\n"), fields, missing=missing)
        yield separator.join(values[f] for f in fields) + "\n"


def count_extracted(lines: Iterable[str], field: str) -> Tuple[int, int]:
    """Return (total_lines, lines_where_field_present) for *field*."""
    total = 0
    present = 0
    for line in lines:
        total += 1
        if field in extract_fields(line):
            present += 1
    return total, present
