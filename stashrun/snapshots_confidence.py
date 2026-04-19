"""Confidence scoring for snapshots based on multiple quality signals."""

from stashrun.snapshots_checksums import get_checksum, verify_checksum
from stashrun.snapshots_ratings import get_rating
from stashrun.snapshots_validate import validate_snapshot
from stashrun.snapshot import get_snapshot

DEFAULT_WEIGHTS = {
    "checksum_valid": 30,
    "rating": 20,
    "no_empty_values": 20,
    "has_keys": 15,
    "checksum_exists": 15,
}


def compute_confidence(name: str, weights: dict = None) -> dict | None:
    """Return a confidence breakdown dict for a snapshot, or None if missing."""
    env = get_snapshot(name)
    if env is None:
        return None

    w = weights or DEFAULT_WEIGHTS
    score = 0
    breakdown = {}

    # checksum exists
    cs = get_checksum(name)
    breakdown["checksum_exists"] = bool(cs)
    if cs:
        score += w.get("checksum_exists", 0)

    # checksum valid
    valid_cs = verify_checksum(name) if cs else False
    breakdown["checksum_valid"] = valid_cs
    if valid_cs:
        score += w.get("checksum_valid", 0)

    # rating (normalised to 0-1 scale, max rating 5)
    rating = get_rating(name)
    if rating is not None:
        normalised = rating / 5.0
        contribution = int(w.get("rating", 0) * normalised)
        breakdown["rating"] = rating
        score += contribution
    else:
        breakdown["rating"] = None

    # no empty values
    issues = validate_snapshot(name, check_nonempty=True)
    no_empty = not any(i["check"] == "nonempty" for i in issues)
    breakdown["no_empty_values"] = no_empty
    if no_empty:
        score += w.get("no_empty_values", 0)

    # has keys
    has_keys = len(env) > 0
    breakdown["has_keys"] = has_keys
    if has_keys:
        score += w.get("has_keys", 0)

    breakdown["score"] = score
    breakdown["max_score"] = sum(w.values())
    breakdown["percent"] = round(score / breakdown["max_score"] * 100, 1)
    return breakdown


def confidence_rank(names: list[str]) -> list[tuple[str, float]]:
    """Return snapshots sorted by confidence percent descending."""
    results = []
    for name in names:
        info = compute_confidence(name)
        if info:
            results.append((name, info["percent"]))
    return sorted(results, key=lambda x: x[1], reverse=True)
