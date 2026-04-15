"""Tests for stashrun.aliases and stashrun.cli_aliases."""

from __future__ import annotations

import argparse
import pytest

from stashrun import aliases as alias_mod
from stashrun.cli_aliases import (
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_rename,
    cmd_alias_resolve,
    cmd_alias_set,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(alias_mod, "get_stash_dir", lambda: tmp_path)
    yield tmp_path


def _ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


# --- unit tests for aliases module ---

def test_set_alias_creates_entry():
    assert alias_mod.set_alias("prod", "snap-001") is True
    assert alias_mod.resolve_alias("prod") == "snap-001"


def test_set_alias_overwrites():
    alias_mod.set_alias("prod", "snap-001")
    alias_mod.set_alias("prod", "snap-002")
    assert alias_mod.resolve_alias("prod") == "snap-002"


def test_resolve_missing_returns_none():
    assert alias_mod.resolve_alias("ghost") is None


def test_remove_alias_existing():
    alias_mod.set_alias("dev", "snap-010")
    assert alias_mod.remove_alias("dev") is True
    assert alias_mod.resolve_alias("dev") is None


def test_remove_alias_missing():
    assert alias_mod.remove_alias("nope") is False


def test_list_aliases_empty():
    assert alias_mod.list_aliases() == {}


def test_list_aliases_multiple():
    alias_mod.set_alias("a", "snap-1")
    alias_mod.set_alias("b", "snap-2")
    result = alias_mod.list_aliases()
    assert result == {"a": "snap-1", "b": "snap-2"}


def test_rename_alias_success():
    alias_mod.set_alias("old", "snap-99")
    assert alias_mod.rename_alias("old", "new") is True
    assert alias_mod.resolve_alias("new") == "snap-99"
    assert alias_mod.resolve_alias("old") is None


def test_rename_alias_missing():
    assert alias_mod.rename_alias("ghost", "new") is False


# --- CLI command tests ---

def test_cmd_alias_set_output(capsys):
    cmd_alias_set(_ns(alias="staging", snapshot="snap-42"))
    assert "staging" in capsys.readouterr().out


def test_cmd_alias_remove_success(capsys):
    alias_mod.set_alias("tmp", "snap-5")
    cmd_alias_remove(_ns(alias="tmp"))
    assert "removed" in capsys.readouterr().out


def test_cmd_alias_remove_missing(capsys):
    cmd_alias_remove(_ns(alias="missing"))
    assert "not found" in capsys.readouterr().out


def test_cmd_alias_resolve_found(capsys):
    alias_mod.set_alias("live", "snap-7")
    cmd_alias_resolve(_ns(alias="live"))
    assert "snap-7" in capsys.readouterr().out


def test_cmd_alias_list_empty(capsys):
    cmd_alias_list(_ns())
    assert "No aliases" in capsys.readouterr().out


def test_cmd_alias_rename_success(capsys):
    alias_mod.set_alias("x", "snap-3")
    cmd_alias_rename(_ns(old="x", new="y"))
    assert "renamed" in capsys.readouterr().out
