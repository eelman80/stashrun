"""Snapshot ratings: allow users to rate snapshots 1-5."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _ratings_path() -> Path:
    return get_stash_dir() / "ratings.json"


def _load_ratings() -> dict:
    p = _ratings_path()
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_ratings(data: dict) -> None:
    with open(_ratings_path(), "w") as f:
        json.dump(data, f, indent=2)


def set_rating(name: str, rating: int) -> bool:
    """Set a 1-5 star rating for a snapshot. Returns False if rating out of range."""
    if not (1 <= rating <= 5):
        return False
    data = _load_ratings()
    data[name] = rating
    _save_ratings(data)
    return True


def get_rating(name: str) -> int | None:
    """Return the rating for a snapshot, or None if unrated."""
    return _load_ratings().get(name)


def remove_rating(name: str) -> bool:
    """Remove a snapshot's rating. Returns False if not found."""
    data = _load_ratings()
    if name not in data:
        return False
    del data[name]
    _save_ratings(data)
    return True


def list_ratings() -> dict:
    """Return all snapshot ratings."""
    return _load_ratings()


def top_rated(n: int = 5) -> list[tuple[str, int]]:
    """Return top-n rated snapshots sorted by rating descending."""
    data = _load_ratings()
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return sorted_items[:n]
