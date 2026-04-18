"""Visibility control for snapshots (public/private/hidden)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_LEVELS = {"public", "private", "hidden"}


def _visibility_path() -> Path:
    return get_stash_dir() / "visibility.json"


def _load_visibility() -> dict:
    p = _visibility_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_visibility(data: dict) -> None:
    _visibility_path().write_text(json.dumps(data, indent=2))


def set_visibility(name: str, level: str) -> bool:
    """Set visibility level for a snapshot. Returns False if level is invalid."""
    if level not in VALID_LEVELS:
        return False
    data = _load_visibility()
    data[name] = level
    _save_visibility(data)
    return True


def get_visibility(name: str, default: str = "private") -> str:
    """Return visibility level for a snapshot, defaulting to 'private'."""
    return _load_visibility().get(name, default)


def remove_visibility(name: str) -> bool:
    """Remove explicit visibility setting. Returns False if not set."""
    data = _load_visibility()
    if name not in data:
        return False
    del data[name]
    _save_visibility(data)
    return True


def list_by_visibility(level: str) -> list[str]:
    """Return all snapshot names with the given visibility level."""
    return [name for name, lvl in _load_visibility().items() if lvl == level]


def is_visible(name: str, viewer_level: str = "public") -> bool:
    """Check if a snapshot is visible at the given viewer access level."""
    order = ["public", "private", "hidden"]
    snap_level = get_visibility(name)
    return order.index(snap_level) <= order.index(viewer_level)
