"""Spotlight feature: mark snapshots as featured/highlighted."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _spotlight_path() -> Path:
    return get_stash_dir() / "spotlight.json"


def _load_spotlight() -> dict:
    p = _spotlight_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_spotlight(data: dict) -> None:
    _spotlight_path().write_text(json.dumps(data, indent=2))


def spotlight_snapshot(name: str, reason: str = "") -> bool:
    """Mark a snapshot as spotlighted. Returns True if newly added."""
    data = _load_spotlight()
    already = name in data
    data[name] = {"reason": reason}
    _save_spotlight(data)
    return not already


def remove_spotlight(name: str) -> bool:
    """Remove spotlight from a snapshot. Returns True if it existed."""
    data = _load_spotlight()
    if name not in data:
        return False
    del data[name]
    _save_spotlight(data)
    return True


def get_spotlight(name: str) -> Optional[dict]:
    """Return spotlight entry for a snapshot, or None."""
    return _load_spotlight().get(name)


def list_spotlighted() -> list[str]:
    """Return all spotlighted snapshot names."""
    return list(_load_spotlight().keys())


def is_spotlighted(name: str) -> bool:
    return name in _load_spotlight()


def clear_spotlight() -> int:
    """Remove all spotlight entries. Returns count removed."""
    data = _load_spotlight()
    count = len(data)
    _save_spotlight({})
    return count
