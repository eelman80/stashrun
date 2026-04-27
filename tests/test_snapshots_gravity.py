"""Tests for stashrun.snapshots_gravity."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_gravity import compute_gravity, gravity_rank, gravity_summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_NAMES = ["snap_a", "snap_b"]


def _patch_deps(name, *, dependents=None, mentions=None, relations=None, endorsements=0):
    return [
        patch("stashrun.snapshots_gravity.get_snapshot", return_value={"KEY": "val"}),
        patch("stashrun.snapshots_gravity.get_dependents", return_value=dependents or []),
        patch("stashrun.snapshots_gravity.get_mentions", return_value=mentions or []),
        patch("stashrun.snapshots_gravity.get_relations", return_value=relations or {}),
        patch("stashrun.snapshots_gravity.get_endorsement_count", return_value=endorsements),
    ]


# ---------------------------------------------------------------------------
# compute_gravity
# ---------------------------------------------------------------------------

def test_compute_gravity_missing_returns_none():
    with patch("stashrun.snapshots_gravity.get_snapshot", return_value=None):
        assert compute_gravity("ghost") is None


def test_compute_gravity_all_zero():
    patches = _patch_deps("snap")
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result is not None
    assert result["total"] == 0
    assert result["name"] == "snap"


def test_compute_gravity_dependents_score():
    patches = _patch_deps("snap", dependents=["a", "b", "c"])
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result["dep_score"] == 3 * 15
    assert result["dependents"] == 3


def test_compute_gravity_dep_score_capped_at_40():
    patches = _patch_deps("snap", dependents=[str(i) for i in range(10)])
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result["dep_score"] == 40


def test_compute_gravity_endorsements_score():
    patches = _patch_deps("snap", endorsements=4)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result["endorse_score"] == 12


def test_compute_gravity_endorse_score_capped_at_15():
    patches = _patch_deps("snap", endorsements=20)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result["endorse_score"] == 15


def test_compute_gravity_relations_score():
    patches = _patch_deps("snap", relations={"related": ["x", "y"], "derived": ["z"]})
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        result = compute_gravity("snap")
    assert result["relations"] == 3
    assert result["relation_score"] == 12


# ---------------------------------------------------------------------------
# gravity_rank
# ---------------------------------------------------------------------------

def test_gravity_rank_sorted_descending():
    def fake_gravity(name):
        return {"name": name, "total": 10 if name == "snap_a" else 5}

    with patch("stashrun.snapshots_gravity.list_all_snapshots", return_value=_NAMES), \
         patch("stashrun.snapshots_gravity.compute_gravity", side_effect=fake_gravity):
        ranked = gravity_rank()

    assert ranked[0]["name"] == "snap_a"
    assert ranked[1]["name"] == "snap_b"


# ---------------------------------------------------------------------------
# gravity_summary
# ---------------------------------------------------------------------------

def test_gravity_summary_empty():
    with patch("stashrun.snapshots_gravity.list_all_snapshots", return_value=[]), \
         patch("stashrun.snapshots_gravity.compute_gravity", return_value=None):
        s = gravity_summary()
    assert s["count"] == 0
    assert s["top"] is None


def test_gravity_summary_values():
    fake = [{"name": "a", "total": 30}, {"name": "b", "total": 10}]
    with patch("stashrun.snapshots_gravity.gravity_rank", return_value=fake):
        s = gravity_summary()
    assert s["count"] == 2
    assert s["max"] == 30
    assert s["avg"] == 20.0
    assert s["top"] == "a"
