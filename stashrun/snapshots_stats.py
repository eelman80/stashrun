"""Statistics and summary utilities for snapshots."""
from __future__ import annotations
from typing import Optional
from stashrun.snapshot import list_all_snapshots, get_snapshot
from stashrun.tags import get_tags
from stashrun.history import get_history
from stashrun.pinning import list_pins


def snapshot_count() -> int:
    return len(list_all_snapshots())


def total_keys() -> int:
    total = 0
    for name in list_all_snapshots():
        env = get_snapshot(name)
        if env:
            total += len(env)
    return total


def average_keys() -> float:
    names = list_all_snapshots()
    if not names:
        return 0.0
    counts = []
    for name in names:
        env = get_snapshot(name)
        if env:
            counts.append(len(env))
    return sum(counts) / len(counts) if counts else 0.0


def most_common_keys(top_n: int = 5) -> list[tuple[str, int]]:
    freq: dict[str, int] = {}
    for name in list_all_snapshots():
        env = get_snapshot(name)
        if env:
            for key in env:
                freq[key] = freq.get(key, 0) + 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]


def tagged_snapshot_count() -> int:
    return sum(1 for name in list_all_snapshots() if get_tags(name))


def pinned_snapshot_count() -> int:
    return len(list_pins())


def summary() -> dict:
    names = list_all_snapshots()
    return {
        "total_snapshots": snapshot_count(),
        "total_keys": total_keys(),
        "average_keys": round(average_keys(), 2),
        "tagged": tagged_snapshot_count(),
        "pinned": pinned_snapshot_count(),
        "most_common_keys": most_common_keys(5),
    }
