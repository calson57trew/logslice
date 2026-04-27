"""CLI integration for anomaly detection."""

from __future__ import annotations

import argparse
import sys
from typing import IO, List, Optional

from logslice.anomaly import AnomalyResult, detect_anomalies, format_anomalies


def add_anomaly_args(parser: argparse.ArgumentParser) -> None:
    """Register --anomaly-threshold and --anomaly-only flags on *parser*."""
    parser.add_argument(
        "--anomaly-threshold",
        metavar="SECONDS",
        type=float,
        default=None,
        help="Flag lines whose timestamp gap exceeds this many seconds.",
    )
    parser.add_argument(
        "--anomaly-only",
        action="store_true",
        default=False,
        help="Output only the anomaly report; suppress normal log lines.",
    )


def apply_anomaly(
    args: argparse.Namespace,
    lines: List[str],
    out: IO[str] = sys.stdout,
) -> List[str]:
    """Run anomaly detection when requested; return lines unchanged otherwise.

    If ``--anomaly-only`` is set the report is written to *out* and an empty
    list is returned so downstream stages receive nothing.
    """
    threshold: Optional[float] = getattr(args, "anomaly_threshold", None)
    if threshold is None:
        return lines

    only: bool = getattr(args, "anomaly_only", False)
    result: AnomalyResult = detect_anomalies(lines, threshold_seconds=threshold)
    out.write(format_anomalies(result))

    if only:
        return []
    return lines
