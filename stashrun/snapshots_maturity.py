"""Track maturity level of snapshots (draft, stable, deprecated)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_LEVELS = {"draft", "stable", "deprecated"}
DEFAULT_LEVEL = "draft"


def _maturity_path() -> Path:
    return get_stash_dir() / "maturity.json"


def _load_maturity() -> dict:
    p = _maturity_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_maturity(data: dict) -> None:
    _maturity_path().write_text(json.dumps(data, indent=2))


def set_maturity(name: str, level: str) -> bool:
    """Set the maturity level for a snapshot.

    Returns False if the level is not one of the valid levels.
    """
    if level not in VALID_LEVELS:
        return False
    data = _load_maturity()
    data[name] = level
    _save_maturity(data)
    return True


def get_maturity(name: str, default: str = DEFAULT_LEVEL) -> str:
    """Return the maturity level for a snapshot, or *default* if not set."""
    return _load_maturity().get(name, default)


def remove_maturity(name: str) -> bool:
    """Remove the maturity entry for a snapshot.

    Returns False if the snapshot had no maturity entry.
    """
    data = _load_maturity()
    if name not in data:
        return False
    del data[name]
    _save_maturity(data)
    return True


def list_maturity() -> dict:
    """Return all snapshot-to-level mappings."""
    return _load_maturity()


def find_by_maturity(level: str) -> list:
    """Return all snapshot names that have the given maturity level."""
    return [name for name, lvl in _load_maturity().items() if lvl == level]


def promote(name: str) -> bool:
    """Advance a snapshot to the next maturity level.

    Progression order: draft -> stable -> deprecated.
    Returns False if the snapshot is already at the final level
    or has no recorded maturity entry.
    """
    ordered = ["draft", "stable", "deprecated"]
    current = _load_maturity().get(name)
    if current is None or current == ordered[-1]:
        return False
    next_level = ordered[ordered.index(current) + 1]
    return set_maturity(name, next_level)
