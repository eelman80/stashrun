"""Merge two or more snapshots into a new combined snapshot."""

from typing import Optional
from stashrun.snapshot import get_snapshot, create_snapshot


MERGE_STRATEGY_LAST_WINS = "last_wins"
MERGE_STRATEGY_FIRST_WINS = "first_wins"
MERGE_STRATEGY_STRICT = "strict"


def merge_envs(
    envs: list[dict],
    strategy: str = MERGE_STRATEGY_LAST_WINS,
) -> tuple[dict, list[str]]:
    """Merge a list of env dicts using the given strategy.

    Returns (merged_dict, list_of_conflict_keys).
    """
    merged: dict = {}
    conflicts: list[str] = []

    for env in envs:
        for key, value in env.items():
            if key in merged and merged[key] != value:
                conflicts.append(key)
                if strategy == MERGE_STRATEGY_FIRST_WINS:
                    continue
                elif strategy == MERGE_STRATEGY_STRICT:
                    raise ValueError(
                        f"Conflict on key '{key}': '{merged[key]}' vs '{value}'"
                    )
            merged[key] = value

    return merged, list(set(conflicts))


def merge_snapshots(
    names: list[str],
    target_name: str,
    strategy: str = MERGE_STRATEGY_LAST_WINS,
    prefix: Optional[str] = None,
) -> Optional[dict]:
    """Load named snapshots, merge them, and save as target_name.

    Returns the merged env dict, or None if any source snapshot is missing.
    """
    envs: list[dict] = []
    for name in names:
        snap = get_snapshot(name)
        if snap is None:
            return None
        envs.append(snap)

    merged, _ = merge_envs(envs, strategy=strategy)
    create_snapshot(target_name, env=merged, prefix=prefix)
    return merged


def merge_conflicts(
    names: list[str],
) -> dict[str, list[str]]:
    """Return a mapping of conflicting keys to the list of differing values
    found across the given snapshots.
    """
    key_values: dict[str, list[str]] = {}
    for name in names:
        snap = get_snapshot(name)
        if snap is None:
            continue
        for key, value in snap.items():
            key_values.setdefault(key, [])
            if value not in key_values[key]:
                key_values[key].append(value)

    return {k: v for k, v in key_values.items() if len(v) > 1}
