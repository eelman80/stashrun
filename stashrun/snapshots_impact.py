"""Compute impact score for snapshots based on dependents, subscribers, and group membership."""

from stashrun.snapshots_dependencies import get_dependents
from stashrun.snapshots_subscribers import get_subscribers
from stashrun.snapshots_groups import list_groups
from stashrun.snapshot import get_snapshot


def compute_impact(name: str) -> dict | None:
    """Return an impact breakdown for a snapshot."""
    env = get_snapshot(name)
    if env is None:
        return None

    dependents = get_dependents(name)
    subscribers = get_subscribers(name)

    groups = list_groups()
    group_count = sum(1 for g in groups.values() if name in g.get("snapshots", []))

    dependent_score = min(len(dependents) * 10, 40)
    subscriber_score = min(len(subscribers) * 5, 30)
    group_score = min(group_count * 10, 30)
    total = dependent_score + subscriber_score + group_score

    return {
        "name": name,
        "dependents": len(dependents),
        "subscribers": len(subscribers),
        "groups": group_count,
        "dependent_score": dependent_score,
        "subscriber_score": subscriber_score,
        "group_score": group_score,
        "total": total,
    }


def impact_rank(names: list[str]) -> list[dict]:
    """Return snapshots sorted by impact score descending."""
    results = []
    for name in names:
        score = compute_impact(name)
        if score is not None:
            results.append(score)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def impact_summary(names: list[str]) -> dict:
    """Return aggregate impact stats across all given snapshots."""
    scores = [compute_impact(n) for n in names]
    scores = [s for s in scores if s is not None]
    if not scores:
        return {"count": 0, "avg_total": 0, "max_total": 0}
    totals = [s["total"] for s in scores]
    return {
        "count": len(totals),
        "avg_total": round(sum(totals) / len(totals), 2),
        "max_total": max(totals),
    }
