"""CLI integration for the log router feature."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.router import (
    RouteRule,
    RoutedLine,
    collect_sinks,
    compile_route_rules,
    route_lines,
)


def add_route_args(parser: argparse.ArgumentParser) -> None:
    """Register --route and --route-default flags on *parser*."""
    parser.add_argument(
        "--route",
        metavar="PATTERN:SINK",
        action="append",
        default=[],
        dest="route_rules",
        help="Route lines matching PATTERN to SINK (repeatable).",
    )
    parser.add_argument(
        "--route-default",
        metavar="SINK",
        default="default",
        dest="route_default",
        help="Sink name for lines that match no rule (default: 'default').",
    )
    parser.add_argument(
        "--route-ignore-case",
        action="store_true",
        default=False,
        dest="route_ignore_case",
        help="Match route patterns case-insensitively.",
    )
    parser.add_argument(
        "--route-show-sink",
        action="store_true",
        default=False,
        dest="route_show_sink",
        help="Prefix each output line with its sink name.",
    )


def apply_routing(
    args: argparse.Namespace,
    lines: List[str],
    out=None,
) -> List[str]:
    """Apply routing rules; return lines unchanged when no rules are given."""
    if out is None:
        out = sys.stdout

    if not args.route_rules:
        return lines

    raw_rules = []
    for spec in args.route_rules:
        if ":" not in spec:
            raise ValueError(f"--route value must be PATTERN:SINK, got: {spec!r}")
        pattern, _, sink = spec.partition(":")
        raw_rules.append((pattern, sink))

    rules = compile_route_rules(raw_rules, ignore_case=args.route_ignore_case)
    routed = list(route_lines(lines, rules, default_sink=args.route_default))

    if args.route_show_sink:
        return [f"[{rl.sink}] {rl.line}" for rl in routed]

    return [rl.line for rl in routed]
