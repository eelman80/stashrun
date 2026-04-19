"""Tests for snapshots_popularity module."""

import pytest
from unittest.mock import patch

FAKE_ENV = {"KEY": "value", "FOO": "bar"}


def _patch_deps(access=0, favorited=False, reactions=None, rating=0, snapshot_exists=True):
    return [
        patch("stashrun.snapshots_popularity.get_snapshot", return_value=FAKE_ENV if snapshot_exists else None),
        patch("stashrun.snapshots_popularity.get_access_count", return_value=access),
        patch("stashrun.snapshots_popularity.is_favorite", return_value=favorited),
        patch("stashrun.snapshots_popularity.get_reactions", return_value=reactions or {}),
        patch("stashrun.snapshots_popularity.get_rating", return_value=rating),
    ]


def test_compute_popularity_missing_returns_none():
    with patch("stashrun.snapshots_popularity.get_snapshot", return_value=None):
        from stashrun.snapshots_popularity import compute_popularity
        assert compute_popularity("ghost") is None


def test_compute_popularity_all_zero():
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        from stashrun.snapshots_popularity import compute_popularity
        result = compute_popularity("snap")
        assert result["total"] == 0.0


def test_compute_popularity_favorited_adds_score():
    patches = _patch_deps(favorited=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        from stashrun.snapshots_popularity import compute_popularity
        result = compute_popularity("snap")
        assert result["favorite_score"] == 20
        assert result["total"] == 20.0


def test_compute_popularity_access_capped_at_40():
    patches = _patch_deps(access=100)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        from stashrun.snapshots_popularity import compute_popularity
        result = compute_popularity("snap")
        assert result["access_score"] == 40


def test_compute_popularity_rating_contributes():
    patches = _patch_deps(rating=5)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        from stashrun.snapshots_popularity import compute_popularity
        result = compute_popularity("snap")
        assert result["rating_score"] == 20.0


def test_compute_popularity_reactions_contribute():
    patches = _patch_deps(reactions={"👍": 4, "❤️": 2})
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        from stashrun.snapshots_popularity import compute_popularity
        result = compute_popularity("snap")
        assert result["reaction_score"] == 18


def test_popularity_rank_sorted():
    names = ["a", "b", "c"]
    scores = {"a": 10.0, "b": 50.0, "c": 30.0}

    def fake_compute(name):
        return {"name": name, "total": scores[name]}

    with patch("stashrun.snapshots_popularity.list_all_snapshots", return_value=names), \
         patch("stashrun.snapshots_popularity.compute_popularity", side_effect=fake_compute):
        from stashrun.snapshots_popularity import popularity_rank
        ranked = popularity_rank()
        assert [r["name"] for r in ranked] == ["b", "c", "a"]


def test_popularity_summary_empty():
    with patch("stashrun.snapshots_popularity.list_all_snapshots", return_value=[]):
        from stashrun.snapshots_popularity import popularity_summary
        summary = popularity_summary()
        assert summary["count"] == 0
        assert summary["top"] is None
