"""Tests for snapshot freshness scoring."""

import time
import pytest
from unittest.mock import patch

FAKE_ENV = {"KEY": "value"}
NOW = time.time()


def _patch_deps(snapshot_env=FAKE_ENV, last_accessed=None, access_count=0, history=None):
    """Helper to patch all external dependencies of compute_freshness."""
    if history is None:
        history = []
    return [
        patch("stashrun.snapshots_freshness.get_snapshot", return_value=snapshot_env),
        patch("stashrun.snapshots_freshness.get_last_accessed", return_value=last_accessed),
        patch("stashrun.snapshots_freshness.get_access_count", return_value=access_count),
        patch("stashrun.snapshots_freshness.get_history", return_value=history),
    ]


def test_compute_freshness_missing_returns_none():
    with patch("stashrun.snapshots_freshness.get_snapshot", return_value=None):
        from stashrun.snapshots_freshness import compute_freshness
        assert compute_freshness("ghost") is None


def test_compute_freshness_returns_dict():
    patches = _patch_deps(last_accessed=NOW, access_count=5)
    with patches[0], patches[1], patches[2], patches[3]:
        from stashrun.snapshots_freshness import compute_freshness
        result = compute_freshness("mysnap")
        assert isinstance(result, dict)
        assert "total" in result
        assert "age_score" in result
        assert "access_score" in result
        assert "save_score" in result


def test_compute_freshness_recent_access_high_score():
    patches = _patch_deps(last_accessed=NOW - 60, access_count=10)
    with patches[0], patches[1], patches[2], patches[3]:
        from stashrun.snapshots_freshness import compute_freshness
        result = compute_freshness("fresh")
        assert result["age_score"] >= 55
        assert result["access_score"] == 20


def test_compute_freshness_no_access_low_age_score():
    patches = _patch_deps(last_accessed=None, access_count=0)
    with patches[0], patches[1], patches[2], patches[3]:
        from stashrun.snapshots_freshness import compute_freshness
        result = compute_freshness("stale")
        assert result["age_score"] == 0
        assert result["access_score"] == 0


def test_compute_freshness_save_score_with_recent_save():
    history = [{"event": "save", "timestamp": NOW - 100}]
    patches = _patch_deps(last_accessed=NOW, history=history)
    with patches[0], patches[1], patches[2], patches[3]:
        from stashrun.snapshots_freshness import compute_freshness
        result = compute_freshness("saved")
        assert result["save_score"] >= 19


def test_freshness_rank_sorted():
    names = ["a", "b", "c"]
    scores = {"a": {"total": 40, "age_score": 20, "access_score": 10, "save_score": 10},
              "b": {"total": 80, "age_score": 50, "access_score": 20, "save_score": 10},
              "c": {"total": 60, "age_score": 40, "access_score": 10, "save_score": 10}}
    with patch("stashrun.snapshots_freshness.compute_freshness", side_effect=lambda n: scores[n]):
        from stashrun.snapshots_freshness import freshness_rank
        ranked = freshness_rank(names)
        assert ranked[0][0] == "b"
        assert ranked[1][0] == "c"
        assert ranked[2][0] == "a"


def test_freshness_summary_empty():
    with patch("stashrun.snapshots_freshness.compute_freshness", return_value=None):
        from stashrun.snapshots_freshness import freshness_summary
        result = freshness_summary(["x", "y"])
        assert result["count"] == 0
        assert result["average"] == 0
        assert result["top"] is None


def test_freshness_summary_calculates_correctly():
    results = {"a": {"total": 60}, "b": {"total": 80}}
    with patch("stashrun.snapshots_freshness.compute_freshness", side_effect=lambda n: results[n]):
        from stashrun.snapshots_freshness import freshness_summary
        summary = freshness_summary(["a", "b"])
        assert summary["count"] == 2
        assert summary["average"] == 70.0
        assert summary["top"] == 80
