"""Snapshot health scoring based on multiple quality signals."""

from stashrun.snapshots_checksums import get_checksum, compute_checksum
from stashrun.snapshots_validate import validate_snapshot
from stashrun.snapshot import get_snapshot
from stashrun.storage import list_snapshots
from stashrun.notes import get_note
from stashrun.snapshots_ttl import get_ttl
import time


def compute_health(name: str) -> dict | None:
    """Compute a health report for a snapshot."""
    env = get_snapshot(name)
    if env is None:
        return None

    issues = []
    score = 100

    # Check checksum integrity
    stored = get_checksum(name)
    if stored is None:
        issues.append("no checksum stored")
        score -= 20
    else:
        current = compute_checksum(env)
        if current != stored:
            issues.append("checksum mismatch — env may have been tampered")
            score -= 40

    # Check for empty values
    empty_keys = [k for k, v in env.items() if not v]
    if empty_keys:
        issues.append(f"{len(empty_keys)} key(s) with empty values")
        score -= 10

    # Check for note/documentation
    if not get_note(name):
        issues.append("no note attached")
        score -= 5

    # Check TTL expiry
    ttl = get_ttl(name)
    if ttl and ttl < time.time():
        issues.append("snapshot has expired (TTL passed)")
        score -= 15

    # Validate key naming
    validation = validate_snapshot(name)
    bad_keys = validation.get("key_pattern", [])
    if bad_keys:
        issues.append(f"{len(bad_keys)} key(s) fail naming convention")
        score -= 10

    score = max(0, score)
    return {
        "name": name,
        "score": score,
        "status": "healthy" if score >= 80 else "degraded" if score >= 50 else "unhealthy",
        "issues": issues,
    }


def health_summary() -> list[dict]:
    """Return health reports for all snapshots, sorted by score ascending."""
    reports = []
    for name in list_snapshots():
        report = compute_health(name)
        if report:
            reports.append(report)
    return sorted(reports, key=lambda r: r["score"])
