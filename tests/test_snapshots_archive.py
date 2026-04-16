"""Tests for snapshots_archive module."""

import pytest
from unittest.mock import patch
from stashrun import snapshots_archive


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_archive_snapshot_success(isolated_stash_dir):
    from stashrun.storage import save_snapshot
    save_snapshot("mysnap", {"FOO": "bar"})
    result = snapshots_archive.archive_snapshot("mysnap")
    assert result is True
    assert "mysnap" in snapshots_archive.list_archived()


def test_archive_snapshot_removes_active(isolated_stash_dir):
    from stashrun.storage import save_snapshot, load_snapshot
    save_snapshot("mysnap", {"A": "1"})
    snapshots_archive.archive_snapshot("mysnap")
    assert load_snapshot("mysnap") is None


def test_archive_snapshot_missing_returns_false(isolated_stash_dir):
    result = snapshots_archive.archive_snapshot("ghost")
    assert result is False


def test_get_archived_returns_env(isolated_stash_dir):
    from stashrun.storage import save_snapshot
    save_snapshot("snap2", {"X": "42"})
    snapshots_archive.archive_snapshot("snap2")
    env = snapshots_archive.get_archived("snap2")
    assert env == {"X": "42"}


def test_get_archived_missing_returns_none(isolated_stash_dir):
    assert snapshots_archive.get_archived("nope") is None


def test_unarchive_snapshot_restores(isolated_stash_dir):
    from stashrun.storage import save_snapshot, load_snapshot
    save_snapshot("snap3", {"K": "v"})
    snapshots_archive.archive_snapshot("snap3")
    result = snapshots_archive.unarchive_snapshot("snap3")
    assert result is True
    assert load_snapshot("snap3") == {"K": "v"}
    assert "snap3" not in snapshots_archive.list_archived()


def test_unarchive_missing_returns_false(isolated_stash_dir):
    assert snapshots_archive.unarchive_snapshot("missing") is False


def test_list_archived_empty(isolated_stash_dir):
    assert snapshots_archive.list_archived() == []


def test_purge_archived_removes_entry(isolated_stash_dir):
    from stashrun.storage import save_snapshot
    save_snapshot("snap4", {"Z": "99"})
    snapshots_archive.archive_snapshot("snap4")
    result = snapshots_archive.purge_archived("snap4")
    assert result is True
    assert snapshots_archive.get_archived("snap4") is None


def test_purge_archived_missing_returns_false(isolated_stash_dir):
    assert snapshots_archive.purge_archived("none") is False
