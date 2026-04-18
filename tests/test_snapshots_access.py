"""Tests for stashrun.snapshots_access."""

import time
import pytest
from unittest.mock import patch
from pathlib import Path

from stashrun import snapshots_access as sa


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_record_access_returns_timestamp():
    ts = sa.record_access("snap1")
    assert isinstance(ts, float)
    assert ts <= time.time()


def test_get_last_accessed_after_record():
    sa.record_access("snap1")
    ts = sa.get_last_accessed("snap1")
    assert ts is not None
    assert ts <= time.time()


def test_get_last_accessed_missing_returns_none():
    assert sa.get_last_accessed("ghost") is None


def test_record_access_overwrites_previous():
    sa.record_access("snap1")
    ts1 = sa.get_last_accessed("snap1")
    time.sleep(0.01)
    sa.record_access("snap1")
    ts2 = sa.get_last_accessed("snap1")
    assert ts2 >= ts1


def test_remove_access_existing():
    sa.record_access("snap1")
    result = sa.remove_access("snap1")
    assert result is True
    assert sa.get_last_accessed("snap1") is None


def test_remove_access_missing_returns_false():
    assert sa.remove_access("nope") is False


def test_list_accessed_sorted_by_recency():
    sa.record_access("a")
    time.sleep(0.01)
    sa.record_access("b")
    time.sleep(0.01)
    sa.record_access("c")
    result = sa.list_accessed()
    names = [r[0] for r in result]
    assert names[0] == "c"
    assert names[1] == "b"
    assert names[2] == "a"


def test_list_accessed_limit():
    for i in range(5):
        sa.record_access(f"snap{i}")
        time.sleep(0.005)
    result = sa.list_accessed(limit=3)
    assert len(result) == 3


def test_never_accessed_returns_unrecorded():
    sa.record_access("seen")
    result = sa.never_accessed(["seen", "unseen1", "unseen2"])
    assert "unseen1" in result
    assert "unseen2" in result
    assert "seen" not in result


def test_never_accessed_all_seen():
    sa.record_access("x")
    sa.record_access("y")
    assert sa.never_accessed(["x", "y"]) == []
