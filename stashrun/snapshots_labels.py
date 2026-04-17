"""Label management for snapshots — short human-readable descriptions."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _labels_path() -> Path:
    return get_stash_dir() / "labels.json"


def _load_labels() -> dict:
    p = _labels_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_labels(data: dict) -> None:
    p = _labels_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


def set_label(name: str, label: str) -> None:
    """Attach a label to a snapshot."""
    data = _load_labels()
    data[name] = label
    _save_labels(data)


def get_label(name: str) -> str | None:
    """Return the label for a snapshot, or None if not set."""
    return _load_labels().get(name)


def remove_label(name: str) -> bool:
    """Remove the label for a snapshot. Returns True if it existed."""
    data = _load_labels()
    if name not in data:
        return False
    del data[name]
    _save_labels(data)
    return True


def list_labels() -> dict:
    """Return all snapshot -> label mappings."""
    return _load_labels()


def find_by_label(fragment: str) -> list[str]:
    """Return snapshot names whose label contains the given fragment (case-insensitive)."""
    fragment_lower = fragment.lower()
    return [
        name
        for name, label in _load_labels().items()
        if fragment_lower in label.lower()
    ]
