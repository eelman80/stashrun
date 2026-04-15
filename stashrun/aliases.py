"""Alias management for snapshots — map short names to snapshot IDs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _aliases_path() -> Path:
    return get_stash_dir() / "aliases.json"


def _load_aliases() -> dict[str, str]:
    path = _aliases_path()
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_aliases(aliases: dict[str, str]) -> None:
    _aliases_path().write_text(json.dumps(aliases, indent=2))


def set_alias(alias: str, snapshot_name: str) -> bool:
    """Create or overwrite an alias pointing to snapshot_name. Returns True."""
    aliases = _load_aliases()
    aliases[alias] = snapshot_name
    _save_aliases(aliases)
    return True


def remove_alias(alias: str) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases()
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(aliases)
    return True


def resolve_alias(alias: str) -> Optional[str]:
    """Return the snapshot name for the given alias, or None if not found."""
    return _load_aliases().get(alias)


def list_aliases() -> dict[str, str]:
    """Return all alias -> snapshot_name mappings."""
    return _load_aliases()


def rename_alias(old: str, new: str) -> bool:
    """Rename an alias key. Returns False if old does not exist."""
    aliases = _load_aliases()
    if old not in aliases:
        return False
    aliases[new] = aliases.pop(old)
    _save_aliases(aliases)
    return True
