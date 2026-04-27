"""windower_cli.py – CLI integration for tumbling-window aggregation."""
from __future__ import annotations

import argparse
from typing import List

from logslice.windower import tumbling_windows


def add_window_args(parser: argparse.ArgumentParser) -> None:
    """Register --window and --window-summary flags on *parser*."""
    grp = parser.add_argument_group("windowing")
    grp.add_argument(
        "--window",
        metavar="SECONDS",
        type=int,
        default=None,
        help="Group lines into tumbling windows of SECONDS duration.",
    )
    grp.add_argument(
        "--window-summary",
        action="store_true",
        default=False,
        help="Emit only window headers (start/end/count), not the lines.",
    )


def apply_windowing(
    args: argparse.Namespace,
    lines: List[str],
    out,
) -> List[str]:
    """Apply windowing if --window is set; return (possibly unchanged) lines."""
    if not args.window:
        return lines

    collected: List[str] = []
    for win in tumbling_windows(lines, args.window):
        header = (
            f"[window {win.start} -> {win.end}  lines={len(win)}]\n"
        )
        out.write(header)
        if not args.window_summary:
            for ln in win.lines:
                out.write(ln if ln.endswith("\n") else ln + "\n")
                collected.append(ln)
    # When summary-only, return empty list (output already written)
    return [] if args.window_summary else collected
