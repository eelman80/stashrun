"""Drift detection for snapshots.

Measures how much a snapshot has drifted from a reference point (another
snapshot, a template, or the live environment). Drift is expressed as a
normalised score in [0, 100] where 0 means identical and 100 means completely
different.
"""

from __future__ import annotations

from typing import Optional

from stashrun.snapshot import get_snapshot, list_all_snapshots
from stashrun.env import capture_env
from stashrun.diff import compare_dicts


def compute_drift(
    name: str,
    reference: Optional[str] = None,
    *,
    live: bool = False,
) -> Optional[dict]:
    """Compute drift between *name* and a reference.

    Parameters
    ----------
    name:
        Snapshot to evaluate.
    reference:
        Name of the reference snapshot.  Mutually exclusive with *live*.
    live:
        When ``True``, compare against the current live environment instead of
        another snapshot.

    Returns
    -------
    A dict with keys ``added``, ``removed``, ``changed``, ``unchanged``,
    ``total_reference``, ``total_snapshot``, and ``score`` (0-100), or
    ``None`` if the snapshot does not exist.
    """
    env = get_snapshot(name)
    if env is None:
        return None

    if live:
        ref_env = capture_env()
    elif reference:
        ref_env = get_snapshot(reference)
        if ref_env is None:
            return None
    else:
        # Default: compare against live environment
        ref_env = capture_env()

    diff = compare_dicts(ref_env, env)

    total_keys = max(
        len(ref_env),
        len(env),
        1,  # avoid division by zero
    )
    changed_count = len(diff.added) + len(diff.removed) + len(diff.changed)
    score = min(100, round(changed_count / total_keys * 100))

    return {
        "snapshot": name,
        "reference": reference or "<live>",
        "added": diff.added,
        "removed": diff.removed,
        "changed": diff.changed,
        "unchanged": diff.unchanged,
        "total_reference": len(ref_env),
        "total_snapshot": len(env),
        "score": score,
    }


def drift_rank(reference: Optional[str] = None, *, live: bool = False) -> list[dict]:
    """Return all snapshots ranked by drift score (highest first).

    Parameters
    ----------
    reference:
        Reference snapshot name.  When omitted (and *live* is ``False``) the
        live environment is used.
    live:
        Compare each snapshot against the live environment.
    """
    results = []
    for name in list_all_snapshots():
        result = compute_drift(name, reference=reference, live=live)
        if result is not None:
            results.append(result)
    return sorted(results, key=lambda r: r["score"], reverse=True)


def drift_summary(reference: Optional[str] = None, *, live: bool = False) -> dict:
    """Return aggregate drift statistics across all snapshots."""
    ranked = drift_rank(reference=reference, live=live)
    if not ranked:
        return {"count": 0, "avg_score": 0, "max_score": 0, "min_score": 0}

    scores = [r["score"] for r in ranked]
    return {
        "count": len(scores),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "min_score": min(scores),
    }
