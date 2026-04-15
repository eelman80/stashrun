"""Snapshot diff utilities: compare two snapshots or a snapshot against the live environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stashrun.snapshot import get_snapshot
from stashrun.env import capture_env


@dataclass
class SnapshotDiff:
    """Result of comparing two sets of environment variables."""

    added: Dict[str, str] = field(default_factory=dict)      # in right, not in left
    removed: Dict[str, str] = field(default_factory=dict)    # in left, not in right
    changed: Dict[str, tuple] = field(default_factory=dict)  # (left_val, right_val)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def compare_dicts(left: Dict[str, str], right: Dict[str, str]) -> SnapshotDiff:
    """Return a SnapshotDiff describing differences between *left* and *right*."""
    diff = SnapshotDiff()
    all_keys = set(left) | set(right)
    for key in all_keys:
        in_left = key in left
        in_right = key in right
        if in_left and in_right:
            if left[key] == right[key]:
                diff.unchanged[key] = left[key]
            else:
                diff.changed[key] = (left[key], right[key])
        elif in_left:
            diff.removed[key] = left[key]
        else:
            diff.added[key] = right[key]
    return diff


def diff_snapshots(name_a: str, name_b: str) -> Optional[SnapshotDiff]:
    """Compare two named snapshots.  Returns None if either snapshot is missing."""
    snap_a = get_snapshot(name_a)
    snap_b = get_snapshot(name_b)
    if snap_a is None or snap_b is None:
        return None
    return compare_dicts(snap_a, snap_b)


def diff_snapshot_vs_live(name: str, keys: Optional[List[str]] = None) -> Optional[SnapshotDiff]:
    """Compare a named snapshot against the current live environment.

    If *keys* is provided only those variables are considered.
    Returns None if the snapshot does not exist.
    """
    snap = get_snapshot(name)
    if snap is None:
        return None
    live = capture_env(keys=keys)
    if keys:
        snap = {k: v for k, v in snap.items() if k in keys}
    return compare_dicts(snap, live)
