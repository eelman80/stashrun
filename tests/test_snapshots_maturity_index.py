"""Tests for stashrun.snapshots_maturity_index."""

import pytest
from unittest.mock import patch

from stashrun.snapshots_maturity_index import (
    compute_maturity_index,
    maturity_index_rank,
    maturity_index_summary,
)


def _patch_deps(snapshot_env=None, maturity="stable", lifecycle="active",
                status="ready", versions=None):
    """Return a context-manager stack that patches all external dependencies."""
    if versions is None:
        versions = [{"version": 1}]
    patches = [
        patch("stashrun.snapshots_maturity_index.get_snapshot",
              return_value=snapshot_env),
        patch("stashrun.snapshots_maturity_index.get_maturity",
              return_value=maturity),
        patch("stashrun.snapshots_maturity_index.get_lifecycle",
              return_value=lifecycle),
        patch("stashrun.snapshots_maturity_index.get_status",
              return_value=status),
        patch("stashrun.snapshots_maturity_index.list_versions",
              return_value=versions),
        patch("stashrun.snapshots_maturity_index.list_snapshots",
              return_value=["snap1"]),
    ]
    return patches


def test_compute_maturity_index_missing_returns_none():
    with patch("stashrun.snapshots_maturity_index.get_snapshot", return_value=None):
        assert compute_maturity_index("ghost") is None


def test_compute_maturity_index_returns_dict():
    patches = _patch_deps(snapshot_env={"K": "v"})
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_maturity_index("snap1")
    assert isinstance(result, dict)
    assert result["name"] == "snap1"
    assert "total" in result


def test_compute_maturity_index_stable_active_ready():
    patches = _patch_deps(snapshot_env={"K": "v"}, maturity="stable",
                          lifecycle="active", status="ready", versions=[{}, {}])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_maturity_index("snap1")
    # stable=80, active=30, ready=30, 2 versions=10 => 150
    assert result["total"] == 150
    assert result["maturity_score"] == 80
    assert result["lifecycle_score"] == 30
    assert result["status_score"] == 30
    assert result["version_score"] == 10


def test_compute_maturity_index_experimental_draft_unknown():
    patches = _patch_deps(snapshot_env={"K": "v"}, maturity="experimental",
                          lifecycle="draft", status="unknown", versions=[])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_maturity_index("snap1")
    assert result["total"] == 0


def test_compute_maturity_index_version_score_capped_at_20():
    many_versions = [{} for _ in range(10)]
    patches = _patch_deps(snapshot_env={"K": "v"}, maturity="experimental",
                          lifecycle="draft", status="unknown", versions=many_versions)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        result = compute_maturity_index("snap1")
    assert result["version_score"] == 20


def test_maturity_index_rank_sorted_descending():
    call_count = 0
    totals = [40, 150, 80]
    names = ["a", "b", "c"]

    def fake_get_snapshot(name):
        return {"K": "v"}

    def fake_maturity(name, default=None):
        idx = names.index(name)
        return ["experimental", "stable", "beta"][idx]

    def fake_lifecycle(name, default=None):
        return "draft"

    def fake_status(name, default=None):
        return "unknown"

    def fake_versions(name):
        idx = names.index(name)
        return [{}] * [0, 4, 0][idx]

    with patch("stashrun.snapshots_maturity_index.list_snapshots", return_value=names), \
         patch("stashrun.snapshots_maturity_index.get_snapshot", side_effect=fake_get_snapshot), \
         patch("stashrun.snapshots_maturity_index.get_maturity", side_effect=fake_maturity), \
         patch("stashrun.snapshots_maturity_index.get_lifecycle", side_effect=fake_lifecycle), \
         patch("stashrun.snapshots_maturity_index.get_status", side_effect=fake_status), \
         patch("stashrun.snapshots_maturity_index.list_versions", side_effect=fake_versions):
        ranked = maturity_index_rank()
    assert ranked[0]["name"] == "b"
    assert ranked[0]["total"] >= ranked[1]["total"]


def test_maturity_index_summary_empty():
    with patch("stashrun.snapshots_maturity_index.list_snapshots", return_value=[]):
        summary = maturity_index_summary()
    assert summary["count"] == 0
    assert summary["average"] == 0.0
    assert summary["top"] is None
