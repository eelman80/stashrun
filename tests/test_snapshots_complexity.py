"""Tests for snapshots_complexity module."""

import pytest
from unittest.mock import patch

from stashrun import snapshots_complexity as sc


DEFAULT_ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_URL": "postgres://user:pass@host/db",
    "SECRET_KEY": "x" * 120,
}


@pytest.fixture()
def mock_deps(monkeypatch):
    monkeypatch.setattr(sc, "get_snapshot", lambda name: DEFAULT_ENV if name == "snap1" else None)
    monkeypatch.setattr(sc, "get_tags", lambda name: ["prod", "web"])


def test_compute_complexity_missing_returns_none(mock_deps):
    assert sc.compute_complexity("missing") is None


def test_compute_complexity_returns_dict(mock_deps):
    result = sc.compute_complexity("snap1")
    assert result is not None
    assert result["name"] == "snap1"
    assert result["key_count"] == 4


def test_compute_complexity_long_values(mock_deps):
    result = sc.compute_complexity("snap1")
    assert "SECRET_KEY" in result["long_value_keys"]


def test_compute_complexity_prefix_count(mock_deps):
    result = sc.compute_complexity("snap1")
    # APP, DB, SECRET -> 3 prefixes
    assert result["prefix_count"] == 3


def test_compute_complexity_tag_count(mock_deps):
    result = sc.compute_complexity("snap1")
    assert result["tag_count"] == 2


def test_compute_complexity_score_positive(mock_deps):
    result = sc.compute_complexity("snap1")
    assert result["score"] > 0


def test_complexity_rank_sorted(monkeypatch):
    def fake_get(name):
        return {"A": "1"} if name == "small" else {"A": "1", "B": "2", "C": "3"}

    monkeypatch.setattr(sc, "get_snapshot", fake_get)
    monkeypatch.setattr(sc, "get_tags", lambda n: [])
    ranked = sc.complexity_rank(["small", "large"])
    assert ranked[0]["name"] == "large"


def test_complexity_summary_empty(monkeypatch):
    monkeypatch.setattr(sc, "get_snapshot", lambda n: None)
    monkeypatch.setattr(sc, "get_tags", lambda n: [])
    summary = sc.complexity_summary(["x", "y"])
    assert summary["count"] == 0


def test_complexity_summary_values(monkeypatch):
    monkeypatch.setattr(sc, "get_snapshot", lambda n: {"K": "v"})
    monkeypatch.setattr(sc, "get_tags", lambda n: [])
    summary = sc.complexity_summary(["a", "b"])
    assert summary["count"] == 2
    assert summary["max_score"] == summary["min_score"]
