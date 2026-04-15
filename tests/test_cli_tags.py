"""Tests for stashrun.cli_tags CLI commands."""

from __future__ import annotations

import argparse

import pytest

from stashrun import tags as tag_mod
from stashrun.cli_tags import cmd_tag_add, cmd_tag_find, cmd_tag_list, cmd_tag_remove


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / "stash"))
    yield tmp_path / "stash"


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_cmd_tag_add_success(capsys):
    rc = cmd_tag_add(_ns(snapshot="snap1", tag="prod"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "added" in out


def test_cmd_tag_add_duplicate(capsys):
    tag_mod.add_tag("snap1", "prod")
    rc = cmd_tag_add(_ns(snapshot="snap1", tag="prod"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_tag_remove_success(capsys):
    tag_mod.add_tag("snap1", "prod")
    rc = cmd_tag_remove(_ns(snapshot="snap1", tag="prod"))
    assert rc == 0
    assert "prod" not in tag_mod.get_tags("snap1")


def test_cmd_tag_remove_missing(capsys):
    rc = cmd_tag_remove(_ns(snapshot="snap1", tag="ghost"))
    assert rc == 1
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_tag_list_with_tags(capsys):
    tag_mod.add_tag("snap1", "alpha")
    tag_mod.add_tag("snap1", "beta")
    rc = cmd_tag_list(_ns(snapshot="snap1"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_tag_list_empty(capsys):
    rc = cmd_tag_list(_ns(snapshot="empty"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_find_results(capsys):
    tag_mod.add_tag("snap1", "prod")
    tag_mod.add_tag("snap2", "prod")
    rc = cmd_tag_find(_ns(tag="prod"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" in out


def test_cmd_tag_find_no_results(capsys):
    rc = cmd_tag_find(_ns(tag="missing"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No snapshots" in out
