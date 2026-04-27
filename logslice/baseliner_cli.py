"""CLI integration for the baseliner module."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.baseliner import (
    BaselineResult,
    compare_to_baseline,
    format_baseline_summary,
    load_baseline,
    save_baseline,
)


def add_baseline_args(parser: argparse.ArgumentParser) -> None:
    """Register --baseline-* flags on *parser*."""
    grp = parser.add_argument_group("baseliner")
    grp.add_argument(
        "--baseline-file",
        metavar="PATH",
        default=None,
        help="Path to the baseline JSON fingerprint file.",
    )
    grp.add_argument(
        "--baseline-save",
        action="store_true",
        default=False,
        help="Save current input lines as the new baseline (overwrites).",
    )
    grp.add_argument(
        "--baseline-summary",
        action="store_true",
        default=False,
        help="Print a comparison summary to stderr after processing.",
    )
    grp.add_argument(
        "--baseline-emit-known",
        action="store_true",
        default=False,
        help="Emit known (baseline) lines as well as new ones.",
    )


def apply_baseline(
    args: argparse.Namespace,
    lines: List[str],
    *,
    out=None,
) -> List[str]:
    """Apply baseline logic to *lines*; returns the (possibly filtered) list."""
    if out is None:
        out = sys.stderr

    if not getattr(args, "baseline_file", None):
        return lines

    path: str = args.baseline_file
    save: bool = getattr(args, "baseline_save", False)
    summary: bool = getattr(args, "baseline_summary", False)
    emit_known: bool = getattr(args, "baseline_emit_known", False)

    if save:
        count = save_baseline(path, lines)
        if summary:
            print(f"Baseline saved: {count} fingerprints → {path}", file=out)
        return lines

    baseline = load_baseline(path)
    result: BaselineResult = compare_to_baseline(lines, baseline, emit_known=emit_known)

    if summary:
        print(format_baseline_summary(result), file=out)

    if emit_known:
        return lines  # pass all through when caller wants everything
    return result.new_lines
