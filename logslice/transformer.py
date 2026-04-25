"""Line-level text transformation: uppercase, lowercase, strip, replace."""

from __future__ import annotations

import re
from typing import Callable, Iterable, Iterator, List, Tuple

# A transform is a callable that accepts a line and returns a transformed line.
TransformFn = Callable[[str], str]


def _make_replace(pattern: str, replacement: str, ignore_case: bool) -> TransformFn:
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)

    def _replace(line: str) -> str:
        return compiled.sub(replacement, line)

    return _replace


def compile_transforms(
    ops: List[Tuple[str, ...]],
    ignore_case: bool = False,
) -> List[TransformFn]:
    """Build a list of transform functions from (op, *args) tuples.

    Supported ops: 'upper', 'lower', 'strip', 'replace'.
    'replace' expects two extra args: pattern and replacement.
    """
    fns: List[TransformFn] = []
    for op_tuple in ops:
        op = op_tuple[0].lower()
        if op == "upper":
            fns.append(str.upper)
        elif op == "lower":
            fns.append(str.lower)
        elif op == "strip":
            fns.append(str.strip)
        elif op == "replace":
            if len(op_tuple) < 3:
                raise ValueError("'replace' transform requires pattern and replacement")
            fns.append(_make_replace(op_tuple[1], op_tuple[2], ignore_case))
        else:
            raise ValueError(f"Unknown transform op: {op!r}")
    return fns


def transform_line(line: str, transforms: List[TransformFn]) -> str:
    """Apply each transform in order to *line*."""
    for fn in transforms:
        line = fn(line)
    return line


def transform_lines(
    lines: Iterable[str],
    transforms: List[TransformFn],
) -> Iterator[str]:
    """Yield each line after applying all transforms."""
    for line in lines:
        yield transform_line(line, transforms)


def count_transformed(original: List[str], result: List[str]) -> int:
    """Return the number of lines that changed after transformation."""
    return sum(1 for a, b in zip(original, result) if a != b)
