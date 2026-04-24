"""Snapshot similarity scoring based on shared keys and values."""

from stashrun.snapshot import get_snapshot
from stashrun.storage import list_snapshots


def compute_similarity(name_a: str, name_b: str) -> dict | None:
    """Compute similarity metrics between two snapshots."""
    env_a = get_snapshot(name_a)
    env_b = get_snapshot(name_b)
    if env_a is None or env_b is None:
        return None

    keys_a = set(env_a.keys())
    keys_b = set(env_b.keys())
    shared_keys = keys_a & keys_b
    all_keys = keys_a | keys_b

    key_overlap = len(shared_keys) / len(all_keys) if all_keys else 1.0

    matching_values = sum(
        1 for k in shared_keys if env_a[k] == env_b[k]
    )
    value_overlap = matching_values / len(shared_keys) if shared_keys else 0.0

    score = round((key_overlap * 0.5 + value_overlap * 0.5) * 100, 2)

    return {
        "snapshot_a": name_a,
        "snapshot_b": name_b,
        "shared_keys": sorted(shared_keys),
        "key_overlap": round(key_overlap, 4),
        "value_overlap": round(value_overlap, 4),
        "score": score,
    }


def find_similar(name: str, threshold: float = 50.0) -> list[dict]:
    """Find all snapshots similar to the given one above a score threshold."""
    all_names = list_snapshots()
    results = []
    for other in all_names:
        if other == name:
            continue
        result = compute_similarity(name, other)
        if result and result["score"] >= threshold:
            results.append(result)
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def similarity_matrix(names: list[str]) -> list[dict]:
    """Compute pairwise similarity for a list of snapshot names."""
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            result = compute_similarity(a, b)
            if result:
                pairs.append(result)
    pairs.sort(key=lambda r: r["score"], reverse=True)
    return pairs
