"""Snapshot complexity scoring based on env structure."""

from stashrun.snapshot import get_snapshot
from stashrun.tags import get_tags


def compute_complexity(name: str) -> dict | None:
    """Compute a complexity report for a snapshot."""
    env = get_snapshot(name)
    if env is None:
        return None

    key_count = len(env)
    avg_value_len = (
        sum(len(v) for v in env.values()) / key_count if key_count else 0
    )
    long_values = [k for k, v in env.items() if len(v) > 100]
    prefixes = {k.split("_")[0] for k in env if "_" in k}
    tags = get_tags(name)

    score = (
        key_count * 2
        + int(avg_value_len)
        + len(long_values) * 5
        + len(prefixes)
        + len(tags)
    )

    return {
        "name": name,
        "key_count": key_count,
        "avg_value_length": round(avg_value_len, 2),
        "long_value_keys": long_values,
        "prefix_count": len(prefixes),
        "tag_count": len(tags),
        "score": score,
    }


def complexity_rank(names: list[str]) -> list[dict]:
    """Return snapshots sorted by complexity score descending."""
    results = [compute_complexity(n) for n in names]
    valid = [r for r in results if r is not None]
    return sorted(valid, key=lambda r: r["score"], reverse=True)


def complexity_summary(names: list[str]) -> dict:
    """Aggregate complexity stats across multiple snapshots."""
    ranked = complexity_rank(names)
    if not ranked:
        return {"count": 0, "avg_score": 0, "max_score": 0, "min_score": 0}
    scores = [r["score"] for r in ranked]
    return {
        "count": len(ranked),
        "avg_score": round(sum(scores) / len(scores), 2),
        "max_score": max(scores),
        "min_score": min(scores),
    }
