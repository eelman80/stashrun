"""Category management for snapshots."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _categories_path() -> Path:
    return get_stash_dir() / "categories.json"


def _load_categories() -> dict:
    p = _categories_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_categories(data: dict) -> None:
    _categories_path().write_text(json.dumps(data, indent=2))


def set_category(name: str, category: str) -> None:
    """Assign a category to a snapshot."""
    data = _load_categories()
    data[name] = category
    _save_categories(data)


def get_category(name: str, default: str = "uncategorized") -> str:
    """Get category for a snapshot."""
    return _load_categories().get(name, default)


def remove_category(name: str) -> bool:
    """Remove category assignment for a snapshot."""
    data = _load_categories()
    if name not in data:
        return False
    del data[name]
    _save_categories(data)
    return True


def list_categories() -> dict:
    """Return all name -> category mappings."""
    return _load_categories()


def find_by_category(category: str) -> list:
    """Return snapshot names assigned to a given category."""
    return [n for n, c in _load_categories().items() if c == category]


def all_category_names() -> list:
    """Return sorted list of distinct category values in use."""
    return sorted(set(_load_categories().values()))
