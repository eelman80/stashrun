"""Bookmark snapshots with short memorable names for quick access."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _bookmarks_path() -> Path:
    return get_stash_dir() / "bookmarks.json"


def _load_bookmarks() -> dict:
    p = _bookmarks_path()
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_bookmarks(data: dict) -> None:
    with open(_bookmarks_path(), "w") as f:
        json.dump(data, f, indent=2)


def set_bookmark(alias: str, snapshot_name: str) -> None:
    """Map a bookmark alias to a snapshot name."""
    data = _load_bookmarks()
    data[alias] = snapshot_name
    _save_bookmarks(data)


def remove_bookmark(alias: str) -> bool:
    data = _load_bookmarks()
    if alias not in data:
        return False
    del data[alias]
    _save_bookmarks(data)
    return True


def resolve_bookmark(alias: str) -> str | None:
    return _load_bookmarks().get(alias)


def list_bookmarks() -> dict:
    return _load_bookmarks()


def rename_bookmark(old: str, new: str) -> bool:
    data = _load_bookmarks()
    if old not in data:
        return False
    data[new] = data.pop(old)
    _save_bookmarks(data)
    return True
