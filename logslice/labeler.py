"""labeler.py — Attach static or dynamic labels to log lines.

Labels are prepended as a bracketed prefix, e.g. ``[app=web] 2024-01-01 ...``.
Dynamic labels are derived by matching a regex capture group named ``value``
against each line; if the group is absent the fallback label is used instead.
"""

from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# A label rule is a (key, value_or_pattern, is_dynamic) triple.
# When is_dynamic is True, value_or_pattern is a compiled regex that may
# contain a named group ``value``; the matched text becomes the label value.
LabelRule = Tuple[str, object, bool]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def compile_label_rules(
    static: Optional[List[Tuple[str, str]]] = None,
    dynamic: Optional[List[Tuple[str, str]]] = None,
    ignore_case: bool = False,
) -> List[LabelRule]:
    """Build a list of label rules from static and dynamic definitions.

    Parameters
    ----------
    static:
        List of ``(key, value)`` pairs applied unconditionally to every line.
    dynamic:
        List of ``(key, pattern)`` pairs where *pattern* is a regex.  If the
        regex matches the line and contains a ``(?P<value>...)`` group the
        captured text is used as the label value; otherwise the key itself is
        used as a boolean flag label.
    ignore_case:
        When *True* dynamic patterns are compiled with ``re.IGNORECASE``.

    Returns
    -------
    list of LabelRule triples ready for :func:`label_line`.
    """
    rules: List[LabelRule] = []
    flags = re.IGNORECASE if ignore_case else 0

    for key, value in (static or []):
        rules.append((key, value, False))

    for key, pattern in (dynamic or []):
        compiled = re.compile(pattern, flags)
        rules.append((key, compiled, True))

    return rules


def label_line(line: str, rules: List[LabelRule], fallback: str = "") -> str:
    """Return *line* with any matching label prefixes prepended.

    Labels are formatted as ``[key=value]`` and joined with a single space
    before the original line content.  Lines that already end with ``\\n``
    retain their newline at the end.

    Parameters
    ----------
    line:
        The raw log line (may include a trailing newline).
    rules:
        Compiled label rules produced by :func:`compile_label_rules`.
    fallback:
        Value used for dynamic rules whose pattern matches but has no
        ``value`` capture group.
    """
    stripped = line.rstrip("\n")
    trailing = "\n" if line.endswith("\n") else ""

    prefixes: List[str] = []
    for key, rule, is_dynamic in rules:
        if is_dynamic:
            m = rule.search(stripped)  # type: ignore[union-attr]
            if m:
                try:
                    val = m.group("value")
                except IndexError:
                    val = fallback or key
                prefixes.append(f"[{key}={val}]")
        else:
            prefixes.append(f"[{key}={rule}]")

    if not prefixes:
        return line

    prefix_str = " ".join(prefixes)
    return f"{prefix_str} {stripped}{trailing}"


def label_lines(
    lines: Iterable[str],
    rules: List[LabelRule],
    fallback: str = "",
) -> Iterator[str]:
    """Apply :func:`label_line` to every line in *lines*."""
    for line in lines:
        yield label_line(line, rules, fallback=fallback)


def count_labeled(lines: Iterable[str], rules: List[LabelRule]) -> Tuple[int, int]:
    """Return ``(total, labeled)`` counts after processing *lines*.

    *labeled* counts lines that received at least one label prefix.
    """
    total = 0
    labeled = 0
    for line in lines:
        total += 1
        result = label_line(line, rules)
        if result != line:
            labeled += 1
    return total, labeled
