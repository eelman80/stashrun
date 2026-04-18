"""Snapshot status tracking: active, paused, deprecated, etc."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_STATUSES = {"active", "paused", "deprecated", "archived", "draft"}
DEFAULT_STATUS = "active"


def _status_path() -> Path:
    return get_stash_dir() / "statuses.json"


def _load_statuses() -> dict:
    p = _status_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_statuses(data: dict) -> None:
    _status_path().write_text(json.dumps(data, indent=2))


def set_status(name: str, status: str) -> bool:
    """Set the status for a snapshot. Returns False if status is invalid."""
    if status not in VALID_STATUSES:
        return False
    data = _load_statuses()
    data[name] = status
    _save_statuses(data)
    return True


def get_status(name: str, default: str = DEFAULT_STATUS) -> str:
    """Get the status of a snapshot, returning default if not set."""
    return _load_statuses().get(name, default)


def remove_status(name: str) -> bool:
    """Remove status entry for a snapshot. Returns False if not found."""
    data = _load_statuses()
    if name not in data:
        return False
    del data[name]
    _save_statuses(data)
    return True


def list_statuses() -> dict:
    """Return all snapshot name -> status mappings."""
    return _load_statuses()


def find_by_status(status: str) -> list:
    """Return list of snapshot names with the given status."""
    return [name for name, s in _load_statuses().items() if s == status]
