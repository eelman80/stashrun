"""Badge system for snapshots based on their attributes."""

from stashrun.snapshots_ratings import get_rating
from stashrun.pinning import is_pinned
from stashrun.snapshots_favorites import is_favorite
from stashrun.snapshots_checksums import verify_checksum
from stashrun.snapshot import get_snapshot

BADGES = {
    "verified": "Checksum verified",
    "pinned": "Pinned snapshot",
    "favorite": "Marked as favorite",
    "top_rated": "Rating 5 stars",
    "well_rated": "Rating 4+ stars",
    "large": "More than 20 keys",
    "tiny": "5 or fewer keys",
}


def compute_badges(name: str) -> list[str] | None:
    """Return list of badge keys earned by a snapshot, or None if missing."""
    env = get_snapshot(name)
    if env is None:
        return None

    earned = []

    if verify_checksum(name):
        earned.append("verified")

    if is_pinned(name):
        earned.append("pinned")

    if is_favorite(name):
        earned.append("favorite")

    rating = get_rating(name)
    if rating == 5:
        earned.append("top_rated")
    elif rating is not None and rating >= 4:
        earned.append("well_rated")

    key_count = len(env)
    if key_count > 20:
        earned.append("large")
    elif key_count <= 5:
        earned.append("tiny")

    return earned


def badge_summary(name: str) -> dict | None:
    """Return badge details with labels for a snapshot."""
    badges = compute_badges(name)
    if badges is None:
        return None
    return {b: BADGES[b] for b in badges}


def snapshots_with_badge(badge: str, names: list[str]) -> list[str]:
    """Return subset of names that have earned the given badge."""
    result = []
    for name in names:
        badges = compute_badges(name)
        if badges and badge in badges:
            result.append(name)
    return result
