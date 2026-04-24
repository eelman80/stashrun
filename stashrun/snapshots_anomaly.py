"""Anomaly detection for snapshots.

Detects unusual or suspicious patterns in snapshot environments,
such as keys with extremely long values, unexpected prefixes,
high entropy values (possible secrets), or statistical outliers
compared to other snapshots in the stash.
"""

import math
import re
from typing import Optional

from stashrun.snapshot import get_snapshot, list_all_snapshots

# Thresholds
_MAX_NORMAL_VALUE_LEN = 256
_HIGH_ENTROPY_THRESHOLD = 4.2  # bits per character (Shannon entropy)
_SECRET_PATTERNS = [
    re.compile(r'(?i)(password|secret|token|api[_-]?key|private[_-]?key|auth)'),
    re.compile(r'[A-Za-z0-9+/]{32,}={0,2}'),  # base64-like
    re.compile(r'[0-9a-fA-F]{32,}'),           # hex strings (tokens, hashes)
]


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy (bits per character) of a string."""
    if not value:
        return 0.0
    freq = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _looks_like_secret(key: str, value: str) -> bool:
    """Heuristic check: does this key/value look like a sensitive secret?"""
    for pattern in _SECRET_PATTERNS:
        if pattern.search(key) or pattern.search(value):
            return True
    return False


def detect_anomalies(name: str) -> Optional[dict]:
    """Analyse a snapshot for anomalous env var patterns.

    Returns a dict with:
      - ``name``: snapshot name
      - ``anomalies``: list of dicts, each describing one anomaly
      - ``score``: integer severity score (higher = more anomalous)

    Returns ``None`` if the snapshot does not exist.
    """
    env = get_snapshot(name)
    if env is None:
        return None

    anomalies = []

    for key, value in env.items():
        # Very long values
        if len(value) > _MAX_NORMAL_VALUE_LEN:
            anomalies.append({
                "key": key,
                "type": "long_value",
                "detail": f"value length {len(value)} exceeds {_MAX_NORMAL_VALUE_LEN}",
            })

        # High entropy (possible embedded secret / random token)
        entropy = _shannon_entropy(value)
        if entropy >= _HIGH_ENTROPY_THRESHOLD and len(value) >= 16:
            anomalies.append({
                "key": key,
                "type": "high_entropy",
                "detail": f"Shannon entropy {entropy:.2f} >= {_HIGH_ENTROPY_THRESHOLD}",
            })

        # Secret-looking key or value pattern
        if _looks_like_secret(key, value):
            # Avoid double-reporting if already flagged for entropy
            already = any(a["key"] == key and a["type"] == "high_entropy" for a in anomalies)
            if not already:
                anomalies.append({
                    "key": key,
                    "type": "possible_secret",
                    "detail": "key name or value pattern suggests sensitive data",
                })

        # Empty value (might be intentional, but worth flagging)
        if value == "":
            anomalies.append({
                "key": key,
                "type": "empty_value",
                "detail": "value is an empty string",
            })

    score = sum({"long_value": 1, "high_entropy": 3, "possible_secret": 2, "empty_value": 1}.get(
        a["type"], 1) for a in anomalies)

    return {"name": name, "anomalies": anomalies, "score": score}


def anomaly_rank(limit: int = 10) -> list[dict]:
    """Return snapshots sorted by anomaly score (highest first).

    Each entry contains ``name`` and ``score``.
    """
    results = []
    for name in list_all_snapshots():
        report = detect_anomalies(name)
        if report is not None:
            results.append({"name": name, "score": report["score"]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def anomaly_summary() -> dict:
    """Aggregate anomaly statistics across all snapshots.

    Returns counts of each anomaly type and the total number of
    snapshots that have at least one anomaly.
    """
    type_counts: dict[str, int] = {}
    flagged = 0
    total = 0

    for name in list_all_snapshots():
        report = detect_anomalies(name)
        if report is None:
            continue
        total += 1
        if report["anomalies"]:
            flagged += 1
        for anomaly in report["anomalies"]:
            t = anomaly["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_snapshots": total,
        "flagged_snapshots": flagged,
        "anomaly_type_counts": type_counts,
    }
