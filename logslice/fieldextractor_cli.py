"""CLI integration for field extraction."""

from __future__ import annotations

import argparse
from typing import List, Optional

from logslice.fieldextractor import project_lines


def add_field_args(parser: argparse.ArgumentParser) -> None:
    """Register --fields and --field-sep flags on *parser*."""
    parser.add_argument(
        "--fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Extract these named fields (key=value) from each log line.",
    )
    parser.add_argument(
        "--field-sep",
        metavar="SEP",
        default="\t",
        help="Separator between projected field values (default: TAB).",
    )
    parser.add_argument(
        "--field-missing",
        metavar="STR",
        default="",
        help="Placeholder for fields absent in a line (default: empty string).",
    )


def apply_field_extraction(
    args: argparse.Namespace,
    lines: List[str],
) -> List[str]:
    """If --fields is set, project *lines* down to those fields; else pass through."""
    if not args.fields:
        return lines

    sep: str = args.field_sep.replace("\\t", "\t").replace("\\n", "\n")
    missing: str = args.field_missing

    return list(project_lines(lines, args.fields, separator=sep, missing=missing))
