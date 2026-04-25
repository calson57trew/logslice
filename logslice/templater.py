"""Template-based line formatting for logslice output."""
from __future__ import annotations

import re
import string
from typing import Iterable, Iterator

from logslice.parser import extract_timestamp

# Regex to detect log level in a line
_LEVEL_RE = re.compile(
    r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b", re.IGNORECASE
)


def _extract_level(line: str) -> str:
    """Return the first log-level token found in *line*, or empty string."""
    m = _LEVEL_RE.search(line)
    return m.group(1).upper() if m else ""


def _extract_message(line: str) -> str:
    """Return the portion of *line* after the timestamp (if any)."""
    ts = extract_timestamp(line)
    if ts is None:
        return line.rstrip("\n")
    # Strip the matched timestamp prefix from the raw line
    stripped = re.sub(
        r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?",
        "",
        line.rstrip("\n"),
    ).lstrip(" |\t:-")
    return stripped


def render_template(template: str, line: str, index: int = 0) -> str:
    """Render *template* substituting placeholders for fields extracted from *line*.

    Supported placeholders:
      {line}      – the raw line (stripped of trailing newline)
      {timestamp} – ISO-8601 timestamp or empty string
      {level}     – log level or empty string
      {message}   – line content after the timestamp
      {index}     – 1-based line index
    """
    ts = extract_timestamp(line) or ""
    level = _extract_level(line)
    message = _extract_message(line)
    raw = line.rstrip("\n")
    try:
        return template.format(
            line=raw,
            timestamp=ts,
            level=level,
            message=message,
            index=index,
        )
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Invalid template '{template}': {exc}") from exc


def template_lines(
    lines: Iterable[str],
    template: str,
    start_index: int = 1,
) -> Iterator[str]:
    """Yield each line rendered through *template*."""
    for i, line in enumerate(lines, start=start_index):
        yield render_template(template, line, index=i) + "\n"


def count_templated(lines: Iterable[str], template: str) -> tuple[list[str], int]:
    """Return (rendered_lines, count) for all lines processed."""
    result = list(template_lines(lines, template))
    return result, len(result)
