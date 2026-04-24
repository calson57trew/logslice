"""alerter_cli.py — CLI integration for the alerter module."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.alerter import AlertEvent, AlertRule, alert_lines, compile_alert_rules


def add_alert_args(parser: argparse.ArgumentParser) -> None:
    """Register --alert and --alert-threshold flags on *parser*."""
    parser.add_argument(
        "--alert",
        metavar="PATTERN:LABEL",
        action="append",
        dest="alert_rules",
        default=[],
        help=(
            "Emit an alert when PATTERN matches.  "
            "May be repeated.  Format: PATTERN:LABEL or PATTERN:LABEL:THRESHOLD."
        ),
    )
    parser.add_argument(
        "--alert-ignore-case",
        action="store_true",
        default=False,
        help="Match alert patterns case-insensitively.",
    )
    parser.add_argument(
        "--alert-out",
        metavar="FILE",
        default=None,
        help="Write alert events to FILE (default: stderr).",
    )


def _parse_rule(spec: str) -> tuple:
    """Parse 'PATTERN:LABEL' or 'PATTERN:LABEL:THRESHOLD' into a 3-tuple."""
    parts = spec.split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid alert rule (expected PATTERN:LABEL): {spec!r}")
    pattern = parts[0]
    label = parts[1]
    threshold = int(parts[2]) if len(parts) == 3 else 1
    return pattern, label, threshold


def apply_alerting(
    args: argparse.Namespace,
    lines: List[str],
) -> List[str]:
    """Apply alert rules from *args* to *lines*; return lines unchanged.

    Side-effect: writes alert events to stderr (or --alert-out file).
    """
    if not args.alert_rules:
        return lines

    raw_rules = [_parse_rule(spec) for spec in args.alert_rules]
    rules = compile_alert_rules(raw_rules, ignore_case=args.alert_ignore_case)

    alert_dest = open(args.alert_out, "w") if args.alert_out else sys.stderr  # noqa: SIM115
    try:
        out_lines: List[str] = []
        for line, event in alert_lines(lines, rules):
            out_lines.append(line)
            if event is not None:
                ts_part = f" [{event.timestamp}]" if event.timestamp else ""
                alert_dest.write(
                    f"ALERT {event.label}{ts_part} (count={event.count}): {event.line}\n"
                )
    finally:
        if args.alert_out:
            alert_dest.close()

    return out_lines
