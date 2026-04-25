"""Stickiness metric: measures how consistently a snapshot is reused over time."""

from __future__ import annotations

from typing import Optional

from stashrun.storage import list_snapshots
from stashrun.snapshots_access import get_last_accessed, get_access_count
from stashrun.snapshots_favorites import is_favorite
from stashrun.snapshots_bookmarks import resolve_bookmark
from stashrun.snapshots_pinning import is_pinned
from stashrun.history import get_history


def compute_stickiness(name: str) -> Optional[dict]:
    """Compute stickiness score for a snapshot.

    Stickiness reflects how deeply embedded a snapshot is in regular usage.
    Score components (max 100):
      - access_count  : up to 40 pts (capped at 20 accesses)
      - is_favorite   : 15 pts
      - is_pinned     : 15 pts
      - has_bookmark  : 10 pts
      - restore_events: up to 20 pts (capped at 10 restores)
    """
    from stashrun.snapshot import get_snapshot
    if get_snapshot(name) is None:
        return None

    access_count = get_access_count(name) or 0
    access_score = min(access_count, 20) * 2  # max 40

    favorite_score = 15 if is_favorite(name) else 0
    pinned_score = 15 if is_pinned(name) else 0

    bookmarks = resolve_bookmark.__module__
    from stashrun.snapshots_bookmarks import _load_bookmarks
    bm_data = _load_bookmarks()
    bookmark_score = 10 if name in bm_data.values() else 0

    history = get_history(name=name)
    restore_count = sum(1 for e in history if e.get("event") == "restore")
    restore_score = min(restore_count, 10) * 2  # max 20

    total = access_score + favorite_score + pinned_score + bookmark_score + restore_score

    return {
        "name": name,
        "access_score": access_score,
        "favorite_score": favorite_score,
        "pinned_score": pinned_score,
        "bookmark_score": bookmark_score,
        "restore_score": restore_score,
        "total": total,
    }


def stickiness_rank() -> list[dict]:
    """Return all snapshots ranked by stickiness (descending)."""
    results = []
    for name in list_snapshots():
        score = compute_stickiness(name)
        if score is not None:
            results.append(score)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def stickiness_summary() -> dict:
    """Return aggregate stickiness statistics across all snapshots."""
    ranked = stickiness_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "max": 0, "min": 0}
    totals = [r["total"] for r in ranked]
    return {
        "count": len(totals),
        "average": round(sum(totals) / len(totals), 2),
        "max": max(totals),
        "min": min(totals),
    }
