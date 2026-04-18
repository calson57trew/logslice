"""Log line sampling: take every Nth line or a random fraction."""

from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_every_n(lines: Iterable[str], n: int) -> Iterator[str]:
    """Yield every Nth timestamped line (continuation lines follow their parent)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    from logslice.parser import extract_timestamp

    count = 0
    emit = False
    for line in lines:
        is_anchor = extract_timestamp(line) is not None
        if is_anchor:
            count += 1
            emit = (count % n == 0)
        if emit:
            yield line


def sample_random(lines: Iterable[str], rate: float, seed: int | None = None) -> Iterator[str]:
    """Yield each timestamped line (plus continuations) with probability *rate*."""
    if not 0.0 < rate <= 1.0:
        raise ValueError(f"rate must be in (0, 1], got {rate}")
    from logslice.parser import extract_timestamp

    rng = random.Random(seed)
    emit = False
    for line in lines:
        is_anchor = extract_timestamp(line) is not None
        if is_anchor:
            emit = rng.random() < rate
        if emit:
            yield line


def count_sampled(lines: Iterable[str]) -> dict[str, int]:
    """Return {'total': N, 'anchors': M} for a sequence of lines."""
    from logslice.parser import extract_timestamp

    total = 0
    anchors = 0
    for line in lines:
        total += 1
        if extract_timestamp(line) is not None:
            anchors += 1
    return {"total": total, "anchors": anchors}
