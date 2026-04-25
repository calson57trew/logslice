"""CLI integration for the templater feature."""
from __future__ import annotations

import argparse
from typing import Iterable

from logslice.templater import template_lines

_DEFAULT_TEMPLATE = "{line}"


def add_template_args(parser: argparse.ArgumentParser) -> None:
    """Register --template flag on *parser*."""
    parser.add_argument(
        "--template",
        metavar="TMPL",
        default=None,
        help=(
            "Format each output line using a Python str.format template. "
            "Available fields: {line}, {timestamp}, {level}, {message}, {index}. "
            "Example: '[{timestamp}] {level}: {message}'"
        ),
    )
    parser.add_argument(
        "--template-start",
        metavar="N",
        type=int,
        default=1,
        help="Starting value for the {index} placeholder (default: 1).",
    )


def apply_template(
    args: argparse.Namespace,
    lines: Iterable[str],
) -> Iterable[str]:
    """If --template is set, render all *lines* through the template.

    Returns the (possibly transformed) iterable of lines.
    """
    template: str | None = getattr(args, "template", None)
    if not template:
        return lines
    start: int = getattr(args, "template_start", 1)
    return list(template_lines(lines, template, start_index=start))
