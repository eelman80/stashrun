"""Tests for stashrun.cli_attribution."""

from __future__ import annotations

import pytest
from argparse import Namespace

from stashrun.cli_attribution import (
    cmd_attribution_add_contributor,
    cmd_attribution_find,
    cmd_attribution_get,
    cmd_attribution_list,
    cmd_attribution_remove,
    cmd_attribution_set,
)
from stashrun.snapshots_attribution import set_attribution


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def _ns(**kwargs) -> Namespace:
    return Namespace(**kwargs)


def test_cmd_attribution_set_success(capsys):
    cmd_attribution_set(_ns(name="snap1", author="alice", contributors=None, source=None))
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "alice" in out


def test_cmd_attribution_get_existing(capsys):
    set_attribution("snap2", "bob", contributors=["carol"], source="manual")
    cmd_attribution_get(_ns(name="snap2"))
    out = capsys.readouterr().out
    assert "bob" in out
    assert "carol" in out
    assert "manual" in out


def test_cmd_attribution_get_missing(capsys):
    cmd_attribution_get(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No attribution" in out


def test_cmd_attribution_add_contributor_success(capsys):
    set_attribution("snap3", "alice")
    cmd_attribution_add_contributor(_ns(name="snap3", contributor="dave"))
    out = capsys.readouterr().out
    assert "dave" in out
    assert "snap3" in out


def test_cmd_attribution_add_contributor_missing_entry(capsys):
    cmd_attribution_add_contributor(_ns(name="no-snap", contributor="eve"))
    out = capsys.readouterr().out
    assert "No attribution entry" in out


def test_cmd_attribution_remove_existing(capsys):
    set_attribution("snap4", "alice")
    cmd_attribution_remove(_ns(name="snap4"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_attribution_remove_missing(capsys):
    cmd_attribution_remove(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No attribution entry" in out


def test_cmd_attribution_list_empty(capsys):
    cmd_attribution_list(_ns())
    out = capsys.readouterr().out
    assert "No attribution" in out


def test_cmd_attribution_list_shows_entries(capsys):
    set_attribution("a", "alice")
    set_attribution("b", "bob")
    cmd_attribution_list(_ns())
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_cmd_attribution_find_match(capsys):
    set_attribution("s1", "frank")
    set_attribution("s2", "frank")
    cmd_attribution_find(_ns(author="frank"))
    out = capsys.readouterr().out
    assert "s1" in out
    assert "s2" in out


def test_cmd_attribution_find_no_match(capsys):
    cmd_attribution_find(_ns(author="nobody"))
    out = capsys.readouterr().out
    assert "No snapshots" in out
