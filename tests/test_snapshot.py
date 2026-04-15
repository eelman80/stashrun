"""Tests for stashrun.snapshot module."""

import os
import pytest

from stashrun import storage
from stashrun.snapshot import (
    create_snapshot,
    restore_snapshot,
    get_snapshot,
    remove_snapshot,
    list_all_snapshots,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stashrun"))
    yield tmp_path / ".stashrun"


def test_create_snapshot_saves_env(monkeypatch):
    monkeypatch.setenv("SNAP_VAR", "snap_value")
    env = create_snapshot("mysnap", keys=["SNAP_VAR"])
    assert env["SNAP_VAR"] == "snap_value"
    loaded = get_snapshot("mysnap")
    assert loaded is not None
    assert loaded["SNAP_VAR"] == "snap_value"


def test_create_snapshot_with_prefix(monkeypatch):
    monkeypatch.setenv("APP_HOST", "localhost")
    monkeypatch.setenv("APP_PORT", "8080")
    monkeypatch.setenv("DB_URL", "postgres://...")
    env = create_snapshot("appsnap", prefixes=["APP_"])
    assert "APP_HOST" in env
    assert "APP_PORT" in env
    assert "DB_URL" not in env


def test_restore_snapshot_applies_env(monkeypatch):
    monkeypatch.setenv("RESTORE_ME", "before")
    create_snapshot("restore_test", keys=["RESTORE_ME"])
    monkeypatch.setenv("RESTORE_ME", "after")
    restore_snapshot("restore_test")
    assert os.environ["RESTORE_ME"] == "before"


def test_restore_snapshot_missing_returns_none():
    result = restore_snapshot("does_not_exist")
    assert result is None


def test_get_snapshot_returns_dict(monkeypatch):
    monkeypatch.setenv("GET_VAR", "get_val")
    create_snapshot("getsnap", keys=["GET_VAR"])
    snap = get_snapshot("getsnap")
    assert isinstance(snap, dict)
    assert snap["GET_VAR"] == "get_val"


def test_remove_snapshot_deletes(monkeypatch):
    monkeypatch.setenv("DEL_VAR", "x")
    create_snapshot("delsnap", keys=["DEL_VAR"])
    assert remove_snapshot("delsnap") is True
    assert get_snapshot("delsnap") is None


def test_remove_snapshot_missing_returns_false():
    assert remove_snapshot("ghost") is False


def test_list_all_snapshots(monkeypatch):
    monkeypatch.setenv("LIST_VAR", "1")
    create_snapshot("snap_a", keys=["LIST_VAR"])
    create_snapshot("snap_b", keys=["LIST_VAR"])
    names = list_all_snapshots()
    assert "snap_a" in names
    assert "snap_b" in names
