"""Snapshot key coverage analysis — measures how well a snapshot covers a reference key set."""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot, list_all_snapshots


def compute_coverage(
    name: str,
    reference_keys: list[str],
) -> Optional[dict]:
    """Return coverage metrics for a snapshot against a reference key set.

    Returns None if the snapshot does not exist or reference_keys is empty.
    """
    env = get_snapshot(name)
    if env is None:
        return None
    if not reference_keys:
        return None

    ref_set = set(reference_keys)
    snapshot_keys = set(env.keys())

    covered = ref_set & snapshot_keys
    missing = ref_set - snapshot_keys
    extra = snapshot_keys - ref_set

    coverage_pct = round(len(covered) / len(ref_set) * 100, 2)

    return {
        "name": name,
        "total_reference": len(ref_set),
        "covered": sorted(covered),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "coverage_pct": coverage_pct,
    }


def coverage_rank(
    reference_keys: list[str],
    names: Optional[list[str]] = None,
) -> list[dict]:
    """Rank all (or given) snapshots by coverage percentage descending."""
    if names is None:
        names = list_all_snapshots()

    results = []
    for name in names:
        result = compute_coverage(name, reference_keys)
        if result is not None:
            results.append(result)

    results.sort(key=lambda r: r["coverage_pct"], reverse=True)
    return results


def coverage_summary(reference_keys: list[str]) -> dict:
    """Return aggregate coverage statistics across all snapshots."""
    ranked = coverage_rank(reference_keys)
    if not ranked:
        return {"count": 0, "avg_coverage_pct": 0.0, "full_coverage": 0}

    avg = round(sum(r["coverage_pct"] for r in ranked) / len(ranked), 2)
    full = sum(1 for r in ranked if r["coverage_pct"] == 100.0)

    return {
        "count": len(ranked),
        "avg_coverage_pct": avg,
        "full_coverage": full,
    }
