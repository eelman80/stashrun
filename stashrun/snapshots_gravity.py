"""Gravity score: measures how much a snapshot 'pulls' others toward it.

Based on: number of dependents, mentions, relations, and endorsements.
"""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot, list_all_snapshots
from stashrun.snapshots_dependencies import get_dependents
from stashrun.snapshots_mentions import get_mentions
from stashrun.snapshots_relations import get_relations
from stashrun.snapshots_endorsements import get_endorsement_count


def compute_gravity(name: str) -> Optional[dict]:
    """Return a gravity breakdown dict, or None if the snapshot doesn't exist."""
    if get_snapshot(name) is None:
        return None

    dependents = get_dependents(name)          # list[str]
    mentions = get_mentions(name)              # list[str]
    relations = get_relations(name)            # dict[str, list]
    endorsements = get_endorsement_count(name) # int

    dep_score = min(len(dependents) * 15, 40)
    mention_score = min(len(mentions) * 5, 20)

    total_relations = sum(len(v) for v in relations.values())
    relation_score = min(total_relations * 4, 25)

    endorse_score = min(endorsements * 3, 15)

    total = dep_score + mention_score + relation_score + endorse_score

    return {
        "name": name,
        "dependents": len(dependents),
        "mentions": len(mentions),
        "relations": total_relations,
        "endorsements": endorsements,
        "dep_score": dep_score,
        "mention_score": mention_score,
        "relation_score": relation_score,
        "endorse_score": endorse_score,
        "total": total,
    }


def gravity_rank() -> list[dict]:
    """Return all snapshots sorted by gravity descending."""
    results = []
    for name in list_all_snapshots():
        g = compute_gravity(name)
        if g is not None:
            results.append(g)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def gravity_summary() -> dict:
    """Return aggregate gravity statistics across all snapshots."""
    ranked = gravity_rank()
    if not ranked:
        return {"count": 0, "avg": 0.0, "max": 0, "top": None}
    scores = [r["total"] for r in ranked]
    return {
        "count": len(scores),
        "avg": round(sum(scores) / len(scores), 2),
        "max": max(scores),
        "top": ranked[0]["name"],
    }
