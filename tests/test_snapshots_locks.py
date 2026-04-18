import pytest
from unittest.mock import patch
import stashrun.snapshots_locks as sl


@pytest.fixture
def isolated_stash_dir(tmp_path):
    with patch("stashrun.snapshots_locks.get_stash_dir", return_value=tmp_path):
        yield tmp_path


def test_lock_snapshot_new(isolated_stash_dir):
    assert sl.lock_snapshot("snap1") is True


def test_lock_snapshot_duplicate(isolated_stash_dir):
    sl.lock_snapshot("snap1")
    assert sl.lock_snapshot("snap1") is False


def test_lock_snapshot_with_reason(isolated_stash_dir):
    sl.lock_snapshot("snap1", reason="production")
    info = sl.get_lock_info("snap1")
    assert info["reason"] == "production"


def test_unlock_existing(isolated_stash_dir):
    sl.lock_snapshot("snap1")
    assert sl.unlock_snapshot("snap1") is True


def test_unlock_missing(isolated_stash_dir):
    assert sl.unlock_snapshot("snap1") is False


def test_is_snapshot_locked_true(isolated_stash_dir):
    sl.lock_snapshot("snap1")
    assert sl.is_snapshot_locked("snap1") is True


def test_is_snapshot_locked_false(isolated_stash_dir):
    assert sl.is_snapshot_locked("snap1") is False


def test_get_lock_info_missing_returns_none(isolated_stash_dir):
    assert sl.get_lock_info("missing") is None


def test_list_locked(isolated_stash_dir):
    sl.lock_snapshot("a")
    sl.lock_snapshot("b")
    locked = sl.list_locked()
    assert set(locked) == {"a", "b"}


def test_clear_all_locks(isolated_stash_dir):
    sl.lock_snapshot("a")
    sl.lock_snapshot("b")
    count = sl.clear_all_locks()
    assert count == 2
    assert sl.list_locked() == []


def test_unlock_after_clear_returns_false(isolated_stash_dir):
    sl.lock_snapshot("a")
    sl.clear_all_locks()
    assert sl.unlock_snapshot("a") is False
