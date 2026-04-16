"""Tests for stashrun.snapshots_ttl."""

import time
import pytest
from unittest.mock import patch
from pathlib import Path

from stashrun import snapshots_ttl as ttl_mod


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_ttl_creates_entry():
    ttl_mod.set_ttl("snap1", 60)
    data = ttl_mod._load_ttl()
    assert "snap1" in data
    assert data["snap1"] > time.time()


def test_get_ttl_missing_returns_none():
    assert ttl_mod.get_ttl("nonexistent") is None


def test_get_ttl_returns_expiry():
    before = time.time()
    ttl_mod.set_ttl("snap2", 100)
    expiry = ttl_mod.get_ttl("snap2")
    assert expiry is not None
    assert expiry > before + 99


def test_remove_ttl_existing():
    ttl_mod.set_ttl("snap3", 60)
    result = ttl_mod.remove_ttl("snap3")
    assert result is True
    assert ttl_mod.get_ttl("snap3") is None


def test_remove_ttl_missing_returns_false():
    assert ttl_mod.remove_ttl("ghost") is False


def test_is_expired_not_expired():
    ttl_mod.set_ttl("fresh", 3600)
    assert ttl_mod.is_expired("fresh") is False


def test_is_expired_past_expiry():
    ttl_mod.set_ttl("stale", -1)
    assert ttl_mod.is_expired("stale") is True


def test_is_expired_no_ttl_returns_false():
    assert ttl_mod.is_expired("no_ttl_snap") is False


def test_list_expired_returns_only_expired():
    ttl_mod.set_ttl("old", -10)
    ttl_mod.set_ttl("new", 3600)
    expired = ttl_mod.list_expired()
    assert "old" in expired
    assert "new" not in expired


def test_purge_expired_calls_delete_and_removes_ttl():
    ttl_mod.set_ttl("gone1", -1)
    ttl_mod.set_ttl("gone2", -1)
    ttl_mod.set_ttl("keep", 3600)

    deleted = []
    def fake_delete(name):
        deleted.append(name)

    purged = ttl_mod.purge_expired(fake_delete)
    assert set(purged) == {"gone1", "gone2"}
    assert set(deleted) == {"gone1", "gone2"}
    assert ttl_mod.get_ttl("gone1") is None
    assert ttl_mod.get_ttl("keep") is not None


def test_purge_expired_handles_delete_exception():
    ttl_mod.set_ttl("bad", -1)

    def failing_delete(name):
        raise RuntimeError("disk error")

    purged = ttl_mod.purge_expired(failing_delete)
    assert purged == []
