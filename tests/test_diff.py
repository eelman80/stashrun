"""Tests for stashrun.diff module."""

from __future__ import annotations

import os
import pytest

from stashrun import storage
from stashrun.snapshot import create_snapshot
from stashrun.diff import (
    compare_dicts,
    diff_snapshots,
    diff_snapshot_vs_live,
    SnapshotDiff,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_dir", lambda: tmp_path / ".stashrun")
    (tmp_path / ".stashrun").mkdir()
    return tmp_path / ".stashrun"


# ---------------------------------------------------------------------------
# compare_dicts
# ---------------------------------------------------------------------------

def test_compare_dicts_added():
    diff = compare_dicts({"A": "1"}, {"A": "1", "B": "2"})
    assert diff.added == {"B": "2"}
    assert not diff.removed
    assert not diff.changed


def test_compare_dicts_removed():
    diff = compare_dicts({"A": "1", "B": "2"}, {"A": "1"})
    assert diff.removed == {"B": "2"}
    assert not diff.added
    assert not diff.changed


def test_compare_dicts_changed():
    diff = compare_dicts({"A": "old"}, {"A": "new"})
    assert diff.changed == {"A": ("old", "new")}
    assert not diff.added
    assert not diff.removed


def test_compare_dicts_unchanged():
    diff = compare_dicts({"A": "1"}, {"A": "1"})
    assert diff.unchanged == {"A": "1"}
    assert not diff.has_changes


def test_has_changes_true():
    diff = compare_dicts({"A": "1"}, {"A": "2"})
    assert diff.has_changes


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

def test_diff_snapshots_basic(monkeypatch):
    monkeypatch.setenv("VAR_X", "hello")
    create_snapshot("snap_a", env={"VAR_X": "hello", "VAR_Y": "world"})
    create_snapshot("snap_b", env={"VAR_X": "hello", "VAR_Z": "new"})
    diff = diff_snapshots("snap_a", "snap_b")
    assert diff is not None
    assert "VAR_Y" in diff.removed
    assert "VAR_Z" in diff.added
    assert "VAR_X" in diff.unchanged


def test_diff_snapshots_missing_returns_none():
    create_snapshot("only_one", env={"K": "v"})
    result = diff_snapshots("only_one", "nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# diff_snapshot_vs_live
# ---------------------------------------------------------------------------

def test_diff_snapshot_vs_live(monkeypatch):
    monkeypatch.setenv("LIVE_VAR", "live_value")
    create_snapshot("live_test", env={"LIVE_VAR": "old_value"})
    diff = diff_snapshot_vs_live("live_test", keys=["LIVE_VAR"])
    assert diff is not None
    assert "LIVE_VAR" in diff.changed
    assert diff.changed["LIVE_VAR"] == ("old_value", "live_value")


def test_diff_snapshot_vs_live_missing_snapshot():
    result = diff_snapshot_vs_live("ghost_snapshot")
    assert result is None
