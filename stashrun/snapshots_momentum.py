"""Momentum scoring: measures how actively a snapshot is being improved over time."""

from typing import Optional
from stashrun.snapshot import get_snapshot, list_all_snapshots
from stashrun.snapshots_versioning import list_versions
from stashrun.snapshots_access import get_last_accessed, get_access_count
from stashrun.snapshots_ratings import get_rating
from stashrun.history import get_history
import time

_MAX_VERSION_SCORE = 40
_MAX_ACCESS_SCORE = 30
_MAX_RATING_SCORE = 20
_MAX_RECENCY_SCORE = 10
_RECENCY_WINDOW = 7 * 24 * 3600  # 7 days


def compute_momentum(name: str) -> Optional[dict]:
    """Compute a momentum score for a snapshot based on activity signals."""
    if get_snapshot(name) is None:
        return None

    versions = list_versions(name) or []
    version_score = min(len(versions) * 8, _MAX_VERSION_SCORE)

    access_count = get_access_count(name) or 0
    access_score = min(access_count * 3, _MAX_ACCESS_SCORE)

    rating = get_rating(name)
    rating_score = round((rating / 5.0) * _MAX_RATING_SCORE) if rating else 0

    now = time.time()
    last_accessed = get_last_accessed(name)
    if last_accessed:
        age = now - last_accessed
        recency_score = max(0, _MAX_RECENCY_SCORE - int(age / _RECENCY_WINDOW) * 2)
    else:
        recency_score = 0

    total = version_score + access_score + rating_score + recency_score
    return {
        "name": name,
        "version_score": version_score,
        "access_score": access_score,
        "rating_score": rating_score,
        "recency_score": recency_score,
        "total": total,
    }


def momentum_rank() -> list:
    """Return all snapshots sorted by momentum score descending."""
    results = []
    for name in list_all_snapshots():
        m = compute_momentum(name)
        if m is not None:
            results.append(m)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def momentum_summary() -> dict:
    """Return aggregate momentum statistics."""
    ranked = momentum_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "top": None}
    total = sum(r["total"] for r in ranked)
    return {
        "count": len(ranked),
        "average": round(total / len(ranked), 2),
        "top": ranked[0]["name"] if ranked else None,
    }
