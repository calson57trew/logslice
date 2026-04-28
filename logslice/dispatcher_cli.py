"""CLI integration for the dispatcher module."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .dispatcher import compile_dispatch_rules, dispatch_lines


def add_dispatch_args(parser: argparse.ArgumentParser) -> None:
    """Register --dispatch, --dispatch-default, and --dispatch-ignore-case flags."""
    parser.add_argument(
        "--dispatch",
        metavar="CHANNEL:PATTERN",
        action="append",
        dest="dispatch_rules",
        default=[],
        help=(
            "Route matching lines to CHANNEL. "
            "May be repeated. Format: channel:pattern"
        ),
    )
    parser.add_argument(
        "--dispatch-default",
        metavar="CHANNEL",
        default=None,
        dest="dispatch_default",
        help="Channel name for lines that match no rule (default: unrouted bucket).",
    )
    parser.add_argument(
        "--dispatch-ignore-case",
        action="store_true",
        default=False,
        dest="dispatch_ignore_case",
        help="Match dispatch patterns case-insensitively.",
    )
    parser.add_argument(
        "--dispatch-show",
        metavar="CHANNEL",
        default=None,
        dest="dispatch_show",
        help="Emit only lines routed to this channel (pass-through mode).",
    )


def _parse_rule_entry(entry: str):
    """Split 'channel:pattern' into (channel, pattern). Raises ValueError on bad format."""
    if ":" not in entry:
        raise ValueError(
            f"Invalid --dispatch value {entry!r}: expected 'channel:pattern'"
        )
    channel, _, pattern = entry.partition(":")
    if not channel or not pattern:
        raise ValueError(
            f"Invalid --dispatch value {entry!r}: channel and pattern must be non-empty"
        )
    return channel, pattern


def apply_dispatch(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Apply dispatch rules; return lines for --dispatch-show channel or all lines."""
    if not args.dispatch_rules:
        return lines

    if out is None:
        out = sys.stderr

    raw_rules = [_parse_rule_entry(e) for e in args.dispatch_rules]
    rules = compile_dispatch_rules(
        raw_rules, ignore_case=args.dispatch_ignore_case
    )
    result = dispatch_lines(lines, rules, default_channel=args.dispatch_default)

    out.write(
        f"[dispatch] total={result.total} dispatched={result.dispatched} "
        f"channels={result.all_channels()}\n"
    )

    if args.dispatch_show:
        from .dispatcher import iter_channel
        return list(iter_channel(result, args.dispatch_show))

    return lines
