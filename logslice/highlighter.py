"""Optional ANSI highlighting for matched log lines."""

import re
from typing import Iterator, Optional

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_CYAN = "\033[36m"

LEVEL_COLORS = {
    "ERROR": "\033[31m",   # red
    "WARN":  "\033[33m",   # yellow
    "WARNING": "\033[33m",
    "INFO":  "\033[36m",   # cyan
    "DEBUG": "\033[37m",   # white
}

_LEVEL_RE = re.compile(
    r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR)\b", re.IGNORECASE
)


def highlight_level(line: str) -> str:
    """Colorize the first log-level keyword found in *line*."""
    match = _LEVEL_RE.search(line)
    if not match:
        return line
    level = match.group(1).upper()
    color = LEVEL_COLORS.get(level, ANSI_BOLD)
    start, end = match.span()
    return line[:start] + color + line[start:end] + ANSI_RESET + line[end:]


def highlight_pattern(line: str, pattern: str) -> str:
    """Highlight all occurrences of *pattern* (regex) in *line* in bold yellow."""
    try:
        highlighted = re.sub(
            pattern,
            lambda m: ANSI_YELLOW + ANSI_BOLD + m.group(0) + ANSI_RESET,
            line,
        )
    except re.error:
        return line
    return highlighted


def highlight_lines(
    lines: Iterator[str],
    *,
    levels: bool = True,
    pattern: Optional[str] = None,
) -> Iterator[str]:
    """Apply highlighting passes to each line and yield results."""
    for line in lines:
        if levels:
            line = highlight_level(line)
        if pattern:
            line = highlight_pattern(line, pattern)
        yield line
