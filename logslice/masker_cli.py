"""masker_cli.py – CLI integration for the masker module."""

from __future__ import annotations

import argparse
from typing import Iterator, List, Optional

from logslice.masker import DEFAULT_PLACEHOLDER, compile_mask_rules, mask_lines


def add_mask_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--mask``, ``--mask-placeholder``, and ``--mask-ignore-case``
    flags on *parser*.
    """
    parser.add_argument(
        "--mask",
        metavar="PATTERN",
        action="append",
        dest="mask_patterns",
        default=[],
        help=(
            "Regex pattern whose first capturing group (or full match) is "
            "replaced with the placeholder.  May be repeated."
        ),
    )
    parser.add_argument(
        "--mask-placeholder",
        metavar="TEXT",
        default=DEFAULT_PLACEHOLDER,
        help=f"Replacement text for masked content (default: {DEFAULT_PLACEHOLDER!r}).",
    )
    parser.add_argument(
        "--mask-ignore-case",
        action="store_true",
        default=False,
        help="Match mask patterns case-insensitively.",
    )


def apply_masking(
    args: argparse.Namespace,
    lines: List[str],
) -> List[str]:
    """Return *lines* after applying any masking rules specified in *args*.

    If no ``--mask`` patterns were supplied the original list is returned
    unchanged.
    """
    patterns: List[str] = getattr(args, "mask_patterns", []) or []
    if not patterns:
        return lines

    placeholder: str = getattr(args, "mask_placeholder", DEFAULT_PLACEHOLDER)
    ignore_case: bool = getattr(args, "mask_ignore_case", False)

    rules = compile_mask_rules(patterns, placeholder=placeholder, ignore_case=ignore_case)
    return list(mask_lines(lines, rules))
