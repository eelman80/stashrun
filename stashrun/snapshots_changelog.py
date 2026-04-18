"""Track a human-readable changelog entry per snapshot."""

import json
from pathlib import Path
from typing import Optional
from stashrun.storage import get_stash_dir


def _changelog_path() -> Path:
    return get_stash_dir() / "changelog.json"


def _load_changelog() -> dict:
    p = _changelog_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_changelog(data: dict) -> None:
    _changelog_path().write_text(json.dumps(data, indent=2))


def set_changelog(name: str, message: str) -> None:
    """Set a changelog message for a snapshot."""
    data = _load_changelog()
    data[name] = message
    _save_changelog(data)


def get_changelog(name: str) -> Optional[str]:
    """Return the changelog message for a snapshot, or None."""
    return _load_changelog().get(name)


def remove_changelog(name: str) -> bool:
    """Remove the changelog entry for a snapshot. Returns True if removed."""
    data = _load_changelog()
    if name in data:
        del data[name]
        _save_changelog(data)
        return True
    return False


def list_changelogs() -> dict:
    """Return all changelog entries as a dict."""
    return _load_changelog()


def clear_changelogs() -> int:
    """Remove all changelog entries. Returns count removed."""
    data = _load_changelog()
    count = len(data)
    _save_changelog({})
    return count
