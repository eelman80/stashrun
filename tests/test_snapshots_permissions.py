"""Tests for snapshots_permissions module."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_permissions import (
    set_permission, get_permissions, has_permission,
    reset_permissions, list_restricted, VALID_PERMISSIONS
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_permission_valid():
    assert set_permission("snap1", "read", False) is True


def test_set_permission_invalid():
    assert set_permission("snap1", "execute", True) is False


def test_get_permissions_defaults_to_true():
    perms = get_permissions("snap1")
    assert set(perms.keys()) == VALID_PERMISSIONS
    assert all(v is True for v in perms.values())


def test_get_permissions_after_set():
    set_permission("snap1", "delete", False)
    perms = get_permissions("snap1")
    assert perms["delete"] is False
    assert perms["read"] is True


def test_has_permission_default_true():
    assert has_permission("snap1", "write") is True


def test_has_permission_after_deny():
    set_permission("snap1", "share", False)
    assert has_permission("snap1", "share") is False


def test_has_permission_unknown_returns_false():
    assert has_permission("snap1", "execute") is False


def test_reset_permissions_existing():
    set_permission("snap1", "read", False)
    assert reset_permissions("snap1") is True
    assert has_permission("snap1", "read") is True


def test_reset_permissions_missing():
    assert reset_permissions("nonexistent") is False


def test_list_restricted_returns_denied():
    set_permission("snap1", "delete", False)
    set_permission("snap2", "delete", False)
    set_permission("snap3", "delete", True)
    restricted = list_restricted("delete")
    assert "snap1" in restricted
    assert "snap2" in restricted
    assert "snap3" not in restricted


def test_list_restricted_empty():
    assert list_restricted("read") == []


def test_multiple_permissions_independent():
    set_permission("snap1", "read", False)
    set_permission("snap1", "write", False)
    perms = get_permissions("snap1")
    assert perms["read"] is False
    assert perms["write"] is False
    assert perms["delete"] is True
