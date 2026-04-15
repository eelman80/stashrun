"""Tag management for snapshots — attach, remove, and query tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashrun.storage import get_stash_dir

TAGS_FILE = "tags.json"


def _tags_path() -> Path:
    return get_stash_dir() / TAGS_FILE


def _load_tags() -> Dict[str, List[str]]:
    """Load the tags index from disk. Returns {snapshot_name: [tag, ...]}."""
    path = _tags_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_tags(data: Dict[str, List[str]]) -> None:
    path = _tags_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def add_tag(snapshot_name: str, tag: str) -> bool:
    """Add *tag* to *snapshot_name*. Returns True if tag was newly added."""
    data = _load_tags()
    tags = data.setdefault(snapshot_name, [])
    if tag in tags:
        return False
    tags.append(tag)
    _save_tags(data)
    return True


def remove_tag(snapshot_name: str, tag: str) -> bool:
    """Remove *tag* from *snapshot_name*. Returns True if tag existed."""
    data = _load_tags()
    tags = data.get(snapshot_name, [])
    if tag not in tags:
        return False
    tags.remove(tag)
    if not tags:
        del data[snapshot_name]
    else:
        data[snapshot_name] = tags
    _save_tags(data)
    return True


def get_tags(snapshot_name: str) -> List[str]:
    """Return all tags for *snapshot_name*."""
    return list(_load_tags().get(snapshot_name, []))


def find_by_tag(tag: str) -> List[str]:
    """Return all snapshot names that carry *tag*."""
    return [name for name, tags in _load_tags().items() if tag in tags]


def remove_snapshot_tags(snapshot_name: str) -> None:
    """Remove all tag entries for a deleted snapshot."""
    data = _load_tags()
    if snapshot_name in data:
        del data[snapshot_name]
        _save_tags(data)


def all_tags() -> Dict[str, List[str]]:
    """Return the full tags index."""
    return _load_tags()
