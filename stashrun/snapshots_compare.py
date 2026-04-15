"""Compare multiple snapshots side-by-side."""

from typing import Optional
from stashrun.snapshot import get_snapshot


def compare_snapshots(names: list[str]) -> dict:
    """Load multiple snapshots and return a comparison matrix.

    Returns a dict with:
      - 'snapshots': list of snapshot names (in order)
      - 'keys': sorted union of all keys across snapshots
      - 'matrix': dict[key] -> list of values (one per snapshot, None if absent)
    """
    loaded: list[Optional[dict]] = [get_snapshot(n) for n in names]

    all_keys: set[str] = set()
    for env in loaded:
        if env:
            all_keys.update(env.keys())

    sorted_keys = sorted(all_keys)
    matrix: dict[str, list[Optional[str]]] = {}
    for key in sorted_keys:
        matrix[key] = [
            env.get(key) if env else None
            for env in loaded
        ]

    return {
        "snapshots": names,
        "keys": sorted_keys,
        "matrix": matrix,
    }


def keys_unique_to(name: str, others: list[str]) -> dict[str, str]:
    """Return keys present in *name* but absent in all *others*."""
    target = get_snapshot(name) or {}
    other_keys: set[str] = set()
    for n in others:
        env = get_snapshot(n)
        if env:
            other_keys.update(env.keys())
    return {k: v for k, v in target.items() if k not in other_keys}


def keys_in_common(names: list[str]) -> dict[str, list[Optional[str]]]:
    """Return only keys that appear in ALL snapshots, with their values."""
    if not names:
        return {}
    envs = [get_snapshot(n) or {} for n in names]
    common_keys = set(envs[0].keys())
    for env in envs[1:]:
        common_keys &= set(env.keys())
    return {
        k: [env.get(k) for env in envs]
        for k in sorted(common_keys)
    }


def value_conflicts(names: list[str]) -> dict[str, list[Optional[str]]]:
    """Return keys shared by all snapshots where the value differs."""
    common = keys_in_common(names)
    return {
        k: vals
        for k, vals in common.items()
        if(v for v in vals if v is not None)) > 1
    }
