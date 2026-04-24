"""watchdog_cli.py – CLI integration for the watchdog / tail feature."""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Callable, Iterable

from .watchdog import watch_lines


def add_watch_args(parser: ArgumentParser) -> None:
    """Register --watch-pattern and --watch-alert flags on *parser*."""
    grp = parser.add_argument_group("watchdog")
    grp.add_argument(
        "--watch-pattern",
        metavar="REGEX",
        default=None,
        help="Emit an alert to stderr whenever a line matches REGEX.",
    )
    grp.add_argument(
        "--watch-ignore-case",
        action="store_true",
        default=False,
        help="Case-insensitive matching for --watch-pattern.",
    )
    grp.add_argument(
        "--watch-prefix",
        metavar="TEXT",
        default="[WATCH]",
        help="Prefix prepended to alert messages (default: '[WATCH]').",
    )


def apply_watch(
    args: Namespace,
    lines: Iterable[str],
) -> list[str]:
    """If --watch-pattern is set, monitor *lines* and print alerts to stderr.

    Always returns all lines unchanged.
    """
    if not getattr(args, "watch_pattern", None):
        return list(lines)

    flags = re.IGNORECASE if getattr(args, "watch_ignore_case", False) else 0
    pattern = re.compile(args.watch_pattern, flags)
    prefix: str = getattr(args, "watch_prefix", "[WATCH]")

    def _alert(line: str) -> None:
        msg = line.rstrip("\n")
        print(f"{prefix} {msg}", file=sys.stderr)

    predicate: Callable[[str], bool] = lambda ln: bool(pattern.search(ln))
    return watch_lines(list(lines), predicate, _alert)
