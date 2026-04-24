"""Tests for stashrun.snapshots_decay."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from stashrun.snapshots_decay import compute_decay, decay_rank, decay_summary


def _patch_deps(
    snapshot_env=None,
    last_accessed=None,
    ttl=None,
    status="active",
    pinned=None,
):
    """Return a context-manager stack that patches all external dependencies."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with patch("stashrun.snapshots_decay.get_snapshot", return_value=snapshot_env), \
             patch("stashrun.snapshots_decay.get_last_accessed", return_value=last_accessed), \
             patch("stashrun.snapshots_decay.get_ttl", return_value=ttl), \
             patch("stashrun.snapshots_decay.get_status", return_value=status), \
             patch("stashrun.snapshots_decay.get_pinned", return_value=set(pinned or [])), \
             patch("stashrun.snapshots_decay.list_all_snapshots", return_value=list(pinned or [])):
            yield

    return _ctx()


def test_compute_decay_missing_returns_none():
    with patch("stashrun.snapshots_decay.get_snapshot", return_value=None):
        result = compute_decay("ghost")
    assert result is None


def test_compute_decay_never_accessed_adds_50():
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=None, status="active"):
        result = compute_decay("snap")
    assert result is not None
    assert result["decay"] >= 50
    assert "never accessed" in result["reasons"]


def test_compute_decay_recent_access_low_score():
    recent = time.time() - 60  # 1 minute ago
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=recent, status="active"):
        result = compute_decay("snap")
    assert result is not None
    assert result["decay"] < 10


def test_compute_decay_expired_ttl_adds_30():
    past_ttl = time.time() - 1
    recent = time.time() - 60
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=recent, ttl=past_ttl, status="active"):
        result = compute_decay("snap")
    assert result is not None
    assert result["decay"] >= 30
    assert "TTL expired" in result["reasons"]


def test_compute_decay_deprecated_status_adds_20():
    recent = time.time() - 60
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=recent, status="deprecated"):
        result = compute_decay("snap")
    assert result is not None
    assert result["decay"] >= 20
    assert any("deprecated" in r for r in result["reasons"])


def test_compute_decay_pinned_reduces_score():
    # Never accessed (50) but pinned should reduce by 20
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=None, status="active", pinned=["snap"]):
        with patch("stashrun.snapshots_decay.list_all_snapshots", return_value=[]):
            result = compute_decay("snap")
    assert result is not None
    assert result["decay"] == 30
    assert any("pinned" in r for r in result["reasons"])


def test_compute_decay_capped_at_100():
    past = time.time() - 60 * 60 * 24 * 90  # 90 days ago
    past_ttl = time.time() - 1
    with _patch_deps(snapshot_env={"A": "1"}, last_accessed=past, ttl=past_ttl, status="deprecated"):
        result = compute_decay("snap")
    assert result is not None
    assert result["decay"] <= 100


def test_decay_rank_sorted_descending():
    names = ["a", "b", "c"]
    scores = {"a": 10, "b": 80, "c": 40}

    def _fake_compute(name):
        return {"name": name, "decay": scores[name], "reasons": []}

    with patch("stashrun.snapshots_decay.list_all_snapshots", return_value=names), \
         patch("stashrun.snapshots_decay.compute_decay", side_effect=_fake_compute):
        ranked = decay_rank()

    assert [r["name"] for r in ranked] == ["b", "c", "a"]


def test_decay_summary_empty():
    with patch("stashrun.snapshots_decay.decay_rank", return_value=[]):
        summary = decay_summary()
    assert summary["count"] == 0
    assert summary["average"] == 0.0


def test_decay_summary_correct_stats():
    fake_ranked = [
        {"name": "a", "decay": 20, "reasons": []},
        {"name": "b", "decay": 60, "reasons": []},
        {"name": "c", "decay": 40, "reasons": []},
    ]
    with patch("stashrun.snapshots_decay.decay_rank", return_value=fake_ranked):
        summary = decay_summary()
    assert summary["count"] == 3
    assert summary["average"] == 40.0
    assert summary["max"] == 60
    assert summary["min"] == 20
