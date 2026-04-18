"""Redact sensitive patterns from log lines."""

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# Common built-in patterns
BUILTIN_PATTERNS: dict[str, str] = {
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "token": r"(?i)(?:token|key|secret|password)[=:\s]+\S+",
    "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
}

REDACT_PLACEHOLDER = "[REDACTED]"

_redact_patterns(
    names: List[str],
    custom: Optional[List[str]] = None[re.Pattern]:
    """Return compiled patterns from builtin names and optional custom regexes."""
    patterns: List[re.Pattern] = []
    for name in names:
        if name in BUILTIN_PATTERNS:
            patterns.append(re.compile(BUILTIN_PATTERNS[name]))
        else:
            raise ValueError(f"Unknown builtin redact pattern: {name!r}")
    for expr in (custom or []):
        patterns.append(re.compile(expr))
    return patterns


def redact_line(line: str, patterns: List[re.Pattern], placeholder: str = REDACT_PLACEHOLDER) -> Tuple[str, int]:
    """Apply all patterns to a single line. Returns (redacted_line, substitution_count)."""
    count = 0
    for pat in patterns:
        line, n = pat.subn(placeholder, line)
        count += n
    return line, count


def redact_lines(
    lines: Iterable[str],
    patterns: List[re.Pattern],
    placeholder: str = REDACT_PLACEHOLDER,
) -> Iterator[str]:
    """Yield redacted lines, applying all patterns to each line."""
    for line in lines:
        redacted, _ = redact_line(line, patterns, placeholder)
        yield redacted


def count_redactions(lines: Iterable[str], patterns: List[re.Pattern]) -> int:
    """Return total number of redactions across all lines."""
    total = 0
    for line in lines:
        _, n = redact_line(line, patterns)
        total += n
    return total
