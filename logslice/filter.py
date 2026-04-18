"""Pattern-based line filtering for logslice."""

import re
from typing import Iterable, Iterator, Optional


def compile_pattern(pattern: str, ignore_case: bool = False) -> re.Pattern:
    """Compile a regex pattern with optional case-insensitivity."""
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def filter_lines(
    lines: Iterable[str],
    include_pattern: Optional[re.Pattern] = None,
    exclude_pattern: Optional[re.Pattern] = None,
    keep_continuations: bool = True,
) -> Iterator[str]:
    """
    Yield lines that match include_pattern and do not match exclude_pattern.

    Continuation lines (lines starting with whitespace) are kept or dropped
    based on the keep_continuations flag, following the last anchor line's fate.
    """
    last_anchor_kept: bool = False

    for line in lines:
        is_continuation = line and line[0] in (" ", "\t")

        if is_continuation and keep_continuations:
            if last_anchor_kept:
                yield line
            continue

        passes = True
        if include_pattern and not include_pattern.search(line):
            passes = False
        if exclude_pattern and exclude_pattern.search(line):
            passes = False

        last_anchor_kept = passes
        if passes:
            yield line


def filter_by_level(
    lines: Iterable[str],
    levels: list[str],
    ignore_case: bool = True,
) -> Iterator[str]:
    """Yield only lines whose log level matches one of the given levels."""
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(l) for l in levels) + r")\b", flags
    )
    for line in lines:
        if pattern.search(line):
            yield line
