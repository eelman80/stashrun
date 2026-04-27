"""Amplification score: measures how much a snapshot influences others.

Combines dependency fan-out, group membership, profile references,
and relation count into a single amplification score (0-100).
"""

from __future__ import annotations

from stashrun.snapshot import list_all_snapshots
from stashrun.snapshots_dependencies import get_dependents
from stashrun.snapshots_groups import list_groups
from stashrun.snapshots_relations import get_relations
from stashrun.snapshot import get_snapshot


def compute_amplification(name: str) -> dict | None:
    """Return amplification metrics for *name*, or None if snapshot missing."""
    if get_snapshot(name) is None:
        return None

    dependents = get_dependents(name)          # snapshots that depend on this
    relations = get_relations(name)            # explicit relation edges

    # count groups this snapshot belongs to
    group_count = sum(
        1 for g in list_groups().values() if name in g.get("members", [])
    )

    dep_score = min(len(dependents) * 10, 40)
    rel_score = min(len(relations) * 8, 30)
    grp_score = min(group_count * 10, 30)

    total = dep_score + rel_score + grp_score

    return {
        "name": name,
        "dependents": len(dependents),
        "relations": len(relations),
        "groups": group_count,
        "dep_score": dep_score,
        "rel_score": rel_score,
        "grp_score": grp_score,
        "score": total,
    }


def amplification_rank() -> list[dict]:
    """Return all snapshots sorted by amplification score descending."""
    results = []
    for name in list_all_snapshots():
        entry = compute_amplification(name)
        if entry is not None:
            results.append(entry)
    return sorted(results, key=lambda x: x["score"], reverse=True)


def amplification_summary() -> dict:
    """Return aggregate stats across all snapshots."""
    ranked = amplification_rank()
    if not ranked:
        return {"count": 0, "avg_score": 0.0, "max_score": 0, "top": None}
    scores = [r["score"] for r in ranked]
    return {
        "count": len(ranked),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "top": ranked[0]["name"],
    }
