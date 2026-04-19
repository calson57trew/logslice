"""Named aliases for common filter/slice argument sets."""
from __future__ import annotations

import json
import os
from typing import Dict, List

DEFAULT_ALIAS_FILE = os.path.expanduser("~/.logslice_aliases.json")


def load_aliases(path: str = DEFAULT_ALIAS_FILE) -> Dict[str, List[str]]:
    """Load aliases from a JSON file. Returns empty dict if file missing."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Alias file must contain a JSON object, got {type(data).__name__}")
    return {k: list(v) for k, v in data.items()}


def save_aliases(aliases: Dict[str, List[str]], path: str = DEFAULT_ALIAS_FILE) -> None:
    """Persist aliases to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(aliases, fh, indent=2)


def set_alias(name: str, args: List[str], path: str = DEFAULT_ALIAS_FILE) -> None:
    """Create or overwrite a named alias."""
    if not name:
        raise ValueError("Alias name must not be empty")
    aliases = load_aliases(path)
    aliases[name] = list(args)
    save_aliases(aliases, path)


def get_alias(name: str, path: str = DEFAULT_ALIAS_FILE) -> List[str]:
    """Return args for a named alias. Raises KeyError if not found."""
    aliases = load_aliases(path)
    if name not in aliases:
        raise KeyError(f"Alias '{name}' not found")
    return aliases[name]


def delete_alias(name: str, path: str = DEFAULT_ALIAS_FILE) -> None:
    """Remove a named alias. Raises KeyError if not found."""
    aliases = load_aliases(path)
    if name not in aliases:
        raise KeyError(f"Alias '{name}' not found")
    del aliases[name]
    save_aliases(aliases, path)


def list_aliases(path: str = DEFAULT_ALIAS_FILE) -> Dict[str, List[str]]:
    """Return all stored aliases."""
    return load_aliases(path)
