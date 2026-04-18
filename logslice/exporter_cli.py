"""CLI integration for the exporter module."""

import argparse
import sys
from typing import Iterable, Iterator, List

from logslice.exporter import get_exporter, SUPPORTED_FORMATS


def add_export_args(parser: argparse.ArgumentParser) -> None:
    """Register --export-format flag on an existing ArgumentParser."""
    parser.add_argument(
        "--export-format",
        dest="export_format",
        choices=SUPPORTED_FORMATS,
        default=None,
        metavar="FMT",
        help=(
            "Export output in the given format instead of plain text. "
            f"Choices: {', '.join(SUPPORTED_FORMATS)}."
        ),
    )
    parser.add_argument(
        "--export-file",
        dest="export_file",
        default=None,
        metavar="PATH",
        help="Write exported output to PATH instead of stdout.",
    )


def apply_export(
    args: argparse.Namespace,
    lines: Iterable[str],
) -> List[str]:
    """If --export-format is set, convert and write lines; return original list.

    The original lines are always returned so the pipeline can continue.
    """
    materialized = list(lines)
    if not args.export_format:
        return materialized

    exporter = get_exporter(args.export_format)
    exported = list(exporter(iter(materialized)))

    if args.export_file:
        with open(args.export_file, "w", encoding="utf-8") as fh:
            fh.writelines(exported)
    else:
        sys.stdout.writelines(exported)

    return materialized
