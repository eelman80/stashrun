"""Snapshot velocity: measures how quickly a snapshot is being updated over time."""

from __future__ import annotations

from typing import Optional

from stashrun.snapshots_versioning import list_versions
from stashrun.snapshots_access import get_last_accessed, get_access_count
from stashrun.snapshot import get_snapshot, list_all_snapshots


def compute_velocity(name: str) -> Optional[dict]:
    """Compute velocity metrics for a snapshot.

    Returns a dict with:
      - version_count: total number of versions pushed
      - access_count: total number of accesses recorded
      - version_score: capped contribution from versions (0-50)
      - access_score: capped contribution from accesses (0-30)
      - recency_bonus: 20 if last_accessed is set, else 0
      - score: overall velocity score (0-100)
    """
    if get_snapshot(name) is None:
        return None

    versions = list_versions(name) or []
    version_count = len(versions)

    access_count = get_access_count(name) or 0
    last_accessed = get_last_accessed(name)

    version_score = min(version_count * 5, 50)
    access_score = min(access_count * 3, 30)
    recency_bonus = 20 if last_accessed else 0

    score = version_score + access_score + recency_bonus

    return {
        "version_count": version_count,
        "access_count": access_count,
        "version_score": version_score,
        "access_score": access_score,
        "recency_bonus": recency_bonus,
        "score": score,
    }


def velocity_rank() -> list[tuple[str, int]]:
    """Return all snapshots ranked by velocity score descending."""
    results = []
    for name in list_all_snapshots():
        data = compute_velocity(name)
        if data is not None:
            results.append((name, data["score"]))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def velocity_summary() -> dict:
    """Return aggregate velocity stats across all snapshots."""
    ranked = velocity_rank()
    if not ranked:
        return {"count": 0, "avg_score": 0, "top": None}
    scores = [s for _, s in ranked]
    return {
        "count": len(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
        "top": ranked[0][0],
    }
