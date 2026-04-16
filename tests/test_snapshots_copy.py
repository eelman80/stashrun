"""Tests for snapshots_copy module."""

import os
import pytest
from stashrun import storage
from stashrun.snapshots_copy import copy_snapshot, rename_snapshot, snapshot_exists


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_stash_dir", lambda: str(tmp_path))
    return tmp_path


def test_copy_snapshot_success():
    storage.save_snapshot("alpha", {"FOO": "bar"})
    result = copy_snapshot("alpha", "alpha_copy")
    assert result is True
    assert storage.load_snapshot("alpha_copy") == {"FOO": "bar"}


def test_copy_snapshot_missing_source():
    result = copy_snapshot("nonexistent", "dst")
    assert result is False


def test_copy_snapshot_no_overwrite():
    storage.save_snapshot("a", {"X": "1"})
    storage.save_snapshot("b", {"X": "2"})
    result = copy_snapshot("a", "b", overwrite=False)
    assert result is False
    assert storage.load_snapshot("b") == {"X": "2"}


def test_copy_snapshot_with_overwrite():
    storage.save_snapshot("a", {"X": "1"})
    storage.save_snapshot("b", {"X": "old"})
    result = copy_snapshot("a", "b", overwrite=True)
    assert result is True
    assert storage.load_snapshot("b") == {"X": "1"}


def test_rename_snapshot_success():
    storage.save_snapshot("orig", {"K": "v"})
    result = rename_snapshot("orig", "renamed")
    assert result is True
    assert storage.load_snapshot("renamed") == {"K": "v"}
    assert storage.load_snapshot("orig") is None


def test_rename_snapshot_missing_source():
    result = rename_snapshot("ghost", "target")
    assert result is False


def test_rename_no_overwrite_existing_dst():
    storage.save_snapshot("src", {"A": "1"})
    storage.save_snapshot("dst", {"A": "2"})
    result = rename_snapshot("src", "dst", overwrite=False)
    assert result is False
    assert storage.load_snapshot("src") == {"A": "1"}


def test_snapshot_exists():
    storage.save_snapshot("present", {})
    assert snapshot_exists("present") is True
    assert snapshot_exists("absent") is False
