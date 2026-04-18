"""Mention tracking: link snapshots to free-text references (ticket IDs, URLs, etc.)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _mentions_path() -> Path:
    return get_stash_dir() / "mentions.json"


def _load_mentions() -> dict:
    p = _mentions_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_mentions(data: dict) -> None:
    _mentions_path().write_text(json.dumps(data, indent=2))


def add_mention(name: str, reference: str) -> bool:
    """Add a reference mention to a snapshot. Returns False if already present."""
    data = _load_mentions()
    refs = data.setdefault(name, [])
    if reference in refs:
        return False
    refs.append(reference)
    _save_mentions(data)
    return True


def remove_mention(name: str, reference: str) -> bool:
    """Remove a reference from a snapshot. Returns False if not found."""
    data = _load_mentions()
    refs = data.get(name, [])
    if reference not in refs:
        return False
    refs.remove(reference)
    if not refs:
        del data[name]
    else:
        data[name] = refs
    _save_mentions(data)
    return True


def get_mentions(name: str) -> list:
    """Return all references for a snapshot."""
    return _load_mentions().get(name, [])


def clear_mentions(name: str) -> bool:
    """Remove all mentions for a snapshot. Returns False if none existed."""
    data = _load_mentions()
    if name not in data:
        return False
    del data[name]
    _save_mentions(data)
    return True


def find_by_mention(reference: str) -> list:
    """Return snapshot names that contain the given reference."""
    data = _load_mentions()
    return [name for name, refs in data.items() if reference in refs]
