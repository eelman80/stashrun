"""Tests for snapshots_momentum.py"""

import pytest
from unittest.mock import patch
from stashrun.snapshots_momentum import compute_momentum, momentum_rank, momentum_summary


def _patch_deps(snapshot_env=None, versions=None, access_count=0, last_accessed=None, rating=None, all_names=None):
    """Return a context-manager stack that patches all external calls."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("stashrun.snapshots_momentum.get_snapshot", return_value=snapshot_env), \
             patch("stashrun.snapshots_momentum.list_versions", return_value=versions or []), \
             patch("stashrun.snapshots_momentum.get_access_count", return_value=access_count), \
             patch("stashrun.snapshots_momentum.get_last_accessed", return_value=last_accessed), \
             patch("stashrun.snapshots_momentum.get_rating", return_value=rating), \
             patch("stashrun.snapshots_momentum.list_all_snapshots", return_value=all_names or []):
            yield

    return _ctx()


def test_compute_momentum_missing_returns_none():
    with _patch_deps(snapshot_env=None):
        assert compute_momentum("ghost") is None


def test_compute_momentum_returns_dict():
    with _patch_deps(snapshot_env={"A": "1"}):
        result = compute_momentum("snap")
    assert isinstance(result, dict)
    assert result["name"] == "snap"
    assert "total" in result


def test_compute_momentum_version_score_capped():
    versions = [{}] * 20  # 20 versions -> 160 raw, capped at 40
    with _patch_deps(snapshot_env={"A": "1"}, versions=versions):
        result = compute_momentum("snap")
    assert result["version_score"] == 40


def test_compute_momentum_access_score_capped():
    with _patch_deps(snapshot_env={"A": "1"}, access_count=100):
        result = compute_momentum("snap")
    assert result["access_score"] == 30


def test_compute_momentum_rating_score():
    with _patch_deps(snapshot_env={"A": "1"}, rating=5):
        result = compute_momentum("snap")
    assert result["rating_score"] == 20


def test_compute_momentum_no_rating_zero_score():
    with _patch_deps(snapshot_env={"A": "1"}, rating=None):
        result = compute_momentum("snap")
    assert result["rating_score"] == 0


def test_compute_momentum_recent_access_high_recency():
    import time
    now = time.time()
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=now - 3600):
        result = compute_momentum("snap")
    assert result["recency_score"] == 10


def test_compute_momentum_no_access_zero_recency():
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=None):
        result = compute_momentum("snap")
    assert result["recency_score"] == 0


def test_momentum_rank_sorted_descending():
    def _fake_momentum(name):
        return {"name": name, "total": {"a": 10, "b": 50, "c": 30}[name]}

    with patch("stashrun.snapshots_momentum.list_all_snapshots", return_value=["a", "b", "c"]), \
         patch("stashrun.snapshots_momentum.compute_momentum", side_effect=_fake_momentum):
        ranked = momentum_rank()

    assert [r["name"] for r in ranked] == ["b", "c", "a"]


def test_momentum_summary_empty():
    with patch("stashrun.snapshots_momentum.momentum_rank", return_value=[]):
        summary = momentum_summary()
    assert summary["count"] == 0
    assert summary["top"] is None


def test_momentum_summary_values():
    fake = [{"name": "x", "total": 60}, {"name": "y", "total": 40}]
    with patch("stashrun.snapshots_momentum.momentum_rank", return_value=fake):
        summary = momentum_summary()
    assert summary["count"] == 2
    assert summary["average"] == 50.0
    assert summary["top"] == "x"
