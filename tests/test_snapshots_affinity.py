"""Tests for stashrun.snapshots_affinity."""

from unittest.mock import patch

import pytest

from stashrun.snapshots_affinity import compute_affinity, affinity_rank, affinity_summary


_SNAP_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod"}
_SNAP_B = {"DB_HOST": "remote", "DB_PORT": "5432", "CACHE_URL": "redis://"}
_SNAP_C = {"UNRELATED_KEY": "value"}


@pytest.fixture()
def mock_deps(monkeypatch):
    def _fake_get(name):
        return {"snap_a": _SNAP_A, "snap_b": _SNAP_B, "snap_c": _SNAP_C}.get(name)

    def _fake_profile(profile):
        return {"db_profile": ["snap_a", "snap_b"]}.get(profile, [])

    def _fake_list():
        return ["snap_a", "snap_b", "snap_c"]

    monkeypatch.setattr("stashrun.snapshots_affinity.get_snapshot", _fake_get)
    monkeypatch.setattr("stashrun.snapshots_affinity.get_profile_snapshots", _fake_profile)
    monkeypatch.setattr("stashrun.snapshots_affinity.list_snapshots", _fake_list)


def test_compute_affinity_missing_snapshot_returns_none(mock_deps):
    result = compute_affinity("nonexistent", "db_profile")
    assert result is None


def test_compute_affinity_returns_dict(mock_deps):
    result = compute_affinity("snap_a", "db_profile")
    assert result is not None
    assert result["snapshot"] == "snap_a"
    assert result["profile"] == "db_profile"
    assert "score" in result


def test_compute_affinity_score_range(mock_deps):
    result = compute_affinity("snap_a", "db_profile")
    assert 0.0 <= result["score"] <= 100.0


def test_compute_affinity_shared_keys_counted(mock_deps):
    result = compute_affinity("snap_a", "db_profile")
    # snap_a keys: DB_HOST, DB_PORT, APP_ENV
    # profile key union (snap_a + snap_b): DB_HOST, DB_PORT, APP_ENV, CACHE_URL
    # shared = DB_HOST, DB_PORT, APP_ENV => 3
    assert result["shared_keys"] == 3


def test_compute_affinity_low_overlap_snapshot(mock_deps):
    result = compute_affinity("snap_c", "db_profile")
    assert result["score"] < 20.0
    assert result["shared_keys"] == 0


def test_compute_affinity_empty_profile_returns_zero(mock_deps):
    result = compute_affinity("snap_a", "unknown_profile")
    assert result["score"] == 0


def test_affinity_rank_returns_list_sorted_descending(mock_deps):
    ranked = affinity_rank("db_profile")
    assert isinstance(ranked, list)
    assert len(ranked) == 3
    scores = [r["score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_affinity_rank_top_entry_is_highest(mock_deps):
    ranked = affinity_rank("db_profile")
    assert ranked[0]["score"] >= ranked[-1]["score"]


def test_affinity_summary_returns_dict(mock_deps):
    summary = affinity_summary("db_profile")
    assert summary["profile"] == "db_profile"
    assert summary["count"] == 3
    assert isinstance(summary["avg_score"], float)
    assert summary["top"] is not None


def test_affinity_summary_empty_list(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_affinity.list_snapshots", lambda: [])
    monkeypatch.setattr("stashrun.snapshots_affinity.get_snapshot", lambda n: None)
    monkeypatch.setattr("stashrun.snapshots_affinity.get_profile_snapshots", lambda p: [])
    summary = affinity_summary("any_profile")
    assert summary["count"] == 0
    assert summary["avg_score"] == 0.0
    assert summary["top"] is None
