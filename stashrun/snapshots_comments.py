"""Per-key inline comments for snapshots."""
from __future__ import annotations
import json
from pathlib import Path
from stashrun.storage import get_stash_dir


def _comments_path() -> Path:
    return get_stash_dir() / "comments.json"


def _load_comments() -> dict:
    p = _comments_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_comments(data: dict) -> None:
    _comments_path().write_text(json.dumps(data, indent=2))


def set_comment(snapshot: str, key: str, comment: str) -> None:
    """Attach a comment to a specific key in a snapshot."""
    data = _load_comments()
    data.setdefault(snapshot, {})[key] = comment
    _save_comments(data)


def get_comment(snapshot: str, key: str) -> str | None:
    """Return the comment for a key, or None."""
    return _load_comments().get(snapshot, {}).get(key)


def remove_comment(snapshot: str, key: str) -> bool:
    data = _load_comments()
    if snapshot in data and key in data[snapshot]:
        del data[snapshot][key]
        if not data[snapshot]:
            del data[snapshot]
        _save_comments(data)
        return True
    return False


def get_all_comments(snapshot: str) -> dict[str, str]:
    """Return all key->comment mappings for a snapshot."""
    return dict(_load_comments().get(snapshot, {}))


def clear_comments(snapshot: str) -> int:
    """Remove all comments for a snapshot. Returns count removed."""
    data = _load_comments()
    count = len(data.pop(snapshot, {}))
    _save_comments(data)
    return count
