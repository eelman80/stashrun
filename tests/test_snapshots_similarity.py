"""Tests for snapshots_similarity module."""

import pytest
from unittest.mock import patch

from stashrun.snapshots_similarity import compute_similarity, find_similar, similarity_matrix


ENV_A = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true", "DB": "postgres"}
ENV_B = {"HOST": "localhost", "PORT": "9090", "DEBUG": "true", "CACHE": "redis"}
ENV_C = {"FOO": "bar", "BAZ": "qux"}


def _fake_get(name):
    return {"snap_a": ENV_A, "snap_b": ENV_B, "snap_c": ENV_C}.get(name)


@pytest.fixture
def mock_get(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_similarity.get_snapshot", _fake_get)


def test_compute_similarity_missing_returns_none(mock_get):
    assert compute_similarity("snap_a", "nonexistent") is None


def test_compute_similarity_returns_dict(mock_get):
    result = compute_similarity("snap_a", "snap_b")
    assert isinstance(result, dict)
    assert result["snapshot_a"] == "snap_a"
    assert result["snapshot_b"] == "snap_b"


def test_compute_similarity_shared_keys(mock_get):
    result = compute_similarity("snap_a", "snap_b")
    assert set(result["shared_keys"]) == {"HOST", "PORT", "DEBUG"}


def test_compute_similarity_key_overlap(mock_get):
    # snap_a has 4 keys, snap_b has 4 keys, union=5, shared=3
    result = compute_similarity("snap_a", "snap_b")
    assert result["key_overlap"] == round(3 / 5, 4)


def test_compute_similarity_value_overlap(mock_get):
    # shared keys: HOST matches, PORT differs, DEBUG matches => 2/3
    result = compute_similarity("snap_a", "snap_b")
    assert result["value_overlap"] == round(2 / 3, 4)


def test_compute_similarity_score_range(mock_get):
    result = compute_similarity("snap_a", "snap_b")
    assert 0.0 <= result["score"] <= 100.0


def test_compute_similarity_no_overlap(mock_get):
    result = compute_similarity("snap_a", "snap_c")
    assert result["key_overlap"] == 0.0
    assert result["score"] == 0.0


def test_find_similar_returns_above_threshold(mock_get, monkeypatch):
    monkeypatch.setattr(
        "stashrun.snapshots_similarity.list_snapshots",
        lambda: ["snap_a", "snap_b", "snap_c"]
    )
    results = find_similar("snap_a", threshold=0.0)
    names = [r["snapshot_b"] for r in results]
    assert "snap_b" in names
    assert "snap_a" not in names


def test_find_similar_excludes_self(mock_get, monkeypatch):
    monkeypatch.setattr(
        "stashrun.snapshots_similarity.list_snapshots",
        lambda: ["snap_a", "snap_b"]
    )
    results = find_similar("snap_a", threshold=0.0)
    assert all(r["snapshot_b"] != "snap_a" for r in results)


def test_similarity_matrix_returns_pairs(mock_get):
    pairs = similarity_matrix(["snap_a", "snap_b", "snap_c"])
    assert len(pairs) == 3
    pair_names = {(p["snapshot_a"], p["snapshot_b"]) for p in pairs}
    assert ("snap_a", "snap_b") in pair_names


def test_similarity_matrix_sorted_descending(mock_get):
    pairs = similarity_matrix(["snap_a", "snap_b", "snap_c"])
    scores = [p["score"] for p in pairs]
    assert scores == sorted(scores, reverse=True)
