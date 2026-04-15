"""High-level snapshot operations (create, restore, list, remove).

This file replaces the previous version and adds tag-cleanup on removal.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from stashrun.env import capture_env
from stashrun.storage import (
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from stashrun.tags import remove_snapshot_tags


def create_snapshot(
    name: str,
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> Dict[str, str]:
    """Capture current env and persist it as *name*."""
    env = capture_env(keys=keys, prefix=prefix)
    save_snapshot(name, env)
    return env


def restore_snapshot(name: str) -> Optional[Dict[str, str]]:
    """Load snapshot *name* and apply it to the current process env.

    Returns the env dict, or None if the snapshot does not exist.
    """
    import os

    env = load_snapshot(name)
    if env is None:
        return None
    os.environ.update(env)
    return env


def get_snapshot(name: str) -> Optional[Dict[str, str]]:
    """Return the env dict for *name*, or None."""
    return load_snapshot(name)


def remove_snapshot(name: str) -> bool:
    """Delete snapshot *name* and its associated tags.

    Returns True if the snapshot existed and was deleted.
    """
    deleted = delete_snapshot(name)
    if deleted:
        remove_snapshot_tags(name)
    return deleted


def list_all_snapshots() -> List[str]:
    """Return sorted list of all snapshot names."""
    return sorted(list_snapshots())
