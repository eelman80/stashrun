"""Tests for stashrun/profiles.py"""

from __future__ import annotations

import pytest

from stashrun import profiles as prof


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def test_create_profile_new():
    assert prof.create_profile("dev") is True
    assert "dev" in prof.list_profiles()


def test_create_profile_duplicate():
    prof.create_profile("dev")
    assert prof.create_profile("dev") is False


def test_delete_profile_existing():
    prof.create_profile("staging")
    assert prof.delete_profile("staging") is True
    assert "staging" not in prof.list_profiles()


def test_delete_profile_missing():
    assert prof.delete_profile("nonexistent") is False


def test_add_snapshot_to_profile_creates_profile():
    assert prof.add_snapshot_to_profile("ci", "snap1") is True
    assert "ci" in prof.list_profiles()
    assert "snap1" in prof.get_profile("ci")


def test_add_snapshot_duplicate():
    prof.add_snapshot_to_profile("ci", "snap1")
    assert prof.add_snapshot_to_profile("ci", "snap1") is False


def test_add_multiple_snapshots():
    prof.add_snapshot_to_profile("prod", "snap_a")
    prof.add_snapshot_to_profile("prod", "snap_b")
    result = prof.get_profile("prod")
    assert "snap_a" in result
    assert "snap_b" in result


def test_remove_snapshot_existing():
    prof.add_snapshot_to_profile("qa", "snap_x")
    assert prof.remove_snapshot_from_profile("qa", "snap_x") is True
    assert prof.get_profile("qa") == []


def test_remove_snapshot_missing():
    prof.create_profile("qa")
    assert prof.remove_snapshot_from_profile("qa", "ghost") is False


def test_remove_snapshot_missing_profile():
    assert prof.remove_snapshot_from_profile("no_profile", "snap") is False


def test_get_profile_missing_returns_none():
    assert prof.get_profile("missing") is None


def test_list_profiles_empty():
    assert prof.list_profiles() == []


def test_list_profiles_multiple():
    prof.create_profile("alpha")
    prof.create_profile("beta")
    names = prof.list_profiles()
    assert "alpha" in names
    assert "beta" in names
