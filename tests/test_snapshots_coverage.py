"""Tests for stashrun.snapshots_coverage."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_coverage import compute_coverage, coverage_rank, coverage_summary


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}
ENV_B = {"DB_HOST": "prod", "REDIS_URL": "redis://localhost"}
ENV_C = {"DB_HOST": "staging", "DB_PORT": "5433", "API_KEY": "s2", "LOG_LEVEL": "debug"}


def _fake_get(name):
    return {"snap_a": ENV_A, "snap_b": ENV_B, "snap_c": ENV_C}.get(name)


@pytest.fixture()
def mock_get(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_coverage.get_snapshot", _fake_get)
    monkeypatch.setattr(
        "stashrun.snapshots_coverage.list_all_snapshots",
        lambda: ["snap_a", "snap_b", "snap_c"],
    )


def test_compute_coverage_missing_returns_none(mock_get):
    assert compute_coverage("nonexistent", ["DB_HOST"]) is None


def test_compute_coverage_empty_reference_returns_none(mock_get):
    assert compute_coverage("snap_a", []) is None


def test_compute_coverage_full_match(mock_get):
    result = compute_coverage("snap_a", ["DB_HOST", "DB_PORT", "API_KEY"])
    assert result is not None
    assert result["coverage_pct"] == 100.0
    assert result["missing"] == []
    assert result["extra"] == []


def test_compute_coverage_partial_match(mock_get):
    result = compute_coverage("snap_b", ["DB_HOST", "DB_PORT", "API_KEY"])
    assert result is not None
    assert result["coverage_pct"] == pytest.approx(100 / 3, rel=1e-2)
    assert "DB_PORT" in result["missing"]
    assert "API_KEY" in result["missing"]
    assert "REDIS_URL" in result["extra"]


def test_compute_coverage_covered_and_missing_sorted(mock_get):
    result = compute_coverage("snap_a", ["API_KEY", "DB_HOST", "MISSING_KEY"])
    assert result["covered"] == sorted(result["covered"])
    assert result["missing"] == sorted(result["missing"])


def test_compute_coverage_extra_keys_reported(mock_get):
    result = compute_coverage("snap_c", ["DB_HOST", "DB_PORT"])
    assert result is not None
    assert set(result["extra"]) == {"API_KEY", "LOG_LEVEL"}


def test_coverage_rank_orders_by_pct_descending(mock_get):
    ref = ["DB_HOST", "DB_PORT", "API_KEY"]
    ranked = coverage_rank(ref)
    pcts = [r["coverage_pct"] for r in ranked]
    assert pcts == sorted(pcts, reverse=True)


def test_coverage_rank_specific_names(mock_get):
    ref = ["DB_HOST", "DB_PORT", "API_KEY"]
    ranked = coverage_rank(ref, names=["snap_a", "snap_b"])
    assert len(ranked) == 2
    names = [r["name"] for r in ranked]
    assert "snap_a" in names and "snap_b" in names


def test_coverage_rank_skips_missing_snapshot(mock_get):
    ref = ["DB_HOST"]
    ranked = coverage_rank(ref, names=["snap_a", "nonexistent"])
    assert all(r["name"] != "nonexistent" for r in ranked)


def test_coverage_summary_returns_counts(mock_get):
    ref = ["DB_HOST", "DB_PORT", "API_KEY"]
    summary = coverage_summary(ref)
    assert summary["count"] == 3
    assert 0.0 <= summary["avg_coverage_pct"] <= 100.0
    assert summary["full_coverage"] >= 1  # snap_a and snap_c both cover all three


def test_coverage_summary_empty_when_no_snapshots(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_coverage.get_snapshot", lambda n: None)
    monkeypatch.setattr("stashrun.snapshots_coverage.list_all_snapshots", lambda: [])
    summary = coverage_summary(["DB_HOST"])
    assert summary == {"count": 0, "avg_coverage_pct": 0.0, "full_coverage": 0}
