"""Classify log lines into named categories based on pattern rules."""

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# Each rule is (category_name, compiled_pattern)
ClassifyRule = Tuple[str, re.Pattern]

_BUILTIN_CATEGORIES = {
    "error": re.compile(r"\b(error|exception|fatal|critical)\b", re.IGNORECASE),
    "warning": re.compile(r"\b(warn(?:ing)?)\b", re.IGNORECASE),
    "info": re.compile(r"\b(info|notice)\b", re.IGNORECASE),
    "debug": re.compile(r"\b(debug|trace|verbose)\b", re.IGNORECASE),
}


def compile_classify_rules(
    rules: List[Tuple[str, str]]
) -> List[ClassifyRule]:
    """Compile a list of (category, pattern_str) pairs into ClassifyRules."""
    return [(cat, re.compile(pat)) for cat, pat in rules]


def classify_line(
    line: str,
    rules: List[ClassifyRule],
    default: str = "unclassified",
    multi: bool = False,
) -> List[str]:
    """Return categories that match *line*.

    If *multi* is False (default) only the first matching category is returned.
    Returns [*default*] when no rule matches.
    """
    matched: List[str] = []
    for cat, pattern in rules:
        if pattern.search(line):
            matched.append(cat)
            if not multi:
                return matched
    return matched if matched else [default]


def classify_lines(
    lines: Iterable[str],
    rules: List[ClassifyRule],
    default: str = "unclassified",
    multi: bool = False,
    tag: bool = False,
) -> Iterator[str]:
    """Yield lines, optionally prepending a ``[category]`` tag.

    When *tag* is True the first matched category is prepended to each line.
    """
    for line in lines:
        cats = classify_line(line, rules, default=default, multi=multi)
        if tag:
            prefix = "[{}] ".format(cats[0])
            stripped = line.rstrip("\n")
            yield prefix + stripped + "\n"
        else:
            yield line


def count_classified(
    lines: Iterable[str],
    rules: List[ClassifyRule],
    default: str = "unclassified",
) -> dict:
    """Return a dict mapping category -> count for *lines*."""
    counts: dict = {}
    for line in lines:
        for cat in classify_line(line, rules, default=default, multi=True):
            counts[cat] = counts.get(cat, 0) + 1
    return counts


def builtin_rules() -> List[ClassifyRule]:
    """Return pre-compiled rules for common log levels."""
    return [(cat, pat) for cat, pat in _BUILTIN_CATEGORIES.items()]
