"""Archive and unarchive snapshots (soft-delete with recovery)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir, load_snapshot, save_snapshot, list_snapshots


def _archive_path() -> Path:
    p = get_stash_dir() / "archive.json"
    if not p.exists():
        p.write_text("{}")
    return p


def _load_archive() -> dict:
    return json.loads(_archive_path().read_text())


def _save_archive(data: dict) -> None:
    _archive_path().write_text(json.dumps(data, indent=2))


def archive_snapshot(name: str) -> bool:
    """Move a snapshot into the archive store. Returns True on success."""
    env = load_snapshot(name)
    if env is None:
        return False
    archive = _load_archive()
    archive[name] = env
    _save_archive(archive)
    # Remove from active storage by saving a tombstone marker
    snap_file = get_stash_dir() / f"{name}.json"
    if snap_file.exists():
        snap_file.unlink()
    return True


def unarchive_snapshot(name: str) -> bool:
    """Restore a snapshot from the archive back to active storage."""
    archive = _load_archive()
    if name not in archive:
        return False
    save_snapshot(name, archive.pop(name))
    _save_archive(archive)
    return True


def list_archived() -> list[str]:
    """Return names of all archived snapshots."""
    return list(_load_archive().keys())


def get_archived(name: str) -> dict | None:
    """Return the env dict for an archived snapshot, or None."""
    return _load_archive().get(name)


def purge_archived(name: str) -> bool:
    """Permanently delete an archived snapshot."""
    archive = _load_archive()
    if name not in archive:
        return False
    del archive[name]
    _save_archive(archive)
    return True
