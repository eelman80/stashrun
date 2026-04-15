"""Scheduling support: store named schedules that map a cron expression to a snapshot name."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

_SCHEDULES_FILE = "schedules.json"


def _schedules_path() -> Path:
    return get_stash_dir() / _SCHEDULES_FILE


def _load_schedules() -> dict:
    path = _schedules_path()
    if not path.exists():
        return {}
    with path.open("r") as fh:
        return json.load(fh)


def _save_schedules(data: dict) -> None:
    path = _schedules_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def set_schedule(schedule_name: str, snapshot_name: str, cron: str) -> dict:
    """Create or update a named schedule."""
    data = _load_schedules()
    entry = {"snapshot": snapshot_name, "cron": cron}
    data[schedule_name] = entry
    _save_schedules(data)
    return entry


def remove_schedule(schedule_name: str) -> bool:
    """Remove a named schedule. Returns True if it existed."""
    data = _load_schedules()
    if schedule_name not in data:
        return False
    del data[schedule_name]
    _save_schedules(data)
    return True


def get_schedule(schedule_name: str) -> Optional[dict]:
    """Return schedule entry or None if not found."""
    return _load_schedules().get(schedule_name)


def list_schedules() -> dict:
    """Return all schedules as a dict keyed by schedule name."""
    return _load_schedules()


def find_schedules_for_snapshot(snapshot_name: str) -> list[str]:
    """Return schedule names that reference the given snapshot."""
    data = _load_schedules()
    return [name for name, entry in data.items() if entry.get("snapshot") == snapshot_name]
