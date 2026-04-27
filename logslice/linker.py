"""linker.py — correlate log lines across a session by linking cause-and-effect chains.

Given a 'trigger' pattern and a 'follow' pattern, linker groups lines where
a trigger line is followed (within a configurable lookahead window) by one or
more follow lines, emitting linked chains for downstream inspection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Pattern

from logslice.parser import extract_timestamp


@dataclass
class LinkedChain:
    """A trigger line paired with the follow lines that responded to it."""

    trigger: str
    follows: List[str] = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return 1 + len(self.follows)

    def lines(self) -> List[str]:
        """Return all lines in the chain, trigger first."""
        return [self.trigger] + self.follows


def compile_pattern(pattern: str, ignore_case: bool = False) -> Pattern[str]:
    """Compile *pattern* to a regex, optionally case-insensitive."""
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def link_lines(
    lines: Iterable[str],
    trigger_pattern: str,
    follow_pattern: str,
    lookahead: int = 50,
    ignore_case: bool = False,
) -> Iterator[LinkedChain]:
    """Yield :class:`LinkedChain` objects found in *lines*.

    For every line matching *trigger_pattern*, the next *lookahead* lines are
    scanned for matches against *follow_pattern*.  All matching follow lines
    are collected into the chain.  A follow line may only belong to the
    nearest preceding trigger (first-match wins).

    Args:
        lines: Iterable of raw log lines.
        trigger_pattern: Regex that marks the start of a chain.
        follow_pattern: Regex that marks a line linked to the trigger.
        lookahead: Maximum number of lines after the trigger to scan.
        ignore_case: Whether pattern matching is case-insensitive.
    """
    if lookahead < 1:
        raise ValueError(f"lookahead must be >= 1, got {lookahead}")

    t_re = compile_pattern(trigger_pattern, ignore_case)
    f_re = compile_pattern(follow_pattern, ignore_case)

    buf: List[str] = list(lines)
    used: set[int] = set()  # indices already claimed as follow lines

    for i, line in enumerate(buf):
        if t_re.search(line):
            chain = LinkedChain(trigger=line)
            end = min(i + 1 + lookahead, len(buf))
            for j in range(i + 1, end):
                if j not in used and f_re.search(buf[j]):
                    chain.follows.append(buf[j])
                    used.add(j)
            yield chain


def count_linked(chains: Iterable[LinkedChain]) -> dict:
    """Return summary counts over a collection of chains.

    Returns a dict with keys:
        ``chains``   — total number of chains
        ``triggers`` — same as chains (one trigger per chain)
        ``follows``  — total follow lines across all chains
        ``total``    — triggers + follows
    """
    n_chains = 0
    n_follows = 0
    for chain in chains:
        n_chains += 1
        n_follows += len(chain.follows)
    return {
        "chains": n_chains,
        "triggers": n_chains,
        "follows": n_follows,
        "total": n_chains + n_follows,
    }


def format_chain(chain: LinkedChain, indent: str = "  ") -> str:
    """Render a single :class:`LinkedChain` as a human-readable block.

    The trigger line is emitted first (stripped of trailing newline), then
    each follow line is indented by *indent*.
    """
    parts = [chain.trigger.rstrip("\n")]
    for follow in chain.follows:
        parts.append(f"{indent}{follow.rstrip(chr(10))}")
    return "\n".join(parts)
