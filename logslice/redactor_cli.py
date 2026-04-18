"""CLI integration for redaction feature."""

import argparse
from typing import Iterable, Iterator, List

from logslice.redactor import compile_redact_patterns, redact_lines, BUILTIN_PATTERNS


def add_redact_args(parser: argparse.ArgumentParser) -> None:
    """Register redaction flags onto an existing argument parser."""
    parser.add_argument(
        "--redact",
        metavar="NAME",
        nargs="+",
        choices=list(BUILTIN_PATTERNS.keys()),
        default=[],
        help=f"Built-in patterns to redact: {', '.join(BUILTIN_PATTERNS)}",
    )
    parser.add_argument(
        "--redact-pattern",
        metavar="REGEX",
        nargs="+",
        default=[],
        dest="redact_pattern",
        help="Custom regex patterns to redact.",
    )
    parser.add_argument(
        "--redact-placeholder",
        metavar="TEXT",
        default="[REDACTED]",
        dest="redact_placeholder",
        help="Replacement text for redacted content (default: [REDACTED]).",
    )


def apply_redaction(args: argparse.Namespace, lines: Iterable[str]) -> Iterator[str]:
    """Apply redaction to lines based on parsed CLI args. Returns lines unchanged if no patterns."""
    builtin: List[str] = args.redact or []
    custom: List[str] = args.redact_pattern or []

    if not builtin and not custom:
        yield from lines
        return

    patterns = compile_redact_patterns(builtin, custom)
    placeholder: str = args.redact_placeholder
    yield from redact_lines(lines, patterns, placeholder)
