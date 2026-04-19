"""Tag log lines with custom labels based on pattern matching."""

import re
from typing import Iterable, Iterator, List, Optional, Tuple


def compile_tag_rules(rules: List[Tuple[str, str]], ignore_case: bool = True) -> List[Tuple[re.Pattern, str]]:
    """Compile a list of (pattern, tag) tuples into (compiled_regex, tag) pairs."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = []
    for pattern, tag in rules:
        compiled.append((re.compile(pattern, flags), tag))
    return compiled


def tag_line(line: str, rules: List[Tuple[re.Pattern, str]], multi: bool = False) -> List[str]:
    """Return list of tags that match the line. If multi=False, return first match only."""
    tags = []
    for regex, tag in rules:
        if regex.search(line):
            tags.append(tag)
            if not multi:
                break
    return tags


def apply_tag(line: str, tags: List[str], prefix: bool = True) -> str:
    """Attach tags to a line. Prepends '[tag1,tag2] ' or appends ' #tag1,tag2'."""
    if not tags:
        return line
    label = ",".join(tags)
    stripped = line.rstrip("\n")
    if prefix:
        return f"[{label}] {stripped}\n"
    return f"{stripped} #{label}\n"


def tag_lines(
    lines: Iterable[str],
    rules: List[Tuple[re.Pattern, str]],
    multi: bool = False,
    prefix: bool = True,
    passthrough_untagged: bool = True,
) -> Iterator[str]:
    """Yield lines with tags applied. Untagged lines passed through if passthrough_untagged."""
    for line in lines:
        tags = tag_line(line, rules, multi=multi)
        if tags:
            yield apply_tag(line, tags, prefix=prefix)
        elif passthrough_untagged:
            yield line


def count_tagged(lines: Iterable[str], rules: List[Tuple[re.Pattern, str]], multi: bool = False) -> int:
    """Count how many lines match at least one tag rule."""
    return sum(1 for line in lines if tag_line(line, rules, multi=multi))
