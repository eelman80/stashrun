"""Snapshot alignment: measure how well a snapshot aligns with a reference profile or template."""

from stashrun.snapshot import get_snapshot
from stashrun.templates import get_template
from stashrun.storage import list_snapshots


def compute_alignment(name: str, reference: str) -> dict | None:
    """Compute alignment score between a snapshot and a reference template.

    Returns a dict with keys: score (0-100), matched, missing, extra.
    Returns None if the snapshot or template is missing.
    """
    env = get_snapshot(name)
    if env is None:
        return None

    tmpl = get_template(reference)
    if tmpl is None:
        return None

    ref_keys = set(tmpl.get("defaults", {}).keys())
    snap_keys = set(env.keys())

    if not ref_keys:
        return None

    matched = ref_keys & snap_keys
    missing = ref_keys - snap_keys
    extra = snap_keys - ref_keys

    score = int(len(matched) / len(ref_keys) * 100)

    return {
        "score": score,
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }


def alignment_rank(reference: str, top: int = 10) -> list[tuple[str, int]]:
    """Rank all snapshots by alignment score against a reference template."""
    results = []
    for name in list_snapshots():
        result = compute_alignment(name, reference)
        if result is not None:
            results.append((name, result["score"]))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top]


def alignment_summary(reference: str) -> dict:
    """Summarise alignment scores for all snapshots against a template."""
    scores = [score for _, score in alignment_rank(reference, top=9999)]
    if not scores:
        return {"count": 0, "average": 0, "min": 0, "max": 0}
    return {
        "count": len(scores),
        "average": round(sum(scores) / len(scores), 1),
        "min": min(scores),
        "max": max(scores),
    }
