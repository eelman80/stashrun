"""Manage favorite (bookmarked) snapshots."""

from pathlib import Path
from stashrun.storage import get_stash_dir
import json


def _favorites_path() -> Path:
    return get_stash_dir() / "favorites.json"


def _load_favorites() -> list:
    p = _favorites_path()
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_favorites(favorites: list) -> None:
    _favorites_path().write_text(json.dumps(favorites, indent=2))


def add_favorite(name: str) -> bool:
    """Add a snapshot to favorites. Returns False if already present."""
    favs = _load_favorites()
    if name in favs:
        return False
    favs.append(name)
    _save_favorites(favs)
    return True


def remove_favorite(name: str) -> bool:
    """Remove a snapshot from favorites. Returns False if not found."""
    favs = _load_favorites()
    if name not in favs:
        return False
    favs.remove(name)
    _save_favorites(favs)
    return True


def list_favorites() -> list:
    """Return all favorited snapshot names."""
    return _load_favorites()


def is_favorite(name: str) -> bool:
    """Check if a snapshot is favorited."""
    return name in _load_favorites()


def clear_favorites() -> int:
    """Remove all favorites. Returns count cleared."""
    favs = _load_favorites()
    count = len(favs)
    _save_favorites([])
    return count
