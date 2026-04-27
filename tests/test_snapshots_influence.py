"""Tests for stashrun.snapshots_influence."""

import pytest
from unittest.mock import patch

FAKE_SNAPSHOTS = ["alpha", "beta", "gamma"]


def _patch_deps(name, dependents=None, subscribers=None, mentions=None, endorsers=None, env=None):
    """Return a context-manager stack that patches all external calls."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("stashrun.snapshots_influence.get_snapshot", return_value=env or {"K": "v"}), \
             patch("stashrun.snapshots_influence.get_dependents", return_value=dependents or []), \
             patch("stashrun.snapshots_influence.get_subscribers", return_value=subscribers or []), \
             patch("stashrun.snapshots_influence.get_mentions", return_value=mentions or []), \
             patch("stashrun.snapshots_influence.get_endorsers", return_value=endorsers or []), \
             patch("stashrun.snapshots_influence.list_snapshots", return_value=FAKE_SNAPSHOTS):
            yield

    return _ctx()


def test_compute_influence_missing_returns_none():
    with patch("stashrun.snapshots_influence.get_snapshot", return_value=None):
        from stashrun.snapshots_influence import compute_influence
        assert compute_influence("ghost") is None


def test_compute_influence_all_zero():
    with _patch_deps("alpha"):
        from stashrun.snapshots_influence import compute_influence
        result = compute_influence("alpha")
    assert result is not None
    assert result["total"] == 0
    assert result["dependents"] == 0


def test_compute_influence_dependents_score():
    with _patch_deps("alpha", dependents=["b", "c", "d"]):
        from stashrun.snapshots_influence import compute_influence
        result = compute_influence("alpha")
    assert result["dep_score"] == 24  # 3 * 8
    assert result["dependents"] == 3


def test_compute_influence_dep_score_capped_at_40():
    with _patch_deps("alpha", dependents=[str(i) for i in range(20)]):
        from stashrun.snapshots_influence import compute_influence
        result = compute_influence("alpha")
    assert result["dep_score"] == 40


def test_compute_influence_subscribers_capped_at_25():
    with _patch_deps("alpha", subscribers=[str(i) for i in range(10)]):
        from stashrun.snapshots_influence import compute_influence
        result = compute_influence("alpha")
    assert result["sub_score"] == 25


def test_compute_influence_endorsements_score():
    with _patch_deps("alpha", endorsers=["alice", "bob"]):
        from stashrun.snapshots_influence import compute_influence
        result = compute_influence("alpha")
    assert result["endorse_score"] == 10  # 2 * 5


def test_compute_influence_total_is_sum_of_parts():
    with _patch_deps("alpha", dependents=["x"], subscribers=["y"], mentions=["z"], endorsers=["w"]):
        from stashrun.snapshots_influence import compute_influence
        r = compute_influence("alpha")
    assert r["total"] == r["dep_score"] + r["sub_score"] + r["mention_score"] + r["endorse_score"]


def test_influence_rank_sorted_descending():
    call_counts = {"alpha": 3, "beta": 1, "gamma": 5}

    def fake_get_snapshot(n):
        return {"K": "v"}

    def fake_dependents(n):
        return [str(i) for i in range(call_counts[n])]

    with patch("stashrun.snapshots_influence.get_snapshot", side_effect=fake_get_snapshot), \
         patch("stashrun.snapshots_influence.get_dependents", side_effect=fake_dependents), \
         patch("stashrun.snapshots_influence.get_subscribers", return_value=[]), \
         patch("stashrun.snapshots_influence.get_mentions", return_value=[]), \
         patch("stashrun.snapshots_influence.get_endorsers", return_value=[]), \
         patch("stashrun.snapshots_influence.list_snapshots", return_value=FAKE_SNAPSHOTS):
        from stashrun.snapshots_influence import influence_rank
        ranked = influence_rank()

    assert ranked[0]["name"] == "gamma"
    assert ranked[-1]["name"] == "beta"


def test_influence_summary_empty():
    with patch("stashrun.snapshots_influence.list_snapshots", return_value=[]):
        from stashrun.snapshots_influence import influence_summary
        summary = influence_summary()
    assert summary["count"] == 0
    assert summary["top"] is None


def test_influence_summary_returns_top():
    with _patch_deps("alpha", dependents=["x", "y"]):
        with patch("stashrun.snapshots_influence.list_snapshots", return_value=["alpha"]):
            from stashrun.snapshots_influence import influence_summary
            summary = influence_summary()
    assert summary["count"] == 1
    assert summary["top"] == "alpha"
    assert summary["max"] > 0
