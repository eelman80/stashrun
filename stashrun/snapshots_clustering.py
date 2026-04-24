"""Cluster snapshots by env key similarity into named groups."""

from typing import Optional
from stashrun.snapshot import list_all_snapshots, get_snapshot
from stashrun.tags import get_tags


def _key_set(name: str) -> set:
    env = get_snapshot(name)
    if env is None:
        return set()
    return set(env.keys())


def jaccard_similarity(a: set, b: set) -> float:
    """Return Jaccard similarity coefficient between two sets."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def cluster_snapshots(threshold: float = 0.5) -> dict[str, list[str]]:
    """Group snapshots into clusters where pairwise Jaccard >= threshold.

    Returns a dict mapping a representative snapshot name to the list
    of snapshot names in that cluster (including the representative).
    Uses a simple greedy single-linkage approach.
    """
    names = list_all_snapshots()
    key_sets = {n: _key_set(n) for n in names}
    assigned: dict[str, str] = {}  # snapshot -> cluster representative
    clusters: dict[str, list[str]] = {}

    for name in names:
        placed = False
        for rep in list(clusters.keys()):
            if jaccard_similarity(key_sets[name], key_sets[rep]) >= threshold:
                clusters[rep].append(name)
                assigned[name] = rep
                placed = True
                break
        if not placed:
            clusters[name] = [name]
            assigned[name] = name

    return clusters


def cluster_summary(threshold: float = 0.5) -> list[dict]:
    """Return a list of cluster info dicts for display."""
    clusters = cluster_snapshots(threshold)
    summary = []
    for rep, members in clusters.items():
        summary.append({
            "representative": rep,
            "size": len(members),
            "members": sorted(members),
        })
    summary.sort(key=lambda c: -c["size"])
    return summary


def find_cluster(name: str, threshold: float = 0.5) -> Optional[list[str]]:
    """Return the cluster containing *name*, or None if snapshot missing."""
    if get_snapshot(name) is None:
        return None
    clusters = cluster_snapshots(threshold)
    for rep, members in clusters.items():
        if name in members:
            return sorted(members)
    return [name]
