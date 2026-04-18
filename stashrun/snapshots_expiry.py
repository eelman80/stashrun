"""Snapshot expiry: check and purge snapshots past their TTL."""

from datetime import datetime, timezone
from typing import List

from stashrun.snapshots_ttl import get_ttl, list_ttl, remove_ttl
from stashrun.snapshot import remove_snapshot, list_all_snapshots


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def is_expired(name: str) -> bool:
    """Return True if the snapshot's TTL has passed."""
    expiry = get_ttl(name)
    if expiry is None:
        return False
    return _now_ts() >= expiry


def list_expired() -> List[str]:
    """Return names of all snapshots whose TTL has passed."""
    expired = []
    for name, expiry in list_ttl().items():
        if _now_ts() >= expiry:
            expired.append(name)
    return expired


def purge_expired(dry_run: bool = False) -> List[str]:
    """Delete all expired snapshots. Returns list of purged names.

    If dry_run is True, snapshots are not actually deleted.
    """
    expired = list_expired()
    if dry_run:
        return expired
    purged = []
    for name in expired:
        ok = remove_snapshot(name)
        if ok:
            remove_ttl(name)
            purged.append(name)
    return purged


def expiry_status(name: str) -> dict:
    """Return expiry metadata for a snapshot."""
    expiry = get_ttl(name)
    if expiry is None:
        return {"name": name, "has_ttl": False, "expired": False, "expiry_ts": None}
    expired = _now_ts() >= expiry
    return {
        "name": name,
        "has_ttl": True,
        "expired": expired,
        "expiry_ts": expiry,
        "expiry_iso": datetime.fromtimestamp(expiry, tz=timezone.utc).isoformat(),
    }
