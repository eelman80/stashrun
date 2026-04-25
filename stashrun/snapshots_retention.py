"""Retention policy management for snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashrun.storage import get_stash_dir, list_snapshots
from stashrun.history import get_history
from stashrun.snapshot import remove_snapshot

_VALID_POLICIES = {"keep_last", "keep_days", "keep_all"}


def _retention_path() -> Path:
    return get_stash_dir() / "retention.json"


def _load_retention() -> Dict:
    p = _retention_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_retention(data: Dict) -> None:
    _retention_path().write_text(json.dumps(data, indent=2))


def set_retention(name: str, policy: str, value: int = 0) -> bool:
    """Set a retention policy for a snapshot. Returns False if policy is invalid."""
    if policy not in _VALID_POLICIES:
        return False
    data = _load_retention()
    data[name] = {"policy": policy, "value": value}
    _save_retention(data)
    return True


def get_retention(name: str) -> Optional[Dict]:
    """Return the retention policy for a snapshot, or None if not set."""
    return _load_retention().get(name)


def remove_retention(name: str) -> bool:
    """Remove the retention policy for a snapshot. Returns False if not found."""
    data = _load_retention()
    if name not in data:
        return False
    del data[name]
    _save_retention(data)
    return True


def list_retention() -> Dict:
    """Return all retention policies."""
    return _load_retention()


def apply_retention(name: str) -> List[str]:
    """Apply the retention policy for a snapshot, pruning old saves.

    Returns a list of snapshot names that were removed."""
    policy_entry = get_retention(name)
    if not policy_entry:
        return []

    policy = policy_entry["policy"]
    value = policy_entry.get("value", 0)

    if policy == "keep_all":
        return []

    history = get_history(name=name)
    save_events = [e for e in history if e.get("event") == "save"]

    if policy == "keep_last":
        keep = max(1, value)
        to_remove = save_events[:-keep] if len(save_events) > keep else []
    elif policy == "keep_days":
        import time
        cutoff = time.time() - value * 86400
        to_remove = [e for e in save_events if e.get("ts", 0) < cutoff]
    else:
        to_remove = []

    removed = []
    for event in to_remove:
        snap_name = event.get("detail", {}).get("snapshot", name)
        if remove_snapshot(snap_name):
            removed.append(snap_name)
    return removed
