"""Subscriber tracking for snapshots — who is watching a snapshot for changes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from stashrun.storage import get_stash_dir


def _subscribers_path() -> Path:
    return get_stash_dir() / "subscribers.json"


def _load_subscribers() -> Dict[str, List[str]]:
    p = _subscribers_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_subscribers(data: Dict[str, List[str]]) -> None:
    p = _subscribers_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def subscribe(name: str, subscriber: str) -> bool:
    """Add a subscriber to a snapshot. Returns False if already subscribed."""
    data = _load_subscribers()
    subs = data.setdefault(name, [])
    if subscriber in subs:
        return False
    subs.append(subscriber)
    _save_subscribers(data)
    return True


def unsubscribe(name: str, subscriber: str) -> bool:
    """Remove a subscriber from a snapshot. Returns False if not found."""
    data = _load_subscribers()
    subs = data.get(name, [])
    if subscriber not in subs:
        return False
    subs.remove(subscriber)
    data[name] = subs
    _save_subscribers(data)
    return True


def list_subscribers(name: str) -> List[str]:
    """Return all subscribers for a snapshot."""
    return _load_subscribers().get(name, [])


def clear_subscribers(name: str) -> int:
    """Remove all subscribers for a snapshot. Returns count removed."""
    data = _load_subscribers()
    removed = len(data.pop(name, []))
    _save_subscribers(data)
    return removed


def find_subscriptions(subscriber: str) -> List[str]:
    """Return all snapshot names a given subscriber is watching."""
    data = _load_subscribers()
    return [name for name, subs in data.items() if subscriber in subs]
