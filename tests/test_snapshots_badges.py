"""Tests for snapshots_badges module."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_badges import compute_badges, badge_summary, snapshots_with_badge


def _patch_deps(env=None, verified=False, pinned=False, favorite=False, rating=None):
    patches = [
        patch("stashrun.snapshots_badges.get_snapshot", return_value=env),
        patch("stashrun.snapshots_badges.verify_checksum", return_value=verified),
        patch("stashrun.snapshots_badges.is_pinned", return_value=pinned),
        patch("stashrun.snapshots_badges.is_favorite", return_value=favorite),
        patch("stashrun.snapshots_badges.get_rating", return_value=rating),
    ]
    return patches


def test_compute_badges_missing_returns_none():
    with patch("stashrun.snapshots_badges.get_snapshot", return_value=None):
        assert compute_badges("ghost") is None


def test_compute_badges_no_badges():
    env = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5", "F": "6"}
    patches = _patch_deps(env=env)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("plain")
    assert result == []


def test_compute_badges_verified():
    env = {"K": "v"}
    patches = _patch_deps(env=env, verified=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "verified" in result


def test_compute_badges_pinned_and_favorite():
    env = {"K": "v"}
    patches = _patch_deps(env=env, pinned=True, favorite=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "pinned" in result
    assert "favorite" in result


def test_compute_badges_top_rated():
    env = {"K": "v"}
    patches = _patch_deps(env=env, rating=5)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "top_rated" in result
    assert "well_rated" not in result


def test_compute_badges_well_rated():
    env = {"K": "v"}
    patches = _patch_deps(env=env, rating=4)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "well_rated" in result
    assert "top_rated" not in result


def test_compute_badges_large():
    env = {str(i): str(i) for i in range(25)}
    patches = _patch_deps(env=env)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "large" in result


def test_compute_badges_tiny():
    env = {"A": "1"}
    patches = _patch_deps(env=env)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_badges("snap")
    assert "tiny" in result


def test_badge_summary_returns_labels():
    env = {"K": "v"}
    patches = _patch_deps(env=env, pinned=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = badge_summary("snap")
    assert isinstance(result, dict)
    assert "pinned" in result
    assert isinstance(result["pinned"], str)


def test_snapshots_with_badge_filters_correctly():
    env = {"K": "v"}
    with patch("stashrun.snapshots_badges.compute_badges", side_effect=[
        ["pinned", "verified"], ["verified"], ["pinned"]
    ]):
        result = snapshots_with_badge("pinned", ["a", "b", "c"])
    assert result == ["a", "c"]
