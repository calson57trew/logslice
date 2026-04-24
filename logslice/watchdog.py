"""watchdog.py – tail and watch a log file, emitting new lines as they arrive."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Generator, Iterable, Optional


def tail_lines(
    path: str | Path,
    poll_interval: float = 0.25,
    max_iterations: Optional[int] = None,
) -> Generator[str, None, None]:
    """Yield new lines appended to *path* as they arrive.

    Reads the file from the current end and yields each new line.
    Intended for use in a pipeline; caller is responsible for stopping
    iteration (e.g. via ``max_iterations`` in tests or a signal handler).
    """
    path = Path(path)
    with path.open("r", errors="replace") as fh:
        fh.seek(0, 2)  # seek to end
        iterations = 0
        while True:
            line = fh.readline()
            if line:
                yield line
            else:
                if max_iterations is not None:
                    iterations += 1
                    if iterations >= max_iterations:
                        return
                time.sleep(poll_interval)


def watch_lines(
    lines: Iterable[str],
    predicate: Callable[[str], bool],
    on_match: Callable[[str], None],
) -> list[str]:
    """Pass *lines* through, calling *on_match* for every line that satisfies
    *predicate*.  Returns all lines unchanged (pass-through semantics)."""
    result: list[str] = []
    for line in lines:
        result.append(line)
        if predicate(line):
            on_match(line)
    return result


def count_watched(lines: Iterable[str], predicate: Callable[[str], bool]) -> int:
    """Return the number of lines in *lines* that satisfy *predicate*."""
    return sum(1 for ln in lines if predicate(ln))
