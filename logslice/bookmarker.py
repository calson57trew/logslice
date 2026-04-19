"""Bookmark support: save and restore log positions by name."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

DEFAULT_BOOKMARK_FILE = os.path.expanduser("~/.logslice_bookmarks.json")


@dataclass
class Bookmark:
    name: str
    timestamp: Optional[str] = None
    line_number: int = 0
    source: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


def load_bookmarks(path: str = DEFAULT_BOOKMARK_FILE) -> Dict[str, Bookmark]:
    """Load bookmarks from a JSON file. Returns empty dict if file missing."""
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        raw = json.load(fh)
    return {name: Bookmark(**data) for name, data in raw.items()}


def save_bookmarks(bookmarks: Dict[str, Bookmark], path: str = DEFAULT_BOOKMARK_FILE) -> None:
    """Persist bookmarks to a JSON file."""
    with open(path, "w") as fh:
        json.dump({name: vars(bm) for name, bm in bookmarks.items()}, fh, indent=2)


def set_bookmark(name: str, timestamp: Optional[str] = None,
                line_number: int = 0, source: Optional[str] = None,
                path: str = DEFAULT_BOOKMARK_FILE) -> Bookmark:
    """Create or update a named bookmark."""
    bookmarks = load_bookmarks(path)
    bm = Bookmark(name=name, timestamp=timestamp, line_number=line_number, source=source)
    bookmarks[name] = bm
    save_bookmarks(bookmarks, path)
    return bm


def get_bookmark(name: str, path: str = DEFAULT_BOOKMARK_FILE) -> Optional[Bookmark]:
    """Retrieve a bookmark by name, or None if not found."""
    return load_bookmarks(path).get(name)


def delete_bookmark(name: str, path: str = DEFAULT_BOOKMARK_FILE) -> bool:
    """Remove a bookmark. Returns True if it existed."""
    bookmarks = load_bookmarks(path)
    if name not in bookmarks:
        return False
    del bookmarks[name]
    save_bookmarks(bookmarks, path)
    return True


def list_bookmarks(path: str = DEFAULT_BOOKMARK_FILE) -> list:
    """Return all bookmarks sorted by name."""
    return sorted(load_bookmarks(path).values(), key=lambda b: b.name)
