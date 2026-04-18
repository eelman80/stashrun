"""Track and query last-accessed timestamps for snapshots."""

import json
import time
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _access_path() -> Path:
    return get_stash_dir() / "access_log.json"


def _load_access() -> dict:
    p = _access_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_access(data: dict) -> None:
    p = _access_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def record_access(name: str) -> float:
    """Record current time as last-accessed for snapshot. Returns timestamp."""
    data = _load_access()
    ts = time.time()
    data[name] = ts
    _save_access(data)
    return ts


def get_last_accessed(name: str) -> Optional[float]:
    """Return last-accessed timestamp for snapshot, or None."""
    return _load_access().get(name)


def remove_access(name: str) -> bool:
    """Remove access record for snapshot. Returns True if it existed."""
    data = _load_access()
    if name not in data:
        return False
    del data[name]
    _save_access(data)
    return True


def list_accessed(limit: int = 10) -> list[tuple[str, float]]:
    """Return snapshots sorted by most recently accessed."""
    data = _load_access()
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return sorted_items[:limit]


def never_accessed(all_names: list[str]) -> list[str]:
    """Return snapshot names that have no access record."""
    data = _load_access()
    return [n for n in all_names if n not in data]
