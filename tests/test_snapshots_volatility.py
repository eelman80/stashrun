"""Tests for stashrun.snapshots_volatility."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_volatility import (
    compute_volatility,
    volatility_rank,
    volatility_summary,
)


def _patch_deps(snapshot_env, versions, access_count):
    """Context manager that patches all external dependencies."""
    return (
        patch("stashrun.snapshots_volatility.get_snapshot", return_value=snapshot_env),
        patch("stashrun.snapshots_volatility.list_versions", return_value=versions),
        patch("stashrun.snapshots_volatility.get_access_count", return_value=access_count),
    )


def test_compute_volatility_missing_returns_none():
    with patch("stashrun.snapshots_volatility.get_snapshot", return_value=None):
        assert compute_volatility("ghost") is None


def test_compute_volatility_returns_dict():
    env = {"A": "1"}
    with patch("stashrun.snapshots_volatility.get_snapshot", return_value=env), \
         patch("stashrun.snapshots_volatility.list_versions", return_value=[]), \
         patch("stashrun.snapshots_volatility.get_access_count", return_value=0):
        result = compute_volatility("snap")
    assert result is not None
    assert result["name"] == "snap"
    assert "volatility_score" in result


def test_compute_volatility_no_versions_zero_churn():
    env = {"A": "1"}
    with patch("stashrun.snapshots_volatility.get_snapshot", return_value=env), \
         patch("stashrun.snapshots_volatility.list_versions", return_value=[]), \
         patch("stashrun.snapshots_volatility.get_access_count", return_value=0):
        result = compute_volatility("snap")
    assert result["key_churn"] == 0.0
    assert result["version_count"] == 0


def test_compute_volatility_key_churn_calculated():
    env = {"A": "1", "B": "2"}
    versions = [
        {"version": 1, "env": {"A": "1", "B": "2"}},
        {"version": 2, "env": {"A": "changed", "B": "2"}},
    ]
    with patch("stashrun.snapshots_volatility.get_snapshot", return_value=env), \
         patch("stashrun.snapshots_volatility.list_versions", return_value=versions), \
         patch("stashrun.snapshots_volatility.get_access_count", return_value=0):
        result = compute_volatility("snap")
    # 1 key changed out of 2 => churn = 0.5
    assert result["key_churn"] == 0.5


def test_compute_volatility_score_capped_at_100():
    env = {"X": "1"}
    versions = [{"version": i, "env": {"X": str(i)}} for i in range(20)]
    with patch("stashrun.snapshots_volatility.get_snapshot", return_value=env), \
         patch("stashrun.snapshots_volatility.list_versions", return_value=versions), \
         patch("stashrun.snapshots_volatility.get_access_count", return_value=100):
        result = compute_volatility("snap")
    assert result["volatility_score"] <= 100


def test_volatility_rank_sorted_descending():
    def fake_compute(name):
        scores = {"a": 10, "b": 80, "c": 45}
        return {"name": name, "volatility_score": scores[name],
                "version_count": 0, "key_churn": 0.0, "access_count": 0}

    with patch("stashrun.snapshots_volatility.compute_volatility", side_effect=fake_compute):
        ranked = volatility_rank(["a", "b", "c"])
    assert [r["name"] for r in ranked] == ["b", "c", "a"]


def test_volatility_summary_empty():
    with patch("stashrun.snapshots_volatility.compute_volatility", return_value=None):
        result = volatility_summary(["x", "y"])
    assert result["count"] == 0


def test_volatility_summary_aggregates_correctly():
    profiles = [
        {"name": "a", "volatility_score": 20},
        {"name": "b", "volatility_score": 80},
    ]
    with patch("stashrun.snapshots_volatility.compute_volatility", side_effect=profiles):
        result = volatility_summary(["a", "b"])
    assert result["count"] == 2
    assert result["avg_score"] == 50.0
    assert result["max_score"] == 80
    assert result["min_score"] == 20
