"""Tests for stashrun.cli_ownership."""

import pytest
from unittest.mock import patch
import stashrun.snapshots_ownership as own
from stashrun.cli_ownership import (
    cmd_owner_set,
    cmd_owner_get,
    cmd_owner_remove,
    cmd_owner_list,
)


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(own, "get_stash_dir", lambda: tmp_path)
    return tmp_path


def _ns(**kwargs):
    import argparse
    return argparse.Namespace(**kwargs)


def test_cmd_owner_set_success(isolated_stash_dir, capsys):
    cmd_owner_set(_ns(name="snap1", owner="alice"))
    out = capsys.readouterr().out
    assert "alice" in out
    assert own.get_owner("snap1") == "alice"


def test_cmd_owner_get_existing(isolated_stash_dir, capsys):
    own.set_owner("snap1", "alice")
    cmd_owner_get(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "alice" in out


def test_cmd_owner_get_missing(isolated_stash_dir, capsys):
    cmd_owner_get(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No owner" in out


def test_cmd_owner_remove_existing(isolated_stash_dir, capsys):
    own.set_owner("snap1", "alice")
    cmd_owner_remove(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "removed" in out
    assert own.get_owner("snap1") is None


def test_cmd_owner_remove_missing(isolated_stash_dir, capsys):
    cmd_owner_remove(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No ownership" in out


def test_cmd_owner_list_all(isolated_stash_dir, capsys):
    own.set_owner("snap1", "alice")
    own.set_owner("snap2", "bob")
    cmd_owner_list(_ns(owner=None))
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_cmd_owner_list_filter(isolated_stash_dir, capsys):
    own.set_owner("snap1", "alice")
    own.set_owner("snap2", "bob")
    cmd_owner_list(_ns(owner="alice"))
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" not in out


def test_cmd_owner_list_empty(isolated_stash_dir, capsys):
    cmd_owner_list(_ns(owner=None))
    out = capsys.readouterr().out
    assert "No ownership" in out
