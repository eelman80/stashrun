"""Track snapshot access and modification history."""

import json
import time
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

_HISTORY_FILE = "history.json"
_MAX_ENTRIES = 200


def _history_path() -> Path:
    return get_stash_dir() / _HISTORY_FILE


def _load_history() -> list:
    path = _history_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_history(entries: list) -> None:
    path = _history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2))


def record_event(snapshot_name: str, action: str, detail: Optional[str] = None) -> None:
    """Append an event entry for a snapshot action (save, restore, delete, export)."""
    entries = _load_history()
    entry = {
        "timestamp": time.time(),
        "snapshot": snapshot_name,
        "action": action,
    }
    if detail:
        entry["detail"] = detail
    entries.append(entry)
    # Trim to max entries
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    _save_history(entries)


def get_history(snapshot_name: Optional[str] = None) -> list:
    """Return history entries, optionally filtered by snapshot name."""
    entries = _load_history()
    if snapshot_name is not None:
        entries = [e for e in entries if e.get("snapshot") == snapshot_name]
    return entries


def clear_history(snapshot_name: Optional[str] = None) -> int:
    """Clear history entries. Returns number of entries removed."""
    entries = _load_history()
    if snapshot_name is None:
        count = len(entries)
        _save_history([])
        return count
    kept = [e for e in entries if e.get("snapshot") != snapshot_name]
    removed = len(entries) - len(kept)
    _save_history(kept)
    return removed
