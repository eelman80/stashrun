"""Volatility analysis: measures how frequently a snapshot's env changes over time."""

from __future__ import annotations

from typing import Optional

from stashrun.snapshots_versioning import list_versions
from stashrun.snapshot import get_snapshot
from stashrun.snapshots_access import get_access_count


def compute_volatility(name: str) -> Optional[dict]:
    """Compute a volatility profile for a snapshot.

    Returns a dict with:
      - version_count: number of stored versions
      - key_churn: average number of keys that differ between consecutive versions
      - access_count: total recorded accesses
      - volatility_score: 0-100 composite score (higher = more volatile)
    Returns None if snapshot does not exist.
    """
    env = get_snapshot(name)
    if env is None:
        return None

    versions = list_versions(name)  # list of {version, env, saved_at}
    version_count = len(versions)

    # Compute average key churn across consecutive version pairs
    churn_total = 0
    pairs = 0
    for i in range(1, len(versions)):
        prev_env = versions[i - 1].get("env", {})
        curr_env = versions[i].get("env", {})
        all_keys = set(prev_env) | set(curr_env)
        changed = sum(
            1 for k in all_keys if prev_env.get(k) != curr_env.get(k)
        )
        if all_keys:
            churn_total += changed / len(all_keys)
            pairs += 1

    key_churn = round(churn_total / pairs, 4) if pairs > 0 else 0.0

    access_count = get_access_count(name) or 0

    # Score: version churn (up to 60) + access frequency (up to 40)
    version_score = min(version_count * 6, 60)
    churn_score = round(key_churn * 30)
    access_score = min(access_count * 2, 40)
    volatility_score = min(version_score + churn_score + access_score, 100)

    return {
        "name": name,
        "version_count": version_count,
        "key_churn": key_churn,
        "access_count": access_count,
        "volatility_score": volatility_score,
    }


def volatility_rank(names: list[str]) -> list[dict]:
    """Return snapshots sorted by volatility_score descending."""
    results = [r for n in names if (r := compute_volatility(n)) is not None]
    return sorted(results, key=lambda x: x["volatility_score"], reverse=True)


def volatility_summary(names: list[str]) -> dict:
    """Aggregate volatility stats across a list of snapshot names."""
    profiles = [r for n in names if (r := compute_volatility(n)) is not None]
    if not profiles:
        return {"count": 0, "avg_score": 0.0, "max_score": 0, "min_score": 0}
    scores = [p["volatility_score"] for p in profiles]
    return {
        "count": len(profiles),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "min_score": min(scores),
    }
