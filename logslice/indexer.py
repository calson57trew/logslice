"""Build and query a simple byte-offset index over a log file.

The index maps each line's timestamp (as an ISO-8601 string) to its byte
offset in the source file, enabling fast random-access slicing without
scanning the entire file from the start.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from logslice.parser import extract_timestamp


@dataclass
class IndexEntry:
    timestamp: Optional[str]
    offset: int
    line_number: int


@dataclass
class LogIndex:
    entries: List[IndexEntry] = field(default_factory=list)

    def __len__(self) -> int:  # noqa: D105
        return len(self.entries)

    def timed_entries(self) -> List[IndexEntry]:
        """Return only entries that carry a timestamp."""
        return [e for e in self.entries if e.timestamp is not None]


def build_index(path: str) -> LogIndex:
    """Scan *path* and record the byte offset of every line."""
    index = LogIndex()
    with open(path, "rb") as fh:
        line_number = 0
        while True:
            offset = fh.tell()
            raw = fh.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace")
            ts = extract_timestamp(line)
            index.entries.append(IndexEntry(timestamp=ts, offset=offset, line_number=line_number))
            line_number += 1
    return index


def save_index(index: LogIndex, path: str) -> None:
    """Persist *index* to a JSON file at *path*."""
    data = [
        {"timestamp": e.timestamp, "offset": e.offset, "line_number": e.line_number}
        for e in index.entries
    ]
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_index(path: str) -> LogIndex:
    """Load a previously saved index from *path*."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Index file must contain a JSON array")
    entries = [
        IndexEntry(
            timestamp=item.get("timestamp"),
            offset=int(item["offset"]),
            line_number=int(item["line_number"]),
        )
        for item in raw
    ]
    return LogIndex(entries=entries)


def seek_to_timestamp(index: LogIndex, timestamp: str) -> Optional[int]:
    """Return the byte offset of the first entry whose timestamp >= *timestamp*."""
    for entry in index.timed_entries():
        if entry.timestamp >= timestamp:  # type: ignore[operator]
            return entry.offset
    return None


def count_indexed(index: LogIndex) -> Dict[str, int]:
    """Return summary counts for the index."""
    timed = index.timed_entries()
    return {
        "total": len(index),
        "timed": len(timed),
        "untimed": len(index) - len(timed),
    }
