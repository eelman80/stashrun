"""Snapshot pinning — mark snapshots as protected from deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from stashrun.storage import get_stash_dir


def _pins_path() -> Path:
    return get_stash_dir() / "pins.json"


def _load_pins() -> List[str]:
    path = _pins_path()
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_pins(pins: List[str]) -> None:
    _pins_path().write_text(json.dumps(sorted(set(pins)), indent=2))


def pin_snapshot(name: str) -> bool:
    """Pin a snapshot. Returns True if newly pinned, False if already pinned."""
    pins = _load_pins()
    if name in pins:
        return False
    pins.append(name)
    _save_pins(pins)
    return True


def unpin_snapshot(name: str) -> bool:
    """Unpin a snapshot. Returns True if removed, False if not found."""
    pins = _load_pins()
    if name not in pins:
        return False
    pins.remove(name)
    _save_pins(pins)
    return True


def is_pinned(name: str) -> bool:
    """Return True if the snapshot is pinned."""
    return name in _load_pins()


def list_pins() -> List[str]:
    """Return all pinned snapshot names."""
    return _load_pins()


def clear_pins() -> int:
    """Remove all pins. Returns the number of pins cleared."""
    pins = _load_pins()
    count = len(pins)
    _save_pins([])
    return count
