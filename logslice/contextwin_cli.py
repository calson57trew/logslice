"""CLI integration for context window feature."""

import argparse
from typing import List, Optional

from logslice.contextwin import context_window
from logslice.filter import compile_pattern


def add_context_args(parser: argparse.ArgumentParser) -> None:
    """Register --before / --after / --context flags on *parser*."""
    grp = parser.add_argument_group("context window")
    grp.add_argument(
        "-B", "--before",
        metavar="N",
        type=int,
        default=0,
        help="Include N lines of context before each match (default: 0)",
    )
    grp.add_argument(
        "-A", "--after",
        metavar="N",
        type=int,
        default=0,
        help="Include N lines of context after each match (default: 0)",
    )
    grp.add_argument(
        "-C", "--context",
        metavar="N",
        type=int,
        default=None,
        help="Shorthand: set both --before and --after to N",
    )


def apply_context(
    args: argparse.Namespace,
    lines: List[str],
    pattern: Optional[str] = None,
) -> List[str]:
    """Apply context-window filtering to *lines* and return the result.

    *pattern* is a regex string used as the match predicate.  If neither
    a pattern nor a context size is specified the original lines are returned
    unchanged.
    """
    before: int = args.before
    after: int = args.after

    if args.context is not None:
        before = args.context
        after = args.context

    if before == 0 and after == 0:
        return lines

    if pattern is None:
        return lines

    regex = compile_pattern(pattern, ignore_case=True)
    predicate = lambda line: bool(regex.search(line))

    return list(context_window(lines, before=before, after=after, predicate=predicate))
