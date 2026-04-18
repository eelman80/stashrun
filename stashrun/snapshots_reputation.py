"""Reputation scoring for snapshots based on ratings, pins, favorites, and access frequency."""

from stashrun.snapshots_ratings import get_rating
from stashrun.pinning import list_pins
from stashrun.snapshots_favorites import list_favorites
from stashrun.snapshots_access import get_access_count
from stashrun.snapshot import list_all_snapshots


def compute_reputation(name: str) -> float:
    """Compute a reputation score for a snapshot (0.0 - 100.0)."""
    score = 0.0

    rating = get_rating(name)
    if rating is not None:
        score += rating * 10  # max 50

    pins = list_pins()
    if name in pins:
        score += 20

    favorites = list_favorites()
    if name in favorites:
        score += 15

    access_count = get_access_count(name)
    score += min(access_count * 2, 15)  # max 15

    return round(min(score, 100.0), 2)


def reputation_rank(names: list[str]) -> list[tuple[str, float]]:
    """Return snapshots sorted by reputation score descending."""
    scored = [(name, compute_reputation(name)) for name in names]
    return sorted(scored, key=lambda x: x[1], reverse=True)


def top_snapshots(n: int = 5) -> list[tuple[str, float]]:
    """Return the top N snapshots by reputation."""
    all_names = list_all_snapshots()
    ranked = reputation_rank(all_names)
    return ranked[:n]


def reputation_summary(name: str) -> dict:
    """Return a breakdown of reputation components for a snapshot."""
    rating = get_rating(name)
    pinned = name in list_pins()
    favorited = name in list_favorites()
    access_count = get_access_count(name)
    total = compute_reputation(name)

    return {
        "name": name,
        "rating": rating,
        "pinned": pinned,
        "favorited": favorited,
        "access_count": access_count,
        "score": total,
    }
