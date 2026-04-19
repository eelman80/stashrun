"""Composite scoring for snapshots combining health, confidence, reputation, and impact."""

from typing import Optional


def compute_score(
    name: str,
    *,
    get_health=None,
    get_confidence=None,
    get_reputation=None,
    get_impact=None,
) -> Optional[dict]:
    """Compute a composite score (0-100) for a snapshot."""
    from stashrun.snapshots_health import compute_health
    from stashrun.snapshots_confidence import compute_confidence
    from stashrun.snapshots_reputation import compute_reputation
    from stashrun.snapshots_impact import compute_impact

    get_health = get_health or compute_health
    get_confidence = get_confidence or compute_confidence
    get_reputation = get_reputation or compute_reputation
    get_impact = get_impact or compute_impact

    health = get_health(name)
    if health is None:
        return None

    confidence = get_confidence(name) or {"score": 0}
    reputation = get_reputation(name) or {"score": 0}
    impact = get_impact(name) or {"score": 0}

    h = health.get("score", 0)
    c = confidence.get("score", 0)
    r = reputation.get("score", 0)
    i = impact.get("score", 0)

    composite = round(h * 0.4 + c * 0.3 + r * 0.2 + i * 0.1, 2)

    return {
        "name": name,
        "composite": composite,
        "health": h,
        "confidence": c,
        "reputation": r,
        "impact": i,
    }


def score_rank(names: list, **kwargs) -> list:
    """Return snapshots sorted by composite score descending."""
    results = []
    for name in names:
        s = compute_score(name, **kwargs)
        if s is not None:
            results.append(s)
    return sorted(results, key=lambda x: x["composite"], reverse=True)


def score_summary(names: list, **kwargs) -> dict:
    """Return aggregate stats across all scored snapshots."""
    ranked = score_rank(names, **kwargs)
    if not ranked:
        return {"count": 0, "average": 0.0, "top": None}
    total = sum(s["composite"] for s in ranked)
    return {
        "count": len(ranked),
        "average": round(total / len(ranked), 2),
        "top": ranked[0]["name"],
    }
