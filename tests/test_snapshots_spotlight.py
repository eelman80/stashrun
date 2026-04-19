"""Tests for snapshots_spotlight module."""

import pytest
from unittest.mock import patch

from stashrun import snapshots_spotlight as sp


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    from stashrun import storage
    monkeypatch.setattr(storage, "get_stash_dir", lambda: tmp_path)
    monkeypatch.setattr(sp, "get_stash_dir", lambda: tmp_path)
    return tmp_path


def test_spotlight_snapshot_new(isolated_stash_dir):
    result = sp.spotlight_snapshot("snap1", reason="great snapshot")
    assert result is True


def test_spotlight_snapshot_duplicate(isolated_stash_dir):
    sp.spotlight_snapshot("snap1")
    result = sp.spotlight_snapshot("snap1", reason="again")
    assert result is False


def test_get_spotlight_returns_entry(isolated_stash_dir):
    sp.spotlight_snapshot("snap1", reason="notable")
    entry = sp.get_spotlight("snap1")
    assert entry is not None
    assert entry["reason"] == "notable"


def test_get_spotlight_missing_returns_none(isolated_stash_dir):
    assert sp.get_spotlight("nonexistent") is None


def test_is_spotlighted_true(isolated_stash_dir):
    sp.spotlight_snapshot("snap1")
    assert sp.is_spotlighted("snap1") is True


def test_is_spotlighted_false(isolated_stash_dir):
    assert sp.is_spotlighted("snap1") is False


def test_remove_spotlight_existing(isolated_stash_dir):
    sp.spotlight_snapshot("snap1")
    result = sp.remove_spotlight("snap1")
    assert result is True
    assert sp.is_spotlighted("snap1") is False


def test_remove_spotlight_missing(isolated_stash_dir):
    result = sp.remove_spotlight("nonexistent")
    assert result is False


def test_list_spotlighted(isolated_stash_dir):
    sp.spotlight_snapshot("snap1")
    sp.spotlight_snapshot("snap2")
    names = sp.list_spotlighted()
    assert set(names) == {"snap1", "snap2"}


def test_clear_spotlight(isolated_stash_dir):
    sp.spotlight_snapshot("snap1")
    sp.spotlight_snapshot("snap2")
    count = sp.clear_spotlight()
    assert count == 2
    assert sp.list_spotlighted() == []


def test_clear_spotlight_empty(isolated_stash_dir):
    count = sp.clear_spotlight()
    assert count == 0
