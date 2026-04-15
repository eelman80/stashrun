"""Track which environment variable keys are 'watched' for change alerts."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _watchlist_path() -> Path:
    return get_stash_dir() / "watchlist.json"


def _load_watchlist() -> dict:
    path = _watchlist_path()
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_watchlist(data: dict) -> None:
    path = _watchlist_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def watch_key(key: str, label: str | None = None) -> bool:
    """Add a key to the watchlist. Returns True if newly added, False if already present."""
    data = _load_watchlist()
    if key in data:
        return False
    data[key] = {"label": label or key}
    _save_watchlist(data)
    return True


def unwatch_key(key: str) -> bool:
    """Remove a key from the watchlist. Returns True if removed, False if not found."""
    data = _load_watchlist()
    if key not in data:
        return False
    del data[key]
    _save_watchlist(data)
    return True


def get_watched_keys() -> list[str]:
    """Return all currently watched keys."""
    return list(_load_watchlist().keys())


def is_watched(key: str) -> bool:
    """Check whether a specific key is on the watchlist."""
    return key in _load_watchlist()


def check_watched_changes(old_env: dict, new_env: dict) -> list[dict]:
    """Compare two env dicts and return change records for watched keys."""
    watched = _load_watchlist()
    changes = []
    for key in watched:
        old_val = old_env.get(key)
        new_val = new_env.get(key)
        if old_val != new_val:
            changes.append({
                "key": key,
                "label": watched[key].get("label", key),
                "old": old_val,
                "new": new_val,
            })
    return changes
