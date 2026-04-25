"""CLI helpers for the transformer feature."""

from __future__ import annotations

import argparse
from typing import List

from logslice.transformer import compile_transforms, transform_lines


def add_transform_args(parser: argparse.ArgumentParser) -> None:
    """Register --transform flags on *parser*."""
    parser.add_argument(
        "--upper",
        action="store_true",
        default=False,
        help="Convert each line to uppercase.",
    )
    parser.add_argument(
        "--lower",
        action="store_true",
        default=False,
        help="Convert each line to lowercase.",
    )
    parser.add_argument(
        "--strip",
        action="store_true",
        default=False,
        help="Strip leading/trailing whitespace from each line.",
    )
    parser.add_argument(
        "--replace",
        metavar=("PATTERN", "REPLACEMENT"),
        nargs=2,
        action="append",
        default=[],
        help="Replace regex PATTERN with REPLACEMENT (repeatable).",
    )
    parser.add_argument(
        "--transform-ignore-case",
        action="store_true",
        default=False,
        help="Apply replace patterns case-insensitively.",
    )


def apply_transform(args: argparse.Namespace, lines: List[str]) -> List[str]:
    """Return *lines* after applying any transform flags present in *args*."""
    ops = []
    if getattr(args, "upper", False):
        ops.append(("upper",))
    if getattr(args, "lower", False):
        ops.append(("lower",))
    if getattr(args, "strip", False):
        ops.append(("strip",))
    for pattern, replacement in getattr(args, "replace", []) or []:
        ops.append(("replace", pattern, replacement))

    if not ops:
        return lines

    ignore_case = getattr(args, "transform_ignore_case", False)
    transforms = compile_transforms(ops, ignore_case=ignore_case)
    return list(transform_lines(lines, transforms))
