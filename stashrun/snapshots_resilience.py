"""Compute resilience score for snapshots.

Resilience measures how well a snapshot is protected and recoverable:
- Has encryption (+25)
- Has checksum and it's valid (+20)
- Is pinned (+15)
- Has a version history (+20, capped at 3 versions)
- Has a backup/retention policy (+20)
"""

from typing import Optional
from stashrun.snapshot import get_snapshot, list_all_snapshots
from stashrun.encrypted_snapshot import is_snapshot_encrypted
from stashrun.snapshots_checksums import get_checksum, verify_checksum
from stashrun.pinning import is_pinned
from stashrun.snapshots_versioning import list_versions
from stashrun.snapshots_retention import get_retention


def compute_resilience(name: str) -> Optional[dict]:
    """Return a resilience breakdown dict, or None if snapshot missing."""
    env = get_snapshot(name)
    if env is None:
        return None

    score = 0
    details = {}

    encrypted = is_snapshot_encrypted(name)
    details["encrypted"] = encrypted
    if encrypted:
        score += 25

    checksum = get_checksum(name)
    if checksum is not None:
        valid = verify_checksum(name)
        details["checksum"] = "valid" if valid else "invalid"
        score += 20 if valid else 5
    else:
        details["checksum"] = "missing"

    pinned = is_pinned(name)
    details["pinned"] = pinned
    if pinned:
        score += 15

    versions = list_versions(name)
    version_count = len(versions)
    version_score = min(version_count, 3) * (20 // 3)
    details["versions"] = version_count
    score += version_score

    retention = get_retention(name)
    details["retention_policy"] = retention.get("policy") if retention else None
    if retention:
        score += 20

    return {"score": min(score, 100), "details": details}


def resilience_rank() -> list:
    """Return all snapshots sorted by resilience score descending."""
    results = []
    for name in list_all_snapshots():
        r = compute_resilience(name)
        if r is not None:
            results.append((name, r["score"]))
    return sorted(results, key=lambda x: x[1], reverse=True)


def resilience_summary() -> dict:
    """Return aggregate resilience stats across all snapshots."""
    scores = []
    for name in list_all_snapshots():
        r = compute_resilience(name)
        if r is not None:
            scores.append(r["score"])
    if not scores:
        return {"count": 0, "average": 0, "min": 0, "max": 0}
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 2),
        "min": min(scores),
        "max": max(scores),
    }
