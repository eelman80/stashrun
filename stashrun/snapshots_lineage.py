"""Track parent-child lineage relationships between snapshots."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _lineage_path() -> Path:
    return get_stash_dir() / "lineage.json"


def _load_lineage() -> dict:
    p = _lineage_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_lineage(data: dict) -> None:
    _lineage_path().write_text(json.dumps(data, indent=2))


def set_parent(name: str, parent: str) -> bool:
    """Set the parent of a snapshot. Returns False if self-reference."""
    if name == parent:
        return False
    data = _load_lineage()
    entry = data.get(name, {})
    entry["parent"] = parent
    data[name] = entry
    _save_lineage(data)
    return True


def get_parent(name: str) -> str | None:
    data = _load_lineage()
    return data.get(name, {}).get("parent")


def get_children(name: str) -> list[str]:
    data = _load_lineage()
    return [k for k, v in data.items() if v.get("parent") == name]


def remove_lineage(name: str) -> bool:
    data = _load_lineage()
    if name not in data:
        return False
    del data[name]
    _save_lineage(data)
    return True


def get_ancestors(name: str) -> list[str]:
    """Return ordered list of ancestors from immediate parent to root."""
    data = _load_lineage()
    ancestors = []
    visited = set()
    current = data.get(name, {}).get("parent")
    while current and current not in visited:
        ancestors.append(current)
        visited.add(current)
        current = data.get(current, {}).get("parent")
    return ancestors


def lineage_summary() -> dict:
    data = _load_lineage()
    return {
        name: {
            "parent": entry.get("parent"),
            "children": get_children(name),
        }
        for name, entry in data.items()
    }
