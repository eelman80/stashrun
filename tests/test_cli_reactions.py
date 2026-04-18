import pytest
from unittest.mock import patch
from stashrun.cli_reactions import (
    cmd_reaction_add, cmd_reaction_remove,
    cmd_reaction_list, cmd_reaction_clear, cmd_reaction_all
)


def _ns(**kwargs):
    import argparse
    return argparse.Namespace(**kwargs)


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_reactions.get_stash_dir", lambda: tmp_path)
    return tmp_path


def test_cmd_reaction_add_valid(isolated_stash_dir, capsys):
    cmd_reaction_add(_ns(name="snap1", reaction="👍"))
    out = capsys.readouterr().out
    assert "added" in out


def test_cmd_reaction_add_invalid(isolated_stash_dir, capsys):
    cmd_reaction_add(_ns(name="snap1", reaction="💩"))
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_cmd_reaction_remove_existing(isolated_stash_dir, capsys):
    cmd_reaction_add(_ns(name="snap1", reaction="🔥"))
    cmd_reaction_remove(_ns(name="snap1", reaction="🔥"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_reaction_remove_missing(isolated_stash_dir, capsys):
    cmd_reaction_remove(_ns(name="snap1", reaction="🔥"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_reaction_list_with_reactions(isolated_stash_dir, capsys):
    cmd_reaction_add(_ns(name="snap1", reaction="✅"))
    capsys.readouterr()
    cmd_reaction_list(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "✅" in out


def test_cmd_reaction_list_empty(isolated_stash_dir, capsys):
    cmd_reaction_list(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "No reactions" in out


def test_cmd_reaction_clear_existing(isolated_stash_dir, capsys):
    cmd_reaction_add(_ns(name="snap1", reaction="👍"))
    capsys.readouterr()
    cmd_reaction_clear(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "cleared" in out


def test_cmd_reaction_all_empty(isolated_stash_dir, capsys):
    cmd_reaction_all(_ns())
    out = capsys.readouterr().out
    assert "No reactions" in out
