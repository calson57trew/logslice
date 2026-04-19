"""CLI integration for bookmark commands."""

import argparse
from typing import List

from logslice.bookmarker import (
    DEFAULT_BOOKMARK_FILE,
    delete_bookmark,
    get_bookmark,
    list_bookmarks,
    set_bookmark,
)


def add_bookmark_args(parser: argparse.ArgumentParser) -> None:
    """Register bookmark-related flags on an argument parser."""
    grp = parser.add_argument_group("bookmarks")
    grp.add_argument("--bookmark-save", metavar="NAME",
                     help="Save current position as a named bookmark")
    grp.add_argument("--bookmark-load", metavar="NAME",
                     help="Resume from a named bookmark (sets --start)")
    grp.add_argument("--bookmark-delete", metavar="NAME",
                     help="Delete a named bookmark and exit")
    grp.add_argument("--bookmark-list", action="store_true",
                     help="List all saved bookmarks and exit")
    grp.add_argument("--bookmark-file", default=DEFAULT_BOOKMARK_FILE,
                     metavar="PATH", help="Path to bookmark storage file")


def apply_bookmark_pre(args: argparse.Namespace) -> bool:
    """Handle list/delete actions before main processing.

    Returns True if the caller should exit early.
    """
    bf = args.bookmark_file

    if args.bookmark_list:
        bms = list_bookmarks(bf)
        if not bms:
            print("No bookmarks saved.")
        for bm in bms:
            ts = bm.timestamp or "-"
            src = bm.source or "-"
            print(f"{bm.name:20s}  ts={ts}  line={bm.line_number}  src={src}")
        return True

    if args.bookmark_delete:
        removed = delete_bookmark(args.bookmark_delete, bf)
        print("Deleted." if removed else "Bookmark not found.")
        return True

    if args.bookmark_load:
        bm = get_bookmark(args.bookmark_load, bf)
        if bm is None:
            raise SystemExit(f"Bookmark '{args.bookmark_load}' not found.")
        if bm.timestamp and not getattr(args, "start", None):
            args.start = bm.timestamp

    return False


def apply_bookmark_post(args: argparse.Namespace, lines: List[str]) -> List[str]:
    """After slicing, save bookmark if requested. Returns lines unchanged."""
    if args.bookmark_save and lines:
        from logslice.parser import extract_timestamp
        last_ts = None
        for line in reversed(lines):
            ts = extract_timestamp(line)
            if ts:
                last_ts = ts.isoformat()
                break
        set_bookmark(
            args.bookmark_save,
            timestamp=last_ts,
            line_number=len(lines),
            source=getattr(args, "file", None),
            path=args.bookmark_file,
        )
    return lines
