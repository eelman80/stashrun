"""Snapshot versioning: track multiple versions of a named snapshot."""

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir, load_snapshot, save_snapshot


def _versions_path() -> Path:
    return get_stash_dir() / "versions.json"


def _load_versions() -> dict:
    p = _versions_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_versions(data: dict) -> None:
    _versions_path().write_text(json.dumps(data, indent=2))


def push_version(name: str) -> Optional[int]:
    """Push current snapshot as a new version. Returns new version number or None."""
    env = load_snapshot(name)
    if env is None:
        return None
    data = _load_versions()
    versions = data.get(name, [])
    versions.append(env)
    data[name] = versions
    _save_versions(data)
    return len(versions)


def list_versions(name: str) -> list:
    """Return list of version dicts for a snapshot name."""
    data = _load_versions()
    return data.get(name, [])


def get_version(name: str, index: int) -> Optional[dict]:
    """Get a specific version (1-based index). Returns None if not found."""
    versions = list_versions(name)
    if index < 1 or index > len(versions):
        return None
    return versions[index - 1]


def restore_version(name: str, index: int) -> bool:
    """Restore a specific version as the active snapshot. Returns True on success."""
    env = get_version(name, index)
    if env is None:
        return False
    save_snapshot(name, env)
    return True


def drop_versions(name: str) -> bool:
    """Remove all stored versions for a snapshot. Returns True if any existed."""
    data = _load_versions()
    if name not in data:
        return False
    del data[name]
    _save_versions(data)
    return True


def version_count(name: str) -> int:
    return len(list_versions(name))
