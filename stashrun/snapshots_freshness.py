"""Freshness scoring for snapshots based on age and access patterns."""

import time
from stashrun.snapshots_access import get_last_accessed, get_access_count
from stashrun.snapshot import get_snapshot
from stashrun.history import get_history

MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days
MAX_ACCESS_BONUS = 20


def compute_freshness(name: str) -> dict | None:
    """Compute a freshness score (0-100) for a snapshot.

    Higher score = more recently active and accessed.
    Returns None if snapshot does not exist.
    """
    if get_snapshot(name) is None:
        return None

    now = time.time()
    score = 0
    detail = {}

    # Age component (up to 60 points)
    last_accessed = get_last_accessed(name)
    if last_accessed:
        age = now - last_accessed
        age_score = max(0, 60 - int((age / MAX_AGE_SECONDS) * 60))
    else:
        age_score = 0
    score += age_score
    detail["age_score"] = age_score

    # Access frequency bonus (up to 20 points)
    count = get_access_count(name)
    access_score = min(MAX_ACCESS_BONUS, count * 2)
    score += access_score
    detail["access_score"] = access_score

    # Save recency bonus (up to 20 points)
    events = get_history(name)
    save_events = [e for e in events if e.get("event") == "save"]
    if save_events:
        latest_save = max(e.get("timestamp", 0) for e in save_events)
        save_age = now - latest_save
        save_score = max(0, 20 - int((save_age / MAX_AGE_SECONDS) * 20))
    else:
        save_score = 0
    score += save_score
    detail["save_score"] = save_score

    detail["total"] = min(100, score)
    return detail


def freshness_rank(names: list[str]) -> list[tuple[str, int]]:
    """Return snapshots sorted by freshness score descending."""
    results = []
    for name in names:
        result = compute_freshness(name)
        if result is not None:
            results.append((name, result["total"]))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def freshness_summary(names: list[str]) -> dict:
    """Return average and top freshness across a list of snapshots."""
    scores = []
    for name in names:
        r = compute_freshness(name)
        if r:
            scores.append(r["total"])
    if not scores:
        return {"count": 0, "average": 0, "top": None}
    top = max(scores)
    avg = round(sum(scores) / len(scores), 2)
    return {"count": len(scores), "average": avg, "top": top}
