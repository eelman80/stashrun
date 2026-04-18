"""Reminders: attach reminder messages with due dates to snapshots."""

import json
import time
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _reminders_path() -> Path:
    return get_stash_dir() / "reminders.json"


def _load_reminders() -> dict:
    p = _reminders_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_reminders(data: dict) -> None:
    _reminders_path().write_text(json.dumps(data, indent=2))


def set_reminder(name: str, message: str, due_ts: Optional[float] = None) -> None:
    """Set a reminder for a snapshot."""
    data = _load_reminders()
    data[name] = {"message": message, "due_ts": due_ts}
    _save_reminders(data)


def get_reminder(name: str) -> Optional[dict]:
    """Return the reminder dict for a snapshot, or None."""
    return _load_reminders().get(name)


def remove_reminder(name: str) -> bool:
    """Remove a reminder. Returns True if it existed."""
    data = _load_reminders()
    if name not in data:
        return False
    del data[name]
    _save_reminders(data)
    return True


def list_reminders() -> dict:
    """Return all reminders."""
    return _load_reminders()


def due_reminders() -> list:
    """Return list of (name, reminder) tuples whose due_ts has passed."""
    now = time.time()
    result = []
    for name, rem in _load_reminders().items():
        due = rem.get("due_ts")
        if due is not None and due <= now:
            result.append((name, rem))
    return result
