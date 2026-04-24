"""CLI integration for the scorer module."""
from __future__ import annotations

import argparse
from typing import Iterable

from logslice.scorer import compile_score_rules, score_lines, top_lines


def add_score_args(parser: argparse.ArgumentParser) -> None:
    """Register --score, --score-threshold, and --score-top flags."""
    parser.add_argument(
        "--score",
        metavar="PATTERN:WEIGHT",
        action="append",
        dest="score_rules",
        default=[],
        help="Score rule as PATTERN:WEIGHT (may be repeated).",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=0.0,
        metavar="N",
        help="Only emit lines with score >= N (default: 0.0).",
    )
    parser.add_argument(
        "--score-top",
        type=int,
        default=None,
        metavar="N",
        help="Emit only the top-N highest-scored lines.",
    )
    parser.add_argument(
        "--score-case-sensitive",
        action="store_true",
        default=False,
        help="Make scoring patterns case-sensitive.",
    )


def _parse_rule(rule_str: str) -> tuple[str, float]:
    """Split 'PATTERN:WEIGHT' into (pattern, weight)."""
    *parts, weight_str = rule_str.rsplit(":", 1)
    pattern = ":".join(parts)
    return pattern, float(weight_str)


def apply_scoring(
    args: argparse.Namespace, lines: Iterable[str]
) -> Iterable[str]:
    """Apply scoring pipeline; returns plain lines, possibly reordered."""
    if not args.score_rules:
        return lines

    raw_rules = [_parse_rule(r) for r in args.score_rules]
    ignore_case = not args.score_case_sensitive
    compiled = compile_score_rules(raw_rules, ignore_case=ignore_case)

    if args.score_top is not None:
        results = top_lines(list(lines), compiled, n=args.score_top)
    else:
        results = list(
            score_lines(lines, compiled, threshold=args.score_threshold)
        )

    return [r.line for r in results]
