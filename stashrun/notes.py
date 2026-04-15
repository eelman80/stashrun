"""Snapshot notes — attach and retrieve human-readable notes for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir


def _notes_path() -> Path:
    return get_stash_dir() / "notes.json"


def _load_notes() -> dict[str, str]:
    path = _notes_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_notes(notes: dict[str, str]) -> None:
    path = _notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2), encoding="utf-8")


def set_note(snapshot_name: str, note: str) -> None:
    """Attach or overwrite a note for *snapshot_name*."""
    notes = _load_notes()
    notes[snapshot_name] = note
    _save_notes(notes)


def get_note(snapshot_name: str) -> Optional[str]:
    """Return the note for *snapshot_name*, or ``None`` if absent."""
    return _load_notes().get(snapshot_name)


def remove_note(snapshot_name: str) -> bool:
    """Remove the note for *snapshot_name*. Returns ``True`` if it existed."""
    notes = _load_notes()
    if snapshot_name not in notes:
        return False
    del notes[snapshot_name]
    _save_notes(notes)
    return True


def list_notes() -> dict[str, str]:
    """Return all snapshot-name → note mappings."""
    return dict(_load_notes())


def rename_note(old_name: str, new_name: str) -> bool:
    """Move a note from *old_name* to *new_name*. Returns ``True`` on success."""
    notes = _load_notes()
    if old_name not in notes:
        return False
    notes[new_name] = notes.pop(old_name)
    _save_notes(notes)
    return True
