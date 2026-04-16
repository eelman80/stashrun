"""TTL (time-to-live) support for snapshots."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _ttl_path() -> Path:
    return get_stash_dir() / "ttl.json"


def _load_ttl() -> dict:
    p = _ttl_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_ttl(data: dict) -> None:
    p = _ttl_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_ttl(name: str, seconds: int) -> None:
    """Set a TTL for a snapshot. Expires at now + seconds."""
    data = _load_ttl()
    data[name] = time.time() + seconds
    _save_ttl(data)


def remove_ttl(name: str) -> bool:
    data = _load_ttl()
    if name not in data:
        return False
    del data[name]
    _save_ttl(data)
    return True


def get_ttl(name: str) -> Optional[float]:
    """Return expiry timestamp or None if not set."""
    return _load_ttl().get(name)


def is_expired(name: str) -> bool:
    """Return True if the snapshot TTL has passed."""
    expiry = get_ttl(name)
    if expiry is None:
        return False
    return time.time() > expiry


def list_expired() -> list[str]:
    """Return names of all snapshots whose TTL has expired."""
    data = _load_ttl()
    now = time.time()
    return [name for name, expiry in data.items() if now > expiry]


def purge_expired(delete_fn) -> list[str]:
    """Delete all expired snapshots using delete_fn(name). Returns purged names."""
    expired = list_expired()
    purged = []
    for name in expired:
        try:
            delete_fn(name)
            remove_ttl(name)
            purged.append(name)
        except Exception:
            pass
    return purged
