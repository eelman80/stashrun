"""Tests for snapshots_health module."""

import pytest
from unittest.mock import patch

MODULE = "stashrun.snapshots_health"


def _patch(env=None, checksum_stored=None, checksum_current=None,
           note=None, ttl=None, validation=None):
    env = env or {"KEY": "val"}
    patches = {
        f"{MODULE}.get_snapshot": env,
        f"{MODULE}.get_checksum": checksum_stored,
        f"{MODULE}.compute_checksum": checksum_current or "abc",
        f"{MODULE}.get_note": note,
        f"{MODULE}.get_ttl": ttl,
        f"{MODULE}.validate_snapshot": validation or {},
    }
    return patches


def test_compute_health_missing_snapshot():
    with patch(f"{MODULE}.get_snapshot", return_value=None):
        from stashrun.snapshots_health import compute_health
        assert compute_health("ghost") is None


def test_compute_health_perfect_score():
    from stashrun.snapshots_health import compute_health
    with patch(f"{MODULE}.get_snapshot", return_value={"KEY": "val"}), \
         patch(f"{MODULE}.get_checksum", return_value="abc"), \
         patch(f"{MODULE}.compute_checksum", return_value="abc"), \
         patch(f"{MODULE}.get_note", return_value="some note"), \
         patch(f"{MODULE}.get_ttl", return_value=None), \
         patch(f"{MODULE}.validate_snapshot", return_value={}):
        report = compute_health("snap")
    assert report["score"] == 100
    assert report["status"] == "healthy"
    assert report["issues"] == []


def test_compute_health_no_checksum_deducts_score():
    from stashrun.snapshots_health import compute_health
    with patch(f"{MODULE}.get_snapshot", return_value={"K": "v"}), \
         patch(f"{MODULE}.get_checksum", return_value=None), \
         patch(f"{MODULE}.get_note", return_value="note"), \
         patch(f"{MODULE}.get_ttl", return_value=None), \
         patch(f"{MODULE}.validate_snapshot", return_value={}):
        report = compute_health("snap")
    assert report["score"] == 80
    assert any("checksum" in i for i in report["issues"])


def test_compute_health_checksum_mismatch():
    from stashrun.snapshots_health import compute_health
    with patch(f"{MODULE}.get_snapshot", return_value={"K": "v"}), \
         patch(f"{MODULE}.get_checksum", return_value="old"), \
         patch(f"{MODULE}.compute_checksum", return_value="new"), \
         patch(f"{MODULE}.get_note", return_value="note"), \
         patch(f"{MODULE}.get_ttl", return_value=None), \
         patch(f"{MODULE}.validate_snapshot", return_value={}):
        report = compute_health("snap")
    assert report["score"] == 60
    assert any("mismatch" in i for i in report["issues"])


def test_compute_health_expired_ttl():
    from stashrun.snapshots_health import compute_health
    import time
    with patch(f"{MODULE}.get_snapshot", return_value={"K": "v"}), \
         patch(f"{MODULE}.get_checksum", return_value="x"), \
         patch(f"{MODULE}.compute_checksum", return_value="x"), \
         patch(f"{MODULE}.get_note", return_value="n"), \
         patch(f"{MODULE}.get_ttl", return_value=time.time() - 100), \
         patch(f"{MODULE}.validate_snapshot", return_value={}):
        report = compute_health("snap")
    assert report["score"] == 85
    assert any("expired" in i for i in report["issues"])


def test_health_summary_sorted_by_score():
    from stashrun.snapshots_health import health_summary
    reports = [
        {"name": "a", "score": 90, "status": "healthy", "issues": []},
        {"name": "b", "score": 40, "status": "unhealthy", "issues": []},
        {"name": "c", "score": 70, "status": "degraded", "issues": []},
    ]
    with patch(f"{MODULE}.list_snapshots", return_value=["a", "b", "c"]), \
         patch(f"{MODULE}.compute_health", side_effect=reports):
        result = health_summary()
    assert result[0]["name"] == "b"
    assert result[-1]["name"] == "a"
