import pytest
from unittest.mock import patch
from stashrun import snapshots_status as ss


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_status_valid(isolated_stash_dir):
    assert ss.set_status("snap1", "paused") is True
    assert ss.get_status("snap1") == "paused"


def test_set_status_invalid(isolated_stash_dir):
    assert ss.set_status("snap1", "unknown") is False
    assert ss.get_status("snap1") == ss.DEFAULT_STATUS


def test_get_status_default(isolated_stash_dir):
    assert ss.get_status("nonexistent") == "active"


def test_get_status_custom_default(isolated_stash_dir):
    assert ss.get_status("nonexistent", default="draft") == "draft"


def test_set_status_overwrites(isolated_stash_dir):
    ss.set_status("snap1", "paused")
    ss.set_status("snap1", "deprecated")
    assert ss.get_status("snap1") == "deprecated"


def test_remove_status_existing(isolated_stash_dir):
    ss.set_status("snap1", "draft")
    assert ss.remove_status("snap1") is True
    assert ss.get_status("snap1") == ss.DEFAULT_STATUS


def test_remove_status_missing(isolated_stash_dir):
    assert ss.remove_status("ghost") is False


def test_list_statuses_empty(isolated_stash_dir):
    assert ss.list_statuses() == {}


def test_list_statuses_populated(isolated_stash_dir):
    ss.set_status("a", "active")
    ss.set_status("b", "paused")
    result = ss.list_statuses()
    assert result == {"a": "active", "b": "paused"}


def test_find_by_status_match(isolated_stash_dir):
    ss.set_status("a", "deprecated")
    ss.set_status("b", "active")
    ss.set_status("c", "deprecated")
    found = ss.find_by_status("deprecated")
    assert sorted(found) == ["a", "c"]


def test_find_by_status_no_match(isolated_stash_dir):
    ss.set_status("a", "active")
    assert ss.find_by_status("draft") == []
