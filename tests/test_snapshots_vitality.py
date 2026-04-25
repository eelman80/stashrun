"""Tests for stashrun.snapshots_vitality."""

from unittest.mock import patch

import pytest

from stashrun.snapshots_vitality import compute_vitality, vitality_rank, vitality_summary


_FRESHNESS = {"score": 80, "age_score": 40, "access_score": 40}
_HEALTH = {"score": 60, "checksum_ok": True, "lint_ok": False}
_MOMENTUM = {"score": 50, "version_score": 25, "access_score": 25}


@pytest.fixture()
def _patch_deps():
    with (
        patch("stashrun.snapshots_vitality.get_snapshot") as mock_get,
        patch("stashrun.snapshots_vitality.compute_freshness") as mock_fresh,
        patch("stashrun.snapshots_vitality.compute_health") as mock_health,
        patch("stashrun.snapshots_vitality.compute_momentum") as mock_mom,
        patch("stashrun.snapshots_vitality.list_snapshots") as mock_list,
    ):
        mock_get.return_value = {"KEY": "val"}
        mock_fresh.return_value = _FRESHNESS
        mock_health.return_value = _HEALTH
        mock_mom.return_value = _MOMENTUM
        mock_list.return_value = ["snap-a", "snap-b"]
        yield {
            "get": mock_get,
            "fresh": mock_fresh,
            "health": mock_health,
            "mom": mock_mom,
            "list": mock_list,
        }


def test_compute_vitality_missing_returns_none(_patch_deps):
    _patch_deps["get"].return_value = None
    assert compute_vitality("ghost") is None


def test_compute_vitality_returns_dict(_patch_deps):
    result = compute_vitality("snap-a")
    assert isinstance(result, dict)
    assert result["name"] == "snap-a"
    assert "score" in result
    assert "freshness" in result
    assert "health" in result
    assert "momentum" in result


def test_compute_vitality_weighted_correctly(_patch_deps):
    # 80*0.4 + 60*0.4 + 50*0.2 = 32 + 24 + 10 = 66
    result = compute_vitality("snap-a")
    assert result["score"] == 66


def test_compute_vitality_all_zero(_patch_deps):
    _patch_deps["fresh"].return_value = {"score": 0}
    _patch_deps["health"].return_value = {"score": 0}
    _patch_deps["mom"].return_value = {"score": 0}
    result = compute_vitality("snap-a")
    assert result["score"] == 0


def test_compute_vitality_none_sub_scores_default_to_zero(_patch_deps):
    _patch_deps["fresh"].return_value = None
    _patch_deps["health"].return_value = None
    _patch_deps["mom"].return_value = None
    result = compute_vitality("snap-a")
    assert result["score"] == 0


def test_vitality_rank_sorted_descending(_patch_deps):
    def _vitality_side_effect(name):
        scores = {"snap-a": 70, "snap-b": 30}
        return {"name": name, "score": scores[name], "freshness": 0, "health": 0, "momentum": 0}

    with patch("stashrun.snapshots_vitality.compute_vitality", side_effect=_vitality_side_effect):
        ranked = vitality_rank()

    assert ranked[0]["name"] == "snap-a"
    assert ranked[1]["name"] == "snap-b"


def test_vitality_summary_empty(_patch_deps):
    _patch_deps["list"].return_value = []
    with patch("stashrun.snapshots_vitality.compute_vitality", return_value=None):
        summary = vitality_summary()
    assert summary["count"] == 0
    assert summary["top"] is None


def test_vitality_summary_populated(_patch_deps):
    def _v(name):
        scores = {"snap-a": 80, "snap-b": 40}
        return {"name": name, "score": scores[name], "freshness": 0, "health": 0, "momentum": 0}

    with patch("stashrun.snapshots_vitality.compute_vitality", side_effect=_v):
        summary = vitality_summary()

    assert summary["count"] == 2
    assert summary["average"] == 60
    assert summary["top"] == "snap-a"
    assert summary["bottom"] == "snap-b"
