"""Priority levels for snapshots."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_PRIORITIES = {"low", "normal", "high", "critical"}
DEFAULT_PRIORITY = "normal"


def _priority_path() -> Path:
    return get_stash_dir() / "priorities.json"


def _load_priorities() -> dict:
    p = _priority_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(data: dict) -> None:
    _priority_path().write_text(json.dumps(data, indent=2))


def set_priority(name: str, level: str) -> bool:
    """Set priority level for a snapshot. Returns False if level is invalid."""
    if level not in VALID_PRIORITIES:
        return False
    data = _load_priorities()
    data[name] = level
    _save_priorities(data)
    return True


def get_priority(name: str, default: str = DEFAULT_PRIORITY) -> str:
    """Get priority level for a snapshot."""
    data = _load_priorities()
    return data.get(name, default)


def remove_priority(name: str) -> bool:
    """Remove priority entry. Returns False if not found."""
    data = _load_priorities()
    if name not in data:
        return False
    del data[name]
    _save_priorities(data)
    return True


def list_by_priority(level: str) -> list[str]:
    """Return all snapshot names with the given priority level."""
    data = _load_priorities()
    return [name for name, lvl in data.items() if lvl == level]


def all_priorities() -> dict:
    """Return the full priority mapping."""
    return _load_priorities()
