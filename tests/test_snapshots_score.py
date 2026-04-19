"""Tests for snapshots_score composite scoring."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_score import compute_score, score_rank, score_summary


def _make_score(val):
    return {"score": val}


def _patch_deps(health=50, confidence=60, reputation=40, impact=30):
    return (
        patch("stashrun.snapshots_score.compute_health", return_value={"score": health} if health is not None else None),
        patch("stashrun.snapshots_score.compute_confidence", return_value={"score": confidence}),
        patch("stashrun.snapshots_score.compute_reputation", return_value={"score": reputation}),
        patch("stashrun.snapshots_score.compute_impact", return_value={"score": impact}),
    )


def test_compute_score_missing_returns_none():
    with patch("stashrun.snapshots_score.compute_health", return_value=None):
        assert compute_score("ghost") is None


def test_compute_score_returns_dict():
    patches = _patch_deps(health=100, confidence=100, reputation=100, impact=100)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_score("snap1")
    assert result is not None
    assert result["composite"] == 100.0
    assert result["name"] == "snap1"


def test_compute_score_weighted_correctly():
    patches = _patch_deps(health=100, confidence=0, reputation=0, impact=0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_score("snap1")
    assert result["composite"] == 40.0


def test_compute_score_all_zero():
    patches = _patch_deps(health=0, confidence=0, reputation=0, impact=0)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_score("snap1")
    assert result["composite"] == 0.0


def test_score_rank_orders_descending():
    def fake_score(name):
        return {"score": {"a": 80, "b": 50, "c": 95}[name]}

    patches = [
        patch("stashrun.snapshots_score.compute_health", side_effect=fake_score),
        patch("stashrun.snapshots_score.compute_confidence", return_value={"score": 0}),
        patch("stashrun.snapshots_score.compute_reputation", return_value={"score": 0}),
        patch("stashrun.snapshots_score.compute_impact", return_value={"score": 0}),
    ]
    with patches[0], patches[1], patches[2], patches[3]:
        ranked = score_rank(["a", "b", "c"])
    assert [r["name"] for r in ranked] == ["c", "a", "b"]


def test_score_summary_empty():
    with patch("stashrun.snapshots_score.compute_health", return_value=None):
        summary = score_summary(["x"])
    assert summary["count"] == 0
    assert summary["top"] is None


def test_score_summary_with_data():
    patches = _patch_deps(health=80, confidence=80, reputation=80, impact=80)
    with patches[0], patches[1], patches[2], patches[3]:
        summary = score_summary(["a", "b"])
    assert summary["count"] == 2
    assert summary["average"] == 80.0
    assert summary["top"] in ("a", "b")
