"""masker.py – selectively mask fields or substrings in log lines.

Provides pattern-based masking where matched groups are replaced with a
configurable placeholder (default: ``***``).
"""

from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# (compiled-pattern, placeholder) pairs
MaskRule = Tuple[re.Pattern, str]

DEFAULT_PLACEHOLDER = "***"


def compile_mask_rules(
    patterns: Iterable[str],
    placeholder: str = DEFAULT_PLACEHOLDER,
    ignore_case: bool = False,
) -> List[MaskRule]:
    """Compile a list of regex strings into MaskRule pairs.

    Each pattern should contain at least one capturing group; only the
    content of the first group is replaced.  If no group is present the
    entire match is replaced.
    """
    flags = re.IGNORECASE if ignore_case else 0
    rules: List[MaskRule] = []
    for raw in patterns:
        rules.append((re.compile(raw, flags), placeholder))
    return rules


def mask_line(line: str, rules: List[MaskRule]) -> str:
    """Apply all *rules* to *line*, replacing matched content with placeholders.

    When a pattern contains a capturing group the group's span is replaced;
    otherwise the full match span is replaced.
    """
    for pattern, placeholder in rules:
        def _replace(m: re.Match) -> str:  # noqa: E306
            if m.lastindex:  # at least one capturing group
                start = m.start(1)
                end = m.end(1)
                return m.group(0)[: start - m.start(0)] + placeholder + m.group(0)[end - m.start(0) :]
            return placeholder

        line = pattern.sub(_replace, line)
    return line


def mask_lines(
    lines: Iterable[str],
    rules: List[MaskRule],
) -> Iterator[str]:
    """Yield each line after applying all masking rules."""
    for line in lines:
        yield mask_line(line, rules)


def count_masked(original: Iterable[str], rules: List[MaskRule]) -> int:
    """Return the number of lines that were changed by masking."""
    changed = 0
    for line in original:
        if mask_line(line, rules) != line:
            changed += 1
    return changed
