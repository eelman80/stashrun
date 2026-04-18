"""Tests for snapshots_reputation module."""

from unittest.mock import patch
import pytest
from stashrun.snapshots_reputation import compute_reputation, reputation_rank, top_snapshots, reputation_summary


def _patch_deps(rating=None, pins=None, favorites=None, access_count=0, all_snapshots=None):
    pins = pins or []
    favorites = favorites or []
    all_snapshots = all_snapshots or []
    return [
        patch("stashrun.snapshots_reputation.get_rating", return_value=rating),
        patch("stashrun.snapshots_reputation.list_pins", return_value=pins),
        patch("stashrun.snapshots_reputation.list_favorites", return_value=favorites),
        patch("stashrun.snapshots_reputation.get_access_count", return_value=access_count),
        patch("stashrun.snapshots_reputation.list_all_snapshots", return_value=all_snapshots),
    ]


def test_compute_reputation_all_zero():
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        score = compute_reputation("snap")
    assert score == 0.0


def test_compute_reputation_rating_only():
    patches = _patch_deps(rating=5)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        score = compute_reputation("snap")
    assert score == 50.0


def test_compute_reputation_pinned_and_favorited():
    patches = _patch_deps(pins=["snap"], favorites=["snap"])
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        score = compute_reputation("snap")
    assert score == 35.0


def test_compute_reputation_access_capped():
    patches = _patch_deps(access_count=100)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        score = compute_reputation("snap")
    assert score == 15.0


def test_compute_reputation_capped_at_100():
    patches = _patch_deps(rating=5, pins=["snap"], favorites=["snap"], access_count=100)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        score = compute_reputation("snap")
    assert score == 100.0


def test_reputation_rank_sorted():
    def fake_rating(name):
        return {"a": 1, "b": 5, "c": 3}.get(name)
    patches = [
        patch("stashrun.snapshots_reputation.get_rating", side_effect=fake_rating),
        patch("stashrun.snapshots_reputation.list_pins", return_value=[]),
        patch("stashrun.snapshots_reputation.list_favorites", return_value=[]),
        patch("stashrun.snapshots_reputation.get_access_count", return_value=0),
        patch("stashrun.snapshots_reputation.list_all_snapshots", return_value=[]),
    ]
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        ranked = reputation_rank(["a", "b", "c"])
    assert ranked[0][0] == "b"
    assert ranked[1][0] == "c"
    assert ranked[2][0] == "a"


def test_top_snapshots_returns_n():
    patches = _patch_deps(all_snapshots=["x", "y", "z", "w", "v", "u"])
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        top = top_snapshots(3)
    assert len(top) == 3


def test_reputation_summary_structure():
    patches = _patch_deps(rating=4, pins=["snap"], favorites=[], access_count=2)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        summary = reputation_summary("snap")
    assert summary["name"] == "snap"
    assert summary["rating"] == 4
    assert summary["pinned"] is True
    assert summary["favorited"] is False
    assert summary["access_count"] == 2
    assert "score" in summary
