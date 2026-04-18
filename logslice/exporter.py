"""Export sliced log lines to various file formats (plain, JSON, CSV)."""

import csv
import io
import json
from typing import Iterable, Iterator, List

from logslice.parser import extract_timestamp


SUPPORTED_FORMATS = ("plain", "json", "csv")


def export_plain(lines: Iterable[str]) -> Iterator[str]:
    """Yield lines unchanged."""
    for line in lines:
        yield line if line.endswith("\n") else line + "\n"


def export_json(lines: Iterable[str]) -> Iterator[str]:
    """Yield each log line as a JSON object with timestamp and message fields."""
    for line in lines:
        raw = line.rstrip("\n")
        ts = extract_timestamp(raw)
        obj = {"timestamp": ts.isoformat() if ts else None, "message": raw}
        yield json.dumps(obj) + "\n"


def export_csv(lines: Iterable[str]) -> Iterator[str]:
    """Yield CSV rows: timestamp, message. First row is a header."""
    buf = io.StringIO()
    writer = csv.writer(buf)

    writer.writerow(["timestamp", "message"])
    buf.seek(0)
    yield buf.read()

    for line in lines:
        raw = line.rstrip("\n")
        ts = extract_timestamp(raw)
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([ts.isoformat() if ts else "", raw])
        buf.seek(0)
        yield buf.read()


def get_exporter(fmt: str):
    """Return the export function for the given format name."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt!r}. Choose from {SUPPORTED_FORMATS}.")
    return {"plain": export_plain, "json": export_json, "csv": export_csv}[fmt]


def export_lines(lines: Iterable[str], fmt: str) -> List[str]:
    """Materialise exported lines into a list."""
    return list(get_exporter(fmt)(lines))
