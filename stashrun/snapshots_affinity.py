"""Affinity scoring between snapshots and user-defined profiles.

Affinity measures how well a snapshot's keys align with a named profile's
expected key set, returning a normalised 0–100 score.
"""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot
from stashrun.profiles import get_profile_snapshots
from stashrun.storage import list_snapshots


def compute_affinity(snapshot_name: str, profile_name: str) -> Optional[dict]:
    """Return an affinity dict for *snapshot_name* against *profile_name*.

    Returns ``None`` if the snapshot does not exist.
    """
    env = get_snapshot(snapshot_name)
    if env is None:
        return None

    profile_members = get_profile_snapshots(profile_name)
    if not profile_members:
        return {"snapshot": snapshot_name, "profile": profile_name, "score": 0, "shared_keys": 0, "total_keys": len(env)}

    # Collect the union of keys across all snapshots in the profile
    profile_key_set: set[str] = set()
    for member in profile_members:
        member_env = get_snapshot(member)
        if member_env:
            profile_key_set.update(member_env.keys())

    if not profile_key_set:
        return {"snapshot": snapshot_name, "profile": profile_name, "score": 0, "shared_keys": 0, "total_keys": len(env)}

    snapshot_keys = set(env.keys())
    shared = snapshot_keys & profile_key_set
    union = snapshot_keys | profile_key_set
    score = round(len(shared) / len(union) * 100, 1) if union else 0.0

    return {
        "snapshot": snapshot_name,
        "profile": profile_name,
        "score": score,
        "shared_keys": len(shared),
        "total_keys": len(snapshot_keys),
        "profile_keys": len(profile_key_set),
    }


def affinity_rank(profile_name: str) -> list[dict]:
    """Return all snapshots ranked by affinity to *profile_name* (descending)."""
    results = []
    for name in list_snapshots():
        result = compute_affinity(name, profile_name)
        if result is not None:
            results.append(result)
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def affinity_summary(profile_name: str) -> dict:
    """Return summary statistics for affinity scores across all snapshots."""
    ranked = affinity_rank(profile_name)
    if not ranked:
        return {"profile": profile_name, "count": 0, "avg_score": 0.0, "top": None}
    scores = [r["score"] for r in ranked]
    return {
        "profile": profile_name,
        "count": len(ranked),
        "avg_score": round(sum(scores) / len(scores), 1),
        "top": ranked[0]["snapshot"],
    }
