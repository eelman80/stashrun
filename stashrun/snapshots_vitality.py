"""Snapshot vitality scoring — combines freshness, health, and momentum into a single vitality metric."""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot
from stashrun.snapshots_freshness import compute_freshness
from stashrun.snapshots_health import compute_health
from stashrun.snapshots_momentum import compute_momentum
from stashrun.storage import list_snapshots


def compute_vitality(name: str) -> Optional[dict]:
    """Compute a vitality score (0-100) for a snapshot.

    Vitality is a weighted blend of:
      - freshness  (40 %)
      - health     (40 %)
      - momentum   (20 %)

    Returns None if the snapshot does not exist.
    """
    if get_snapshot(name) is None:
        return None

    freshness = compute_freshness(name)
    health = compute_health(name)
    momentum = compute_momentum(name)

    freshness_score = freshness["score"] if freshness else 0
    health_score = health["score"] if health else 0
    momentum_score = momentum["score"] if momentum else 0

    score = round(
        freshness_score * 0.40
        + health_score * 0.40
        + momentum_score * 0.20
    )

    return {
        "name": name,
        "score": score,
        "freshness": freshness_score,
        "health": health_score,
        "momentum": momentum_score,
    }


def vitality_rank() -> list[dict]:
    """Return all snapshots sorted by vitality score descending."""
    results = []
    for name in list_snapshots():
        v = compute_vitality(name)
        if v is not None:
            results.append(v)
    return sorted(results, key=lambda x: x["score"], reverse=True)


def vitality_summary() -> dict:
    """Aggregate vitality statistics across all snapshots."""
    ranked = vitality_rank()
    if not ranked:
        return {"count": 0, "average": 0, "top": None, "bottom": None}
    scores = [r["score"] for r in ranked]
    return {
        "count": len(ranked),
        "average": round(sum(scores) / len(scores)),
        "top": ranked[0]["name"],
        "bottom": ranked[-1]["name"],
    }
