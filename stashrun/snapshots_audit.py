"""Audit trail: track who accessed or modified snapshots and when."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

_AUDIT_FILE = "audit.json"


def _audit_path() -> Path:
    return get_stash_dir() / _AUDIT_FILE


def _load_audit() -> list[dict]:
    p = _audit_path()
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_audit(entries: list[dict]) -> None:
    _audit_path().write_text(json.dumps(entries, indent=2))


def record_audit(
    action: str,
    snapshot_name: str,
    user: Optional[str] = None,
    detail: Optional[str] = None,
) -> dict:
    """Append an audit entry and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "snapshot": snapshot_name,
        "user": user or os.environ.get("USER", "unknown"),
        "detail": detail,
    }
    entries = _load_audit()
    entries.append(entry)
    _save_audit(entries)
    return entry


def get_audit_log(
    snapshot_name: Optional[str] = None,
    action: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    """Return audit entries, optionally filtered by snapshot name or action."""
    entries = _load_audit()
    if snapshot_name:
        entries = [e for e in entries if e.get("snapshot") == snapshot_name]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    if limit and limit > 0:
        entries = entries[-limit:]
    return entries


def clear_audit_log(snapshot_name: Optional[str] = None) -> int:
    """Clear all audit entries, or only those for a given snapshot. Returns count removed."""
    entries = _load_audit()
    if snapshot_name:
        kept = [e for e in entries if e.get("snapshot") != snapshot_name]
        removed = len(entries) - len(kept)
        _save_audit(kept)
    else:
        removed = len(entries)
        _save_audit([])
    return removed
