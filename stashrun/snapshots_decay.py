"""Decay scoring for snapshots — measures how stale or neglected a snapshot is."""

from __future__ import annotations

import time
from typing import Optional

from stashrun.snapshot import get_snapshot, list_all_snapshots
from stashrun.snapshots_access import get_last_accessed
from stashrun.snapshots_ttl import get_ttl
from stashrun.snapshots_status import get_status
from stashrun.pinning import get_pinned

_MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days
_MAX_DECAY = 100


def compute_decay(name: str) -> Optional[dict]:
    """Compute a decay score (0–100) for a snapshot.

    Higher score means more decayed / stale.
    Returns None if the snapshot does not exist.
    """
    if get_snapshot(name) is None:
        return None

    now = time.time()
    score = 0
    reasons = []

    # Factor 1: time since last access (up to 50 points)
    last_accessed = get_last_accessed(name)
    if last_accessed is None:
        score += 50
        reasons.append("never accessed")
    else:
        age = now - last_accessed
        age_score = min(50, int((age / _MAX_AGE_SECONDS) * 50))
        score += age_score
        if age_score > 0:
            reasons.append(f"last accessed {int(age // 86400)}d ago")

    # Factor 2: expired TTL (up to 30 points)
    ttl = get_ttl(name)
    if ttl is not None and ttl < now:
        score += 30
        reasons.append("TTL expired")

    # Factor 3: status is deprecated or archived (up to 20 points)
    status = get_status(name)
    if status in ("deprecated", "archived"):
        score += 20
        reasons.append(f"status={status}")

    # Pinned snapshots get a decay reduction
    if name in get_pinned():
        score = max(0, score - 20)
        reasons.append("pinned (-20)")

    score = min(_MAX_DECAY, score)
    return {"name": name, "decay": score, "reasons": reasons}


def decay_rank() -> list[dict]:
    """Return all snapshots sorted by decay score descending."""
    results = []
    for name in list_all_snapshots():
        entry = compute_decay(name)
        if entry is not None:
            results.append(entry)
    return sorted(results, key=lambda x: x["decay"], reverse=True)


def decay_summary() -> dict:
    """Return aggregate decay statistics across all snapshots."""
    ranked = decay_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "max": 0, "min": 0}
    scores = [r["decay"] for r in ranked]
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 2),
        "max": max(scores),
        "min": min(scores),
    }
