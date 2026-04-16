"""Rollback support: revert a snapshot to a previous history entry."""

from __future__ import annotations

from typing import Optional

from stashrun.history import get_history, record_event
from stashrun.snapshot import create_snapshot, get_snapshot, restore_snapshot


def get_rollback_candidates(name: str) -> list[dict]:
    """Return history entries for *name* that can be rolled back to."""
    events = get_history(name=name)
    return [e for e in events if e.get("event") == "save"]


def rollback_snapshot(name: str, steps: int = 1) -> Optional[dict]:
    """Restore a snapshot to the env captured *steps* saves ago.

    Returns the env dict that was restored, or None if not possible.
    """
    candidates = get_rollback_candidates(name)
    # candidates are oldest-first; we want the Nth-from-last
    if len(candidates) < steps + 1:
        return None

    target = candidates[-(steps + 1)]
    env = target.get("detail", {}).get("env")
    if env is None:
        return None

    # Overwrite the current snapshot with the historic env
    create_snapshot(name, env=env)
    record_event(name, "rollback", detail={"steps": steps, "env": env})
    return env


def rollback_to_index(name: str, index: int) -> Optional[dict]:
    """Restore a snapshot to a specific history index (0 = oldest save)."""
    candidates = get_rollback_candidates(name)
    if index < 0 or index >= len(candidates):
        return None

    target = candidates[index]
    env = target.get("detail", {}).get("env")
    if env is None:
        return None

    create_snapshot(name, env=env)
    record_event(name, "rollback", detail={"index": index, "env": env})
    return env
