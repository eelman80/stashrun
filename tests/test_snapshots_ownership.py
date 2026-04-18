"""Tests for stashrun.snapshots_ownership."""

import pytest
from unittest.mock import patch
from stashrun import snapshots_ownership as own


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.storage.get_stash_dir", lambda: tmp_path)
    monkeypatch.setattr(own, "get_stash_dir", lambda: tmp_path)
    return tmp_path


def test_set_owner_creates_entry(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    assert own.get_owner("snap1") == "alice"


def test_set_owner_overwrites(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    own.set_owner("snap1", "bob")
    assert own.get_owner("snap1") == "bob"


def test_get_owner_missing_returns_none(isolated_stash_dir):
    assert own.get_owner("nonexistent") is None


def test_remove_owner_existing(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    result = own.remove_owner("snap1")
    assert result is True
    assert own.get_owner("snap1") is None


def test_remove_owner_missing_returns_false(isolated_stash_dir):
    assert own.remove_owner("ghost") is False


def test_list_owned_by_returns_matching(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    own.set_owner("snap2", "bob")
    own.set_owner("snap3", "alice")
    result = own.list_owned_by("alice")
    assert set(result) == {"snap1", "snap3"}


def test_list_owned_by_no_match(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    assert own.list_owned_by("carol") == []


def test_list_all_owners_returns_mapping(isolated_stash_dir):
    own.set_owner("snap1", "alice")
    own.set_owner("snap2", "bob")
    result = own.list_all_owners()
    assert result == {"snap1": "alice", "snap2": "bob"}


def test_list_all_owners_empty(isolated_stash_dir):
    assert own.list_all_owners() == {}
