"""CLI integration for named aliases."""
from __future__ import annotations

import argparse
from typing import List, Optional

from logslice.aliaser import (
    DEFAULT_ALIAS_FILE,
    delete_alias,
    get_alias,
    list_aliases,
    set_alias,
)


def add_alias_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("aliases")
    grp.add_argument("--alias", metavar="NAME", help="Expand a saved alias before processing")
    grp.add_argument("--alias-set", nargs=2, metavar=("NAME", "ARGS"),
                     help="Save NAME as alias for quoted ARGS string")
    grp.add_argument("--alias-delete", metavar="NAME", help="Delete a saved alias")
    grp.add_argument("--alias-list", action="store_true", help="Print all saved aliases and exit")
    grp.add_argument("--alias-file", default=DEFAULT_ALIAS_FILE,
                     metavar="PATH", help="Path to alias storage file")


def apply_alias_pre(args: argparse.Namespace, argv: List[str]) -> List[str]:
    """Handle alias management flags; expand --alias into argv.

    Returns potentially modified argv (with alias args prepended).
    Exits or raises for management operations.
    """
    path = args.alias_file

    if args.alias_list:
        aliases = list_aliases(path)
        if not aliases:
            print("No aliases defined.")
        else:
            for name, saved_args in sorted(aliases.items()):
                print(f"{name}: {' '.join(saved_args)}")
        raise SystemExit(0)

    if args.alias_set:
        name, raw_args = args.alias_set
        expanded = raw_args.split()
        set_alias(name, expanded, path)
        print(f"Alias '{name}' saved.")
        raise SystemExit(0)

    if args.alias_delete:
        delete_alias(args.alias_delete, path)
        print(f"Alias '{args.alias_delete}' deleted.")
        raise SystemExit(0)

    if args.alias:
        extra = get_alias(args.alias, path)
        return extra + argv

    return argv
