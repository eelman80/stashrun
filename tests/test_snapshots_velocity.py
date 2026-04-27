"""Tests for snapshots_velocity module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_velocity import compute_velocity, velocity_rank, velocity_summary

_VERSIONS = ["v1", "v2", "v3"]
_ACCESS_COUNT = 5
_LAST_ACCESSED = "2024-06-01T12:00:00"


@pytest.fixture()
def _patch_deps():
    with (
        patch("stashrun.snapshots_velocity.get_snapshot") as mock_get,
        patch("stashrun.snapshots_velocity.list_versions") as mock_versions,
        patch("stashrun.snapshots_velocity.get_access_count") as mock_count,
        patch("stashrun.snapshots_velocity.get_last_accessed") as mock_last,
        patch("stashrun.snapshots_velocity.list_all_snapshots") as mock_list,
    ):
        mock_get.return_value = {"KEY": "val"}
        mock_versions.return_value = _VERSIONS
        mock_count.return_value = _ACCESS_COUNT
        mock_last.return_value = _LAST_ACCESSED
        mock_list.return_value = ["snap_a", "snap_b"]
        yield {
            "get": mock_get,
            "versions": mock_versions,
            "count": mock_count,
            "last": mock_last,
            "list": mock_list,
        }


def test_compute_velocity_missing_returns_none(_patch_deps):
    _patch_deps["get"].return_value = None
    assert compute_velocity("ghost") is None


def test_compute_velocity_returns_dict(_patch_deps):
    result = compute_velocity("snap_a")
    assert isinstance(result, dict)
    assert "score" in result


def test_compute_velocity_version_score_capped(_patch_deps):
    _patch_deps["versions"].return_value = [f"v{i}" for i in range(20)]
    result = compute_velocity("snap_a")
    assert result["version_score"] == 50


def test_compute_velocity_access_score_capped(_patch_deps):
    _patch_deps["count"].return_value = 100
    result = compute_velocity("snap_a")
    assert result["access_score"] == 30


def test_compute_velocity_no_access_no_recency_bonus(_patch_deps):
    _patch_deps["last"].return_value = None
    result = compute_velocity("snap_a")
    assert result["recency_bonus"] == 0


def test_compute_velocity_correct_totals(_patch_deps):
    result = compute_velocity("snap_a")
    expected = result["version_score"] + result["access_score"] + result["recency_bonus"]
    assert result["score"] == expected


def test_velocity_rank_returns_sorted_list(_patch_deps):
    def side_effect(name):
        return {"score": 80} if name == "snap_a" else {"score": 40}

    with patch("stashrun.snapshots_velocity.compute_velocity", side_effect=side_effect):
        ranked = velocity_rank()
    assert ranked[0][0] == "snap_a"
    assert ranked[1][0] == "snap_b"


def test_velocity_summary_returns_correct_fields(_patch_deps):
    summary = velocity_summary()
    assert "count" in summary
    assert "avg_score" in summary
    assert "top" in summary


def test_velocity_summary_empty_list(_patch_deps):
    _patch_deps["list"].return_value = []
    summary = velocity_summary()
    assert summary["count"] == 0
    assert summary["top"] is None
