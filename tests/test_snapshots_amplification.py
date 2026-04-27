"""Tests for stashrun.snapshots_amplification."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_amplification import (
    compute_amplification,
    amplification_rank,
    amplification_summary,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _patch_deps(snapshot=None, dependents=None, relations=None, groups=None):
    """Return a context-manager stack that patches all external calls."""
    snapshot = snapshot or {"KEY": "val"}
    dependents = dependents if dependents is not None else []
    relations = relations if relations is not None else []
    groups = groups if groups is not None else {}

    patches = [
        patch("stashrun.snapshots_amplification.get_snapshot", return_value=snapshot),
        patch("stashrun.snapshots_amplification.get_dependents", return_value=dependents),
        patch("stashrun.snapshots_amplification.get_relations", return_value=relations),
        patch("stashrun.snapshots_amplification.list_groups", return_value=groups),
        patch("stashrun.snapshots_amplification.list_all_snapshots", return_value=["snap1"]),
    ]
    return patches


# ---------------------------------------------------------------------------
# compute_amplification
# ---------------------------------------------------------------------------

def test_compute_amplification_missing_returns_none():
    with patch("stashrun.snapshots_amplification.get_snapshot", return_value=None):
        assert compute_amplification("ghost") is None


def test_compute_amplification_all_zero():
    ps = _patch_deps(dependents=[], relations=[], groups={})
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result is not None
    assert result["score"] == 0
    assert result["dep_score"] == 0
    assert result["rel_score"] == 0
    assert result["grp_score"] == 0


def test_compute_amplification_dependents_score():
    ps = _patch_deps(dependents=["a", "b", "c"], relations=[], groups={})
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["dep_score"] == 30  # 3 * 10
    assert result["score"] == 30


def test_compute_amplification_dep_score_capped_at_40():
    ps = _patch_deps(dependents=["a"] * 10, relations=[], groups={})
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["dep_score"] == 40


def test_compute_amplification_relations_score():
    ps = _patch_deps(dependents=[], relations=[{}, {}], groups={})
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["rel_score"] == 16  # 2 * 8


def test_compute_amplification_rel_score_capped_at_30():
    ps = _patch_deps(dependents=[], relations=[{}] * 10, groups={})
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["rel_score"] == 30


def test_compute_amplification_group_score():
    groups = {
        "g1": {"members": ["snap1", "snap2"]},
        "g2": {"members": ["snap1"]},
        "g3": {"members": ["other"]},
    }
    ps = _patch_deps(dependents=[], relations=[], groups=groups)
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["groups"] == 2
    assert result["grp_score"] == 20


def test_compute_amplification_returns_name_field():
    ps = _patch_deps()
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        result = compute_amplification("snap1")
    assert result["name"] == "snap1"


# ---------------------------------------------------------------------------
# amplification_rank
# ---------------------------------------------------------------------------

def test_amplification_rank_returns_sorted_list():
    def _fake_get(name):
        return {"K": "v"}

    def _fake_dependents(name):
        return ["x"] if name == "snap1" else []

    with patch("stashrun.snapshots_amplification.list_all_snapshots", return_value=["snap1", "snap2"]), \
         patch("stashrun.snapshots_amplification.get_snapshot", side_effect=_fake_get), \
         patch("stashrun.snapshots_amplification.get_dependents", side_effect=_fake_dependents), \
         patch("stashrun.snapshots_amplification.get_relations", return_value=[]), \
         patch("stashrun.snapshots_amplification.list_groups", return_value={}):
        ranked = amplification_rank()

    assert ranked[0]["name"] == "snap1"
    assert ranked[0]["score"] > ranked[1]["score"]


# ---------------------------------------------------------------------------
# amplification_summary
# ---------------------------------------------------------------------------

def test_amplification_summary_empty():
    with patch("stashrun.snapshots_amplification.list_all_snapshots", return_value=[]):
        summary = amplification_summary()
    assert summary["count"] == 0
    assert summary["top"] is None


def test_amplification_summary_returns_top():
    ps = _patch_deps(dependents=["a", "b"])
    with ps[0], ps[1], ps[2], ps[3], ps[4]:
        summary = amplification_summary()
    assert summary["top"] == "snap1"
    assert summary["count"] == 1
