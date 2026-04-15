"""Tests for stashrun.locking."""

from __future__ import annotations

import os
import pytest

from stashrun import locking
from stashrun.storage import get_stash_dir


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_acquire_lock_creates_file(isolated_stash_dir):
    assert locking.acquire_lock("mysnap")
    lock_file = isolated_stash_dir / "mysnap.lock"
    assert lock_file.exists()
    locking.release_lock("mysnap")


def test_lock_file_contains_pid(isolated_stash_dir):
    locking.acquire_lock("mysnap")
    assert locking.lock_owner("mysnap") == os.getpid()
    locking.release_lock("mysnap")


def test_release_lock_removes_file(isolated_stash_dir):
    locking.acquire_lock("mysnap")
    released = locking.release_lock("mysnap")
    assert released is True
    assert not (isolated_stash_dir / "mysnap.lock").exists()


def test_release_lock_missing_returns_false(isolated_stash_dir):
    assert locking.release_lock("nonexistent") is False


def test_is_locked_true_when_held(isolated_stash_dir):
    locking.acquire_lock("mysnap")
    assert locking.is_locked("mysnap") is True
    locking.release_lock("mysnap")


def test_is_locked_false_when_free(isolated_stash_dir):
    assert locking.is_locked("mysnap") is False


def test_acquire_lock_fails_when_already_held(isolated_stash_dir):
    locking.acquire_lock("mysnap")
    # With timeout=0 it should fail immediately
    result = locking.acquire_lock("mysnap", timeout=0)
    assert result is False
    locking.release_lock("mysnap")


def test_lock_owner_none_when_not_locked(isolated_stash_dir):
    assert locking.lock_owner("mysnap") is None


def test_snapshot_lock_context_manager(isolated_stash_dir):
    with locking.SnapshotLock("mysnap"):
        assert locking.is_locked("mysnap")
    assert not locking.is_locked("mysnap")


def test_snapshot_lock_releases_on_exception(isolated_stash_dir):
    try:
        with locking.SnapshotLock("mysnap"):
            assert locking.is_locked("mysnap")
            raise ValueError("boom")
    except ValueError:
        pass
    assert not locking.is_locked("mysnap")


def test_snapshot_lock_timeout_raises(isolated_stash_dir):
    locking.acquire_lock("mysnap")
    with pytest.raises(TimeoutError, match="mysnap"):
        locking.SnapshotLock("mysnap", timeout=0).__enter__()
    locking.release_lock("mysnap")
