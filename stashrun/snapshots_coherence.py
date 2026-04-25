"""Coherence scoring: measures internal consistency of a snapshot's env vars."""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot
from stashrun.snapshots_checksums import verify_checksum
from stashrun.snapshots_validate import validate_key_pattern, validate_value_nonempty
from stashrun.snapshots_permissions import get_permissions
from stashrun.snapshots_status import get_status
from stashrun.storage import list_snapshots

_KEY_PATTERN = r"^[A-Z][A-Z0-9_]*$"


def compute_coherence(name: str) -> Optional[dict]:
    """Return a coherence report for *name*, or None if the snapshot is missing."""
    env = get_snapshot(name)
    if env is None:
        return None

    score = 100
    issues: list[str] = []

    # -20 if any keys violate the conventional uppercase pattern
    bad_keys = validate_key_pattern(name, _KEY_PATTERN)
    if bad_keys:
        score -= 20
        issues.append(f"{len(bad_keys)} key(s) violate naming convention")

    # -20 if any values are empty
    empty_vals = validate_value_nonempty(name)
    if empty_vals:
        score -= 20
        issues.append(f"{len(empty_vals)} empty value(s) found")

    # -20 if checksum does not match
    checksum_ok = verify_checksum(name)
    if checksum_ok is False:
        score -= 20
        issues.append("checksum mismatch")

    # -20 if status is 'deprecated' or 'archived'
    status = get_status(name)
    if status in ("deprecated", "archived"):
        score -= 20
        issues.append(f"status is '{status}'")

    # -20 if read permission is explicitly revoked
    perms = get_permissions(name)
    if not perms.get("read", True):
        score -= 20
        issues.append("read permission revoked")

    score = max(0, score)
    return {"name": name, "score": score, "issues": issues}


def coherence_rank() -> list[dict]:
    """Return all snapshots sorted by coherence score descending."""
    results = []
    for name in list_snapshots():
        report = compute_coherence(name)
        if report is not None:
            results.append(report)
    return sorted(results, key=lambda r: r["score"], reverse=True)


def coherence_summary() -> dict:
    """Aggregate coherence statistics across all snapshots."""
    ranked = coherence_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "perfect": 0, "degraded": 0}
    scores = [r["score"] for r in ranked]
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 2),
        "perfect": sum(1 for s in scores if s == 100),
        "degraded": sum(1 for s in scores if s < 60),
    }
