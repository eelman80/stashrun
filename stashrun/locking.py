"""Snapshot locking — prevent concurrent modifications to the same snapshot."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

_LOCK_SUFFIX = ".lock"
_LOCK_TIMEOUT = 10  # seconds
_LOCK_RETRY_INTERVAL = 0.1  # seconds


def _lock_path(snapshot_name: str) -> Path:
    return get_stash_dir() / f"{snapshot_name}{_LOCK_SUFFIX}"


def acquire_lock(snapshot_name: str, timeout: float = _LOCK_TIMEOUT) -> bool:
    """Attempt to acquire a lock for *snapshot_name*.

    Returns True if the lock was acquired, False if it timed out.
    """
    lock = _lock_path(snapshot_name)
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            # Exclusive creation — atomic on POSIX and Windows
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(_LOCK_RETRY_INTERVAL)

    return False


def release_lock(snapshot_name: str) -> bool:
    """Release the lock for *snapshot_name*.

    Returns True if the lock file was removed, False if it did not exist.
    """
    lock = _lock_path(snapshot_name)
    try:
        lock.unlink()
        return True
    except FileNotFoundError:
        return False


def is_locked(snapshot_name: str) -> bool:
    """Return True if *snapshot_name* currently holds a lock."""
    return _lock_path(snapshot_name).exists()


def lock_owner(snapshot_name: str) -> Optional[int]:
    """Return the PID stored in the lock file, or None if not locked."""
    lock = _lock_path(snapshot_name)
    try:
        return int(lock.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


class SnapshotLock:
    """Context manager that acquires and releases a snapshot lock."""

    def __init__(self, snapshot_name: str, timeout: float = _LOCK_TIMEOUT) -> None:
        self.snapshot_name = snapshot_name
        self.timeout = timeout
        self._acquired = False

    def __enter__(self) -> "SnapshotLock":
        self._acquired = acquire_lock(self.snapshot_name, self.timeout)
        if not self._acquired:
            raise TimeoutError(
                f"Could not acquire lock for snapshot '{self.snapshot_name}' "
                f"within {self.timeout}s."
            )
        return self

    def __exit__(self, *_: object) -> None:
        if self._acquired:
            release_lock(self.snapshot_name)
            self._acquired = False
