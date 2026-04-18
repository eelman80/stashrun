"""Ownership tracking for snapshots."""

import json
import os
from pathlib import Path
from stashrun.storage import get_stash_dir


def _ownership_path() -> Path:
    return get_stash_dir() / "ownership.json"


def _load_ownership() -> dict:
    p = _ownership_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_ownership(data: dict) -> None:
    _ownership_path().write_text(json.dumps(data, indent=2))


def set_owner(name: str, owner: str) -> None:
    """Assign an owner to a snapshot."""
    data = _load_ownership()
    data[name] = {"owner": owner}
    _save_ownership(data)


def get_owner(name: str) -> str | None:
    """Return the owner of a snapshot, or None if unset."""
    return _load_ownership().get(name, {}).get("owner")


def remove_owner(name: str) -> bool:
    """Remove ownership record for a snapshot."""
    data = _load_ownership()
    if name in data:
        del data[name]
        _save_ownership(data)
        return True
    return False


def list_owned_by(owner: str) -> list[str]:
    """Return all snapshot names owned by the given owner."""
    data = _load_ownership()
    return [k for k, v in data.items() if v.get("owner") == owner]


def list_all_owners() -> dict[str, str]:
    """Return a mapping of snapshot name -> owner for all tracked snapshots."""
    data = _load_ownership()
    return {k: v["owner"] for k, v in data.items() if "owner" in v}
