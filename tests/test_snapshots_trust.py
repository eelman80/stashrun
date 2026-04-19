"""Tests for snapshots_trust module."""

import pytest
from unittest.mock import patch

ENV = {"KEY": "value", "OTHER": "data"}
CHECKSUM = "abc123"


def _patch_deps(env=ENV, owner="alice", checksum=CHECKSUM, valid_checksum=True,
                visibility="private", perms=None):
    if perms is None:
        perms = {"read": True, "write": False, "delete": False}
    computed = checksum if valid_checksum else "wrong"
    return [
        patch("stashrun.snapshots_trust.get_snapshot", return_value=env),
        patch("stashrun.snapshots_trust.get_owner", return_value=owner),
        patch("stashrun.snapshots_trust.get_checksum", return_value=checksum),
        patch("stashrun.snapshots_trust.compute_checksum", return_value=computed),
        patch("stashrun.snapshots_trust.get_visibility", return_value=visibility),
        patch("stashrun.snapshots_trust.get_permissions", return_value=perms),
    ]


def test_compute_trust_missing_returns_none():
    with patch("stashrun.snapshots_trust.get_snapshot", return_value=None):
        from stashrun.snapshots_trust import compute_trust
        assert compute_trust("ghost") is None


def test_compute_trust_full_score():
    from stashrun.snapshots_trust import compute_trust
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_trust("snap")
    assert result is not None
    assert result["score"] == 20 + 30 + 20 + 15 + 15
    assert result["level"] == "verified"


def test_compute_trust_no_owner_reduces_score():
    from stashrun.snapshots_trust import compute_trust
    patches = _patch_deps(owner=None)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_trust("snap")
    assert result["breakdown"]["owner"] == 0


def test_compute_trust_invalid_checksum_partial_score():
    from stashrun.snapshots_trust import compute_trust
    patches = _patch_deps(valid_checksum=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_trust("snap")
    assert result["breakdown"]["checksum"] == 10


def test_compute_trust_no_checksum_zero():
    from stashrun.snapshots_trust import compute_trust
    patches = _patch_deps(checksum=None)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_trust("snap")
    assert result["breakdown"]["checksum"] == 0


def test_compute_trust_public_visibility_lower_score():
    from stashrun.snapshots_trust import compute_trust
    patches = _patch_deps(visibility="public")
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_trust("snap")
    assert result["breakdown"]["visibility"] == 5


def test_trust_level_boundaries():
    from stashrun.snapshots_trust import trust_level
    assert trust_level(95) == "verified"
    assert trust_level(75) == "high"
    assert trust_level(50) == "medium"
    assert trust_level(25) == "low"
    assert trust_level(10) == "untrusted"


def test_trust_rank_orders_by_score():
    from stashrun.snapshots_trust import trust_rank
    scores = {"a": 80, "b": 40, "c": 60}

    def fake_compute(name):
        return {"score": scores[name], "level": "medium", "breakdown": {}}

    with patch("stashrun.snapshots_trust.compute_trust", side_effect=fake_compute):
        ranked = trust_rank(["a", "b", "c"])
    assert [n for n, _ in ranked] == ["a", "c", "b"]


def test_trust_summary_counts_levels():
    from stashrun.snapshots_trust import trust_summary
    results = {"x": {"score": 95, "level": "verified"}, "y": {"score": 30, "level": "low"}}
    with patch("stashrun.snapshots_trust.compute_trust", side_effect=lambda n: results.get(n)):
        summary = trust_summary(["x", "y"])
    assert summary["verified"] == 1
    assert summary["low"] == 1
    assert summary["high"] == 0
