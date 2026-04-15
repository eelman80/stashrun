"""Search and filter snapshots by name, tags, keys, and values."""

from typing import Optional
from stashrun.storage import list_snapshots, load_snapshot
from stashrun.tags import get_tags


def search_by_name(pattern: str, stash_dir: Optional[str] = None) -> list[str]:
    """Return snapshot names containing the given pattern (case-insensitive)."""
    pattern = pattern.lower()
    return [
        name for name in list_snapshots(stash_dir)
        if pattern in name.lower()
    ]


def search_by_tag(tag: str, stash_dir: Optional[str] = None) -> list[str]:
    """Return snapshot names that have the given tag."""
    results = []
    for name in list_snapshots(stash_dir):
        if tag in get_tags(name, stash_dir):
            results.append(name)
    return results


def search_by_key(key: str, stash_dir: Optional[str] = None) -> list[str]:
    """Return snapshot names that contain the given environment variable key."""
    results = []
    for name in list_snapshots(stash_dir):
        data = load_snapshot(name, stash_dir)
        if data and key in data:
            results.append(name)
    return results


def search_by_value(value: str, stash_dir: Optional[str] = None) -> list[str]:
    """Return snapshot names that contain an env var with the given value."""
    results = []
    for name in list_snapshots(stash_dir):
        data = load_snapshot(name, stash_dir)
        if data and value in data.values():
            results.append(name)
    return results


def search_by_key_pattern(pattern: str, stash_dir: Optional[str] = None) -> list[str]:
    """Return snapshot names that contain any key matching pattern (case-insensitive)."""
    pattern = pattern.lower()
    results = []
    for name in list_snapshots(stash_dir):
        data = load_snapshot(name, stash_dir)
        if data and any(pattern in k.lower() for k in data):
            results.append(name)
    return results
