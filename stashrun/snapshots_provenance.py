"""Provenance tracking for snapshots — records origin, creation method, and source context."""

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _provenance_path() -> Path:
    return get_stash_dir() / "provenance.json"


def _load_provenance() -> dict:
    p = _provenance_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_provenance(data: dict) -> None:
    p = _provenance_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_provenance(
    name: str,
    origin: str,
    method: str = "manual",
    source_context: Optional[str] = None,
    created_by: Optional[str] = None,
) -> dict:
    """Record provenance for a snapshot. Returns the stored entry."""
    data = _load_provenance()
    entry = {
        "origin": origin,
        "method": method,
        "source_context": source_context,
        "created_by": created_by,
    }
    data[name] = entry
    _save_provenance(data)
    return entry


def get_provenance(name: str) -> Optional[dict]:
    """Return provenance entry for a snapshot, or None if not found."""
    return _load_provenance().get(name)


def remove_provenance(name: str) -> bool:
    """Remove provenance record for a snapshot. Returns True if removed."""
    data = _load_provenance()
    if name not in data:
        return False
    del data[name]
    _save_provenance(data)
    return True


def list_provenance() -> dict:
    """Return all provenance records."""
    return _load_provenance()


def find_by_origin(origin: str) -> list[str]:
    """Return snapshot names whose origin matches (case-insensitive substring)."""
    data = _load_provenance()
    origin_lower = origin.lower()
    return [
        name
        for name, entry in data.items()
        if origin_lower in entry.get("origin", "").lower()
    ]


def find_by_method(method: str) -> list[str]:
    """Return snapshot names created by the given method."""
    data = _load_provenance()
    return [
        name
        for name, entry in data.items()
        if entry.get("method") == method
    ]
