"""Maturity index: aggregate score combining maturity, lifecycle, status, and versioning."""

from stashrun.snapshot import get_snapshot
from stashrun.snapshots_maturity import get_maturity
from stashrun.snapshots_lifecycle import get_lifecycle
from stashrun.snapshots_status import get_status
from stashrun.snapshots_versioning import list_versions
from stashrun.storage import list_snapshots

_MATURITY_WEIGHTS = {
    "experimental": 0,
    "alpha": 20,
    "beta": 50,
    "stable": 80,
    "deprecated": 30,
}

_LIFECYCLE_WEIGHTS = {
    "draft": 0,
    "active": 30,
    "archived": 10,
    "retired": 5,
}

_STATUS_WEIGHTS = {
    "unknown": 0,
    "pending": 10,
    "ready": 30,
    "stale": 5,
    "broken": 0,
}


def compute_maturity_index(name: str) -> dict | None:
    """Return a maturity index dict for the named snapshot, or None if missing."""
    if get_snapshot(name) is None:
        return None

    maturity = get_maturity(name, default="experimental")
    lifecycle = get_lifecycle(name, default="draft")
    status = get_status(name, default="unknown")
    versions = list_versions(name)
    version_count = len(versions)

    maturity_score = _MATURITY_WEIGHTS.get(maturity, 0)
    lifecycle_score = _LIFECYCLE_WEIGHTS.get(lifecycle, 0)
    status_score = _STATUS_WEIGHTS.get(status, 0)
    version_score = min(version_count * 5, 20)

    total = maturity_score + lifecycle_score + status_score + version_score

    return {
        "name": name,
        "maturity": maturity,
        "lifecycle": lifecycle,
        "status": status,
        "version_count": version_count,
        "maturity_score": maturity_score,
        "lifecycle_score": lifecycle_score,
        "status_score": status_score,
        "version_score": version_score,
        "total": total,
    }


def maturity_index_rank() -> list[dict]:
    """Return all snapshots ranked by maturity index descending."""
    results = []
    for name in list_snapshots():
        entry = compute_maturity_index(name)
        if entry is not None:
            results.append(entry)
    return sorted(results, key=lambda x: x["total"], reverse=True)


def maturity_index_summary() -> dict:
    """Return aggregate stats across all snapshots."""
    ranked = maturity_index_rank()
    if not ranked:
        return {"count": 0, "average": 0.0, "top": None}
    total_sum = sum(e["total"] for e in ranked)
    return {
        "count": len(ranked),
        "average": round(total_sum / len(ranked), 2),
        "top": ranked[0]["name"] if ranked else None,
    }
