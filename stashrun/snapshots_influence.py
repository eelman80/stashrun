"""Compute influence score for snapshots based on relationships and usage."""

from stashrun.snapshots_dependencies import get_dependents
from stashrun.snapshots_subscribers import get_subscribers
from stashrun.snapshots_mentions import get_mentions
from stashrun.snapshots_endorsements import get_endorsers
from stashrun.snapshot import get_snapshot
from stashrun.storage import list_snapshots

_MAX_DEPENDENTS = 40
_MAX_SUBSCRIBERS = 25
_MAX_MENTIONS = 20
_MAX_ENDORSEMENTS = 15


def compute_influence(name: str) -> dict | None:
    """Return an influence breakdown dict for a snapshot, or None if missing."""
    if get_snapshot(name) is None:
        return None

    dependents = get_dependents(name)
    dep_score = min(len(dependents) * 8, _MAX_DEPENDENTS)

    subscribers = get_subscribers(name)
    sub_score = min(len(subscribers) * 5, _MAX_SUBSCRIBERS)

    mentions = get_mentions(name)
    mention_score = min(len(mentions) * 4, _MAX_MENTIONS)

    endorsers = get_endorsers(name)
    endorse_score = min(len(endorsers) * 5, _MAX_ENDORSEMENTS)

    total = dep_score + sub_score + mention_score + endorse_score

    return {
        "name": name,
        "dependents": len(dependents),
        "subscribers": len(subscribers),
        "mentions": len(mentions),
        "endorsements": len(endorsers),
        "dep_score": dep_score,
        "sub_score": sub_score,
        "mention_score": mention_score,
        "endorse_score": endorse_score,
        "total": total,
    }


def influence_rank() -> list[dict]:
    """Return all snapshots sorted by influence score descending."""
    results = []
    for name in list_snapshots():
        info = compute_influence(name)
        if info is not None:
            results.append(info)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def influence_summary() -> dict:
    """Return aggregate influence statistics across all snapshots."""
    ranked = influence_rank()
    if not ranked:
        return {"count": 0, "avg": 0.0, "max": 0, "top": None}
    scores = [r["total"] for r in ranked]
    return {
        "count": len(scores),
        "avg": round(sum(scores) / len(scores), 2),
        "max": max(scores),
        "top": ranked[0]["name"],
    }
