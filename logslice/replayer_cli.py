"""CLI integration for the replayer module."""

import argparse
from typing import List


def add_replay_args(parser: argparse.ArgumentParser) -> None:
    """Register replay-related flags onto *parser*."""
    group = parser.add_argument_group("replay")
    group.add_argument(
        "--replay",
        action="store_true",
        default=False,
        help="Replay lines with timing delays.",
    )
    group.add_argument(
        "--replay-mode",
        choices=["realtime", "fixed"],
        default="fixed",
        help="'realtime' uses timestamp gaps; 'fixed' uses a constant delay (default: fixed).",
    )
    group.add_argument(
        "--replay-speed",
        type=float,
        default=1.0,
        metavar="FACTOR",
        help="Speed multiplier for realtime mode (default: 1.0).",
    )
    group.add_argument(
        "--replay-delay",
        type=float,
        default=0.05,
        metavar="SECS",
        help="Fixed delay in seconds between lines (default: 0.05).",
    )
    group.add_argument(
        "--replay-max-gap",
        type=float,
        default=None,
        metavar="SECS",
        help="Cap on a single sleep in realtime mode.",
    )


def apply_replay(args: argparse.Namespace, lines: List[str]) -> List[str]:
    """Apply replay delays and return lines unchanged.

    The side-effect is the timing; the content is passed through.
    """
    if not getattr(args, "replay", False):
        return lines

    from logslice.replayer import replay_realtime, replay_fixed

    if args.replay_mode == "realtime":
        replayed = replay_realtime(
            lines,
            speed=args.replay_speed,
            max_gap=args.replay_max_gap,
        )
    else:
        replayed = replay_fixed(lines, delay=args.replay_delay)

    return list(replayed)
