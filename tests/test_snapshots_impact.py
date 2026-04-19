import pytest
from unittest.mock import patch
from stashrun.snapshots_impact import compute_impact, impact_rank, impact_summary

ENV = {"KEY": "val"}


def _patch_deps(get_snap=ENV, dependents=None, subscribers=None, groups=None):
    return (
        patch("stashrun.snapshots_impact.get_snapshot", return_value=get_snap),
        patch("stashrun.snapshots_impact.get_dependents", return_value=dependents or []),
        patch("stashrun.snapshots_impact.get_subscribers", return_value=subscribers or []),
        patch("stashrun.snapshots_impact.list_groups", return_value=groups or {}),
    )


def test_compute_impact_missing_returns_none():
    with patch("stashrun.snapshots_impact.get_snapshot", return_value=None):
        assert compute_impact("ghost") is None


def test_compute_impact_all_zero():
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_impact("snap")
    assert result["total"] == 0
    assert result["dependents"] == 0


def test_compute_impact_dependents_score():
    patches = _patch_deps(dependents=["a", "b", "c"])
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_impact("snap")
    assert result["dependent_score"] == 30
    assert result["dependents"] == 3


def test_compute_impact_subscriber_score():
    patches = _patch_deps(subscribers=["u1", "u2"])
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_impact("snap")
    assert result["subscriber_score"] == 10


def test_compute_impact_group_score():
    groups = {
        "g1": {"snapshots": ["snap", "other"]},
        "g2": {"snapshots": ["snap"]},
    }
    patches = _patch_deps(groups=groups)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_impact("snap")
    assert result["groups"] == 2
    assert result["group_score"] == 20


def test_compute_impact_score_capped():
    dependents = [str(i) for i in range(10)]
    patches = _patch_deps(dependents=dependents)
    with patches[0], patches[1], patches[2], patches[3]:
        result = compute_impact("snap")
    assert result["dependent_score"] == 40


def test_impact_rank_sorted():
    results = [
        {"name": "a", "total": 10},
        {"name": "b", "total": 50},
        {"name": "c", "total": 30},
    ]
    with patch("stashrun.snapshots_impact.compute_impact", side_effect=results):
        ranked = impact_rank(["a", "b", "c"])
    assert ranked[0]["name"] == "b"
    assert ranked[-1]["name"] == "a"


def test_impact_summary_empty():
    with patch("stashrun.snapshots_impact.compute_impact", return_value=None):
        summary = impact_summary(["x"])
    assert summary["count"] == 0


def test_impact_summary_values():
    scores = [{"total": 20}, {"total": 40}]
    with patch("stashrun.snapshots_impact.compute_impact", side_effect=scores):
        summary = impact_summary(["a", "b"])
    assert summary["count"] == 2
    assert summary["avg_total"] == 30.0
    assert summary["max_total"] == 40
