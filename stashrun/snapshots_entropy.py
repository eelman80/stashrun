"""Snapshot entropy scoring — measures unpredictability/randomness of env values."""

from __future__ import annotations

import math
from collections import Counter
from typing import Optional

from stashrun.snapshot import get_snapshot
from stashrun.storage import list_snapshots


def _char_entropy(value: str) -> float:
    """Compute Shannon entropy (bits) of a string's character distribution."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def compute_entropy(name: str) -> Optional[dict]:
    """Return an entropy report for a snapshot's env values.

    Returns None if the snapshot does not exist.
    Keys in the report:
      - mean_entropy: average Shannon entropy across all values
      - max_entropy:  highest single-value entropy
      - high_entropy_keys: list of keys whose entropy exceeds threshold (4.0 bits)
      - score: 0-100 normalised score (higher = more random/unpredictable values)
    """
    env = get_snapshot(name)
    if env is None:
        return None

    if not env:
        return {"mean_entropy": 0.0, "max_entropy": 0.0, "high_entropy_keys": [], "score": 0}

    entropies = {k: _char_entropy(v) for k, v in env.items()}
    mean_e = sum(entropies.values()) / len(entropies)
    max_e = max(entropies.values())
    threshold = 4.0
    high_keys = [k for k, e in entropies.items() if e >= threshold]

    # Normalise: treat 6.0 bits as ceiling for score=100
    score = min(100, round((mean_e / 6.0) * 100))

    return {
        "mean_entropy": round(mean_e, 4),
        "max_entropy": round(max_e, 4),
        "high_entropy_keys": sorted(high_keys),
        "score": score,
    }


def entropy_rank() -> list[tuple[str, int]]:
    """Return all snapshots ranked by entropy score (descending)."""
    results = []
    for name in list_snapshots():
        report = compute_entropy(name)
        if report is not None:
            results.append((name, report["score"]))
    return sorted(results, key=lambda x: x[1], reverse=True)


def entropy_summary() -> dict:
    """Return aggregate entropy statistics across all snapshots."""
    ranked = entropy_rank()
    if not ranked:
        return {"total": 0, "average_score": 0, "top": None}
    scores = [s for _, s in ranked]
    return {
        "total": len(scores),
        "average_score": round(sum(scores) / len(scores), 2),
        "top": ranked[0][0] if ranked else None,
    }
