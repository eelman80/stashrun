"""Compute a 'readiness' score for snapshots.

Readiness reflects how prepared a snapshot is for production use,
based on ownership, status, permissions, validation, and lifecycle.
"""

from stashrun.snapshot import get_snapshot
from stashrun.snapshots_ownership import get_owner
from stashrun.snapshots_status import get_status
from stashrun.snapshots_permissions import get_permissions
from stashrun.snapshots_lifecycle import get_lifecycle
from stashrun.snapshots_checksums import get_checksum, compute_checksum
from stashrun.list_snapshots import list_all_snapshots  # noqa: F401 – resolved at runtime
from stashrun.snapshot import list_all_snapshots

_LIFECYCLE_READY = {"stable", "production", "released"}
_STATUS_READY = {"active", "approved", "ready"}


def compute_readiness(name: str) -> dict | None:
    """Return a readiness breakdown for *name*, or None if missing."""
    env = get_snapshot(name)
    if env is None:
        return None

    score = 0
    details: dict[str, object] = {}

    # Owner present (+20)
    owner = get_owner(name)
    details["has_owner"] = owner is not None
    if owner:
        score += 20

    # Status is production-ready (+20)
    status = get_status(name, default="unknown")
    details["status"] = status
    if status in _STATUS_READY:
        score += 20

    # Lifecycle is stable/production (+20)
    lifecycle = get_lifecycle(name, default="unknown")
    details["lifecycle"] = lifecycle
    if lifecycle in _LIFECYCLE_READY:
        score += 20

    # Checksum present and valid (+25)
    stored = get_checksum(name)
    if stored is not None:
        live = compute_checksum(env)
        details["checksum_valid"] = stored == live
        if stored == live:
            score += 25
        else:
            score += 5  # exists but stale
    else:
        details["checksum_valid"] = None

    # Permissions not restricted (+15)
    perms = get_permissions(name)
    all_open = all(perms.get(p, True) for p in ("read", "write", "delete"))
    details["permissions_open"] = all_open
    if all_open:
        score += 15

    details["score"] = min(score, 100)
    return details


def readiness_rank(names: list[str] | None = None) -> list[tuple[str, int]]:
    """Return snapshots sorted by readiness score descending."""
    if names is None:
        names = list_all_snapshots()
    ranked = []
    for n in names:
        r = compute_readiness(n)
        if r is not None:
            ranked.append((n, r["score"]))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def readiness_summary(names: list[str] | None = None) -> dict:
    """Return aggregate readiness statistics."""
    if names is None:
        names = list_all_snapshots()
    scores = [compute_readiness(n)["score"] for n in names if compute_readiness(n)]
    if not scores:
        return {"count": 0, "average": 0, "max": 0, "min": 0}
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 2),
        "max": max(scores),
        "min": min(scores),
    }
