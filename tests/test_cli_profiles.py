"""Tests for stashrun/cli_profiles.py"""

from __future__ import annotations

import argparse
import pytest

import stashrun.profiles as prof
from stashrun.cli_profiles import (
    cmd_profile_add,
    cmd_profile_create,
    cmd_profile_delete,
    cmd_profile_list,
    cmd_profile_remove,
    cmd_profile_show,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def _ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_profile_create_success(capsys):
    cmd_profile_create(_ns(name="dev"))
    assert "created" in capsys.readouterr().out


def test_cmd_profile_create_duplicate(capsys):
    prof.create_profile("dev")
    cmd_profile_create(_ns(name="dev"))
    assert "already exists" in capsys.readouterr().out


def test_cmd_profile_delete_success(capsys):
    prof.create_profile("staging")
    cmd_profile_delete(_ns(name="staging"))
    assert "deleted" in capsys.readouterr().out


def test_cmd_profile_delete_missing(capsys):
    cmd_profile_delete(_ns(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_profile_add_success(capsys):
    cmd_profile_add(_ns(profile="ci", snapshot="snap1"))
    assert "added" in capsys.readouterr().out
    assert "snap1" in prof.get_profile("ci")


def test_cmd_profile_add_duplicate(capsys):
    prof.add_snapshot_to_profile("ci", "snap1")
    cmd_profile_add(_ns(profile="ci", snapshot="snap1"))
    assert "already in" in capsys.readouterr().out


def test_cmd_profile_remove_success(capsys):
    prof.add_snapshot_to_profile("qa", "snap_x")
    cmd_profile_remove(_ns(profile="qa", snapshot="snap_x"))
    assert "removed" in capsys.readouterr().out


def test_cmd_profile_remove_missing(capsys):
    prof.create_profile("qa")
    cmd_profile_remove(_ns(profile="qa", snapshot="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_profile_show_lists_snapshots(capsys):
    prof.add_snapshot_to_profile("prod", "snap_a")
    prof.add_snapshot_to_profile("prod", "snap_b")
    cmd_profile_show(_ns(name="prod"))
    out = capsys.readouterr().out
    assert "snap_a" in out
    assert "snap_b" in out


def test_cmd_profile_show_empty(capsys):
    prof.create_profile("empty")
    cmd_profile_show(_ns(name="empty"))
    assert "empty" in capsys.readouterr().out


def test_cmd_profile_show_missing(capsys):
    cmd_profile_show(_ns(name="missing"))
    assert "not found" in capsys.readouterr().out


def test_cmd_profile_list(capsys):
    prof.create_profile("alpha")
    prof.create_profile("beta")
    cmd_profile_list(_ns())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_profile_list_empty(capsys):
    cmd_profile_list(_ns())
    assert "No profiles" in capsys.readouterr().out
