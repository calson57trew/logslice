"""Inspector: scan log lines and report structural metadata (fields, levels, timestamp formats)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from logslice.parser import extract_timestamp

_LEVEL_RE = re.compile(
    r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL|TRACE)\b", re.IGNORECASE
)
_KV_RE = re.compile(r"(\w[\w.\-]*)=[\"']?([^\"'\s,}]+)[\"']?")
_TS_ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
_TS_EPOCH = re.compile(r"(?<![\d.])\d{10}(?:\.\d+)?(?![\d])")


@dataclass
class InspectResult:
    total_lines: int = 0
    timed_lines: int = 0
    timestamp_formats: Dict[str, int] = field(default_factory=dict)
    level_counts: Dict[str, int] = field(default_factory=dict)
    field_names: Dict[str, int] = field(default_factory=dict)
    sample_lines: List[str] = field(default_factory=list)
    max_samples: int = 5


def _detect_ts_format(line: str) -> Optional[str]:
    if _TS_ISO.search(line):
        return "iso8601"
    if _TS_EPOCH.search(line):
        return "epoch"
    return None


def inspect_lines(lines: Iterable[str], max_samples: int = 5) -> InspectResult:
    result = InspectResult(max_samples=max_samples)
    for raw in lines:
        line = raw.rstrip("\n")
        result.total_lines += 1

        ts = extract_timestamp(line)
        if ts is not None:
            result.timed_lines += 1

        fmt = _detect_ts_format(line)
        if fmt:
            result.timestamp_formats[fmt] = result.timestamp_formats.get(fmt, 0) + 1

        m = _LEVEL_RE.search(line)
        if m:
            lvl = m.group(1).upper()
            if lvl == "WARNING":
                lvl = "WARN"
            result.level_counts[lvl] = result.level_counts.get(lvl, 0) + 1

        for kv in _KV_RE.finditer(line):
            key = kv.group(1)
            result.field_names[key] = result.field_names.get(key, 0) + 1

        if len(result.sample_lines) < max_samples:
            result.sample_lines.append(line)

    return result


def format_inspect(result: InspectResult) -> str:
    lines: List[str] = []
    lines.append(f"total_lines      : {result.total_lines}")
    lines.append(f"timed_lines      : {result.timed_lines}")
    if result.timestamp_formats:
        fmts = ", ".join(f"{k}({v})" for k, v in sorted(result.timestamp_formats.items()))
        lines.append(f"timestamp_formats: {fmts}")
    else:
        lines.append("timestamp_formats: none")
    if result.level_counts:
        lvls = ", ".join(f"{k}={v}" for k, v in sorted(result.level_counts.items()))
        lines.append(f"levels           : {lvls}")
    else:
        lines.append("levels           : none")
    if result.field_names:
        top = sorted(result.field_names.items(), key=lambda x: -x[1])[:10]
        flds = ", ".join(f"{k}({v})" for k, v in top)
        lines.append(f"kv_fields (top10): {flds}")
    else:
        lines.append("kv_fields        : none")
    return "\n".join(lines) + "\n"
