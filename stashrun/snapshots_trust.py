"""Trust scoring for snapshots based on ownership, permissions, checksums, and visibility."""

from stashrun.snapshots_ownership import get_owner
from stashrun.snapshots_permissions import get_permissions
from stashrun.snapshots_checksums import get_checksum, compute_checksum
from stashrun.snapshots_visibility import get_visibility
from stashrun.snapshot import get_snapshot

TRUST_LEVELS = ["untrusted", "low", "medium", "high", "verified"]


def compute_trust(name: str) -> dict | None:
    """Compute a trust score (0-100) for a snapshot."""
    env = get_snapshot(name)
    if env is None:
        return None

    score = 0
    breakdown = {}

    # Owner assigned: +20
    owner = get_owner(name)
    owner_score = 20 if owner else 0
    breakdown["owner"] = owner_score
    score += owner_score

    # Checksum present and valid: +30
    stored = get_checksum(name)
    if stored:
        current = compute_checksum(env)
        checksum_score = 30 if stored == current else 10
    else:
        checksum_score = 0
    breakdown["checksum"] = checksum_score
    score += checksum_score

    # Visibility is restricted (internal/private): +20
    visibility = get_visibility(name)
    vis_score = 20 if visibility in ("private", "internal") else 5
    breakdown["visibility"] = vis_score
    score += vis_score

    # Permissions are restrictive (not all true): +15
    perms = get_permissions(name)
    all_open = all(perms.get(k, True) for k in ("read", "write", "delete"))
    perm_score = 5 if all_open else 15
    breakdown["permissions"] = perm_score
    score += perm_score

    # Non-empty env: +15
    env_score = 15 if env else 0
    breakdown["env_present"] = env_score
    score += env_score

    level = trust_level(score)
    return {"score": score, "level": level, "breakdown": breakdown}


def trust_level(score: int) -> str:
    if score >= 90:
        return "verified"
    elif score >= 70:
        return "high"
    elif score >= 45:
        return "medium"
    elif score >= 20:
        return "low"
    return "untrusted"


def trust_rank(names: list[str]) -> list[tuple[str, int]]:
    """Return snapshots sorted by trust score descending."""
    results = []
    for name in names:
        result = compute_trust(name)
        if result:
            results.append((name, result["score"]))
    return sorted(results, key=lambda x: x[1], reverse=True)


def trust_summary(names: list[str]) -> dict:
    """Return count of snapshots per trust level."""
    counts = {level: 0 for level in TRUST_LEVELS}
    for name in names:
        result = compute_trust(name)
        if result:
            counts[result["level"]] += 1
    return counts
