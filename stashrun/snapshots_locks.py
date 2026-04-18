"""Snapshot-level locking: mark snapshots as locked to prevent modification."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _locks_path() -> Path:
    return get_stash_dir() / "snapshot_locks.json"


def _load_locks() -> dict:
    p = _locks_path()
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_locks(data: dict) -> None:
    with open(_locks_path(), "w") as f:
        json.dump(data, f, indent=2)


def lock_snapshot(name: str, reason: str = "") -> bool:
    """Lock a snapshot. Returns False if already locked."""
    data = _load_locks()
    if name in data:
        return False
    data[name] = {"reason": reason}
    _save_locks(data)
    return True


def unlock_snapshot(name: str) -> bool:
    """Unlock a snapshot. Returns False if not locked."""
    data = _load_locks()
    if name not in data:
        return False
    del data[name]
    _save_locks(data)
    return True


def is_snapshot_locked(name: str) -> bool:
    return name in _load_locks()


def get_lock_info(name: str) -> dict | None:
    return _load_locks().get(name)


def list_locked() -> list[str]:
    return list(_load_locks().keys())


def clear_all_locks() -> int:
    data = _load_locks()
    count = len(data)
    _save_locks({})
    return count
