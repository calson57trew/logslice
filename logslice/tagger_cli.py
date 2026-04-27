"""CLI integration for the tagger module."""

import argparse
from typing import List, Optional

from logslice.tagger import compile_tag_rules, tag_lines


def add_tag_args(parser: argparse.ArgumentParser) -> None:
    """Register tagging flags on an ArgumentParser."""
    parser.add_argument(
        "--tag",
        metavar="PATTERN=LABEL",
        action="append",
        dest="tags",
        default=[],
        help="Tag lines matching PATTERN with LABEL. Can be repeated.",
    )
    parser.add_argument(
        "--tag-multi",
        action="store_true",
        default=False,
        help="Allow multiple tags per line (default: first match wins).",
    )
    parser.add_argument(
        "--tag-suffix",
        action="store_true",
        default=False,
        help="Append tags as suffix instead of prefix.",
    )
    parser.add_argument(
        "--tag-only",
        action="store_true",
        default=False,
        help="Suppress lines that do not match any tag rule.",
    )


def _parse_tag_entry(entry: str) -> tuple:
    """Parse a single PATTERN=LABEL string into a (pattern, label) tuple.

    Raises ValueError if the entry does not contain an '=' separator or if
    either the pattern or label component is empty.
    """
    if "=" not in entry:
        raise ValueError(f"--tag value must be PATTERN=LABEL, got: {entry!r}")
    pattern, _, label = entry.partition("=")
    if not pattern:
        raise ValueError(f"--tag pattern must not be empty, got: {entry!r}")
    if not label:
        raise ValueError(f"--tag label must not be empty, got: {entry!r}")
    return pattern, label


def apply_tagging(args: argparse.Namespace, lines: List[str]) -> List[str]:
    """Apply tagging to lines based on parsed CLI args. Returns processed lines."""
    if not args.tags:
        return lines

    rules_raw = [_parse_tag_entry(entry) for entry in args.tags]

    rules = compile_tag_rules(rules_raw)
    result = list(
        tag_lines(
            lines,
            rules,
            multi=args.tag_multi,
            prefix=not args.tag_suffix,
            passthrough_untagged=not args.tag_only,
        )
    )
    return result
