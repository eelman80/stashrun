"""Tests for snapshots_alignment module."""

import pytest
from unittest.mock import patch

from stashrun.snapshots_alignment import (
    compute_alignment,
    alignment_rank,
    alignment_summary,
)

_SNAP = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod"}
_TMPL = {"defaults": {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_NAME": "app"}}


@pytest.fixture()
def mock_deps(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_alignment.get_snapshot", lambda n: _SNAP if n == "snap1" else None)
    monkeypatch.setattr("stashrun.snapshots_alignment.get_template", lambda t: _TMPL if t == "base" else None)
    monkeypatch.setattr("stashrun.snapshots_alignment.list_snapshots", lambda: ["snap1"])


def test_compute_alignment_missing_snapshot(mock_deps):
    result = compute_alignment("missing", "base")
    assert result is None


def test_compute_alignment_missing_template(mock_deps):
    result = compute_alignment("snap1", "unknown_tmpl")
    assert result is None


def test_compute_alignment_returns_dict(mock_deps):
    result = compute_alignment("snap1", "base")
    assert result is not None
    assert "score" in result
    assert "matched" in result
    assert "missing" in result
    assert "extra" in result


def test_compute_alignment_matched_keys(mock_deps):
    result = compute_alignment("snap1", "base")
    assert set(result["matched"]) == {"DB_HOST", "DB_PORT"}


def test_compute_alignment_missing_keys(mock_deps):
    result = compute_alignment("snap1", "base")
    assert result["missing"] == ["DB_NAME"]


def test_compute_alignment_extra_keys(mock_deps):
    result = compute_alignment("snap1", "base")
    assert result["extra"] == ["APP_ENV"]


def test_compute_alignment_score(mock_deps):
    # 2 out of 3 template keys matched => 66
    result = compute_alignment("snap1", "base")
    assert result["score"] == 66


def test_alignment_rank_returns_list(mock_deps):
    ranked = alignment_rank("base")
    assert isinstance(ranked, list)
    assert len(ranked) == 1
    assert ranked[0][0] == "snap1"
    assert ranked[0][1] == 66


def test_alignment_rank_empty_when_no_snapshots(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_alignment.list_snapshots", lambda: [])
    monkeypatch.setattr("stashrun.snapshots_alignment.get_snapshot", lambda n: None)
    monkeypatch.setattr("stashrun.snapshots_alignment.get_template", lambda t: _TMPL)
    result = alignment_rank("base")
    assert result == []


def test_alignment_summary_returns_dict(mock_deps):
    summary = alignment_summary("base")
    assert summary["count"] == 1
    assert summary["average"] == 66.0
    assert summary["min"] == 66
    assert summary["max"] == 66


def test_alignment_summary_no_snapshots(monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_alignment.list_snapshots", lambda: [])
    monkeypatch.setattr("stashrun.snapshots_alignment.get_snapshot", lambda n: None)
    monkeypatch.setattr("stashrun.snapshots_alignment.get_template", lambda t: _TMPL)
    summary = alignment_summary("base")
    assert summary["count"] == 0
    assert summary["average"] == 0
