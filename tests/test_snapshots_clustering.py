"""Tests for stashrun.snapshots_clustering."""

import pytest
from unittest.mock import patch

from stashrun.snapshots_clustering import (
    jaccard_similarity,
    cluster_snapshots,
    cluster_summary,
    find_cluster,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENVS = {
    "alpha": {"A": "1", "B": "2", "C": "3"},
    "beta":  {"A": "1", "B": "2", "D": "4"},
    "gamma": {"X": "9", "Y": "8"},
    "delta": {"X": "9", "Y": "8", "Z": "7"},
}


def _fake_list():
    return list(_ENVS.keys())


def _fake_get(name):
    return _ENVS.get(name)


@pytest.fixture(autouse=True)
def mock_deps(monkeypatch):
    monkeypatch.setattr(
        "stashrun.snapshots_clustering.list_all_snapshots", _fake_list
    )
    monkeypatch.setattr(
        "stashrun.snapshots_clustering.get_snapshot", _fake_get
    )


# ---------------------------------------------------------------------------
# jaccard_similarity
# ---------------------------------------------------------------------------

def test_jaccard_identical_sets():
    assert jaccard_similarity({"A", "B"}, {"A", "B"}) == 1.0


def test_jaccard_disjoint_sets():
    assert jaccard_similarity({"A"}, {"B"}) == 0.0


def test_jaccard_partial_overlap():
    result = jaccard_similarity({"A", "B", "C"}, {"A", "B", "D"})
    assert abs(result - 0.5) < 1e-9


def test_jaccard_both_empty():
    assert jaccard_similarity(set(), set()) == 1.0


# ---------------------------------------------------------------------------
# cluster_snapshots
# ---------------------------------------------------------------------------

def test_cluster_snapshots_returns_dict():
    result = cluster_snapshots(threshold=0.5)
    assert isinstance(result, dict)


def test_cluster_snapshots_all_names_assigned():
    result = cluster_snapshots(threshold=0.5)
    all_members = [m for members in result.values() for m in members]
    assert set(all_members) == set(_ENVS.keys())


def test_cluster_snapshots_similar_together():
    """alpha and beta share 2/4 keys -> Jaccard 0.5, should cluster."""
    result = cluster_snapshots(threshold=0.5)
    all_members = [m for members in result.values() for m in members]
    # alpha and beta must end up in the same cluster
    for members in result.values():
        if "alpha" in members:
            assert "beta" in members
            break


def test_cluster_snapshots_dissimilar_separate():
    """alpha/beta and gamma/delta share no keys, must be separate clusters."""
    result = cluster_snapshots(threshold=0.5)
    for members in result.values():
        if "alpha" in members:
            assert "gamma" not in members
            assert "delta" not in members


# ---------------------------------------------------------------------------
# cluster_summary
# ---------------------------------------------------------------------------

def test_cluster_summary_sorted_by_size_desc():
    summary = cluster_summary(threshold=0.5)
    sizes = [c["size"] for c in summary]
    assert sizes == sorted(sizes, reverse=True)


def test_cluster_summary_has_required_keys():
    summary = cluster_summary(threshold=0.5)
    for entry in summary:
        assert "representative" in entry
        assert "size" in entry
        assert "members" in entry


# ---------------------------------------------------------------------------
# find_cluster
# ---------------------------------------------------------------------------

def test_find_cluster_returns_list_containing_name():
    result = find_cluster("alpha")
    assert result is not None
    assert "alpha" in result


def test_find_cluster_missing_returns_none():
    result = find_cluster("nonexistent")
    assert result is None


def test_find_cluster_groups_similar():
    result = find_cluster("beta")
    assert result is not None
    assert "alpha" in result
