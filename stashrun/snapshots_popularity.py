"""Snapshot popularity scoring based on access frequency, favorites, reactions, and ratings."""

from stashrun.snapshots_access import get_access_count
from stashrun.snapshots_favorites import is_favorite
from stashrun.snapshots_reactions import get_reactions
from stashrun.snapshots_ratings import get_rating
from stashrun.snapshot import list_all_snapshots


def compute_popularity(name: str) -> dict | None:
    """Compute a popularity breakdown for a snapshot."""
    from stashrun.snapshot import get_snapshot
    if get_snapshot(name) is None:
        return None

    access_count = get_access_count(name) or 0
    favorited = 1 if is_favorite(name) else 0
    reactions = get_reactions(name) or {}
    reaction_count = sum(reactions.values()) if reactions else 0
    rating = get_rating(name) or 0

    access_score = min(access_count * 2, 40)
    favorite_score = favorited * 20
    reaction_score = min(reaction_count * 3, 20)
    rating_score = (rating / 5.0) * 20

    total = access_score + favorite_score + reaction_score + rating_score

    return {
        "name": name,
        "access_score": access_score,
        "favorite_score": favorite_score,
        "reaction_score": reaction_score,
        "rating_score": round(rating_score, 2),
        "total": round(total, 2),
    }


def popularity_rank() -> list[dict]:
    """Return all snapshots sorted by popularity score descending."""
    results = []
    for name in list_all_snapshots():
        score = compute_popularity(name)
        if score is not None:
            results.append(score)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def popularity_summary() -> dict:
    """Return aggregate popularity statistics."""
    ranked = popularity_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "top": None}
    totals = [r["total"] for r in ranked]
    return {
        "count": len(ranked),
        "average": round(sum(totals) / len(totals), 2),
        "top": ranked[0]["name"] if ranked else None,
    }
