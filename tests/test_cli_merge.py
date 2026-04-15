"""Tests for stashrun.cli_merge."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from stashrun.cli_merge import cmd_merge, cmd_merge_conflicts, register_merge_commands


def _ns(**kwargs):
    defaults = {"sources": ["a", "b"], "target": "merged", "strategy": "last_wins"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# cmd_merge
# ---------------------------------------------------------------------------

@patch("stashrun.cli_merge.merge_snapshots", return_value={"A": "1", "B": "2"})
def test_cmd_merge_success(mock_merge, capsys):
    cmd_merge(_ns())
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "merged" in out
    assert "2 keys" in out


@patch("stashrun.cli_merge.merge_snapshots", return_value=None)
def test_cmd_merge_missing_source(mock_merge, capsys):
    cmd_merge(_ns())
    out = capsys.readouterr().out
    assert "[error]" in out
    assert "not found" in out


@patch("stashrun.cli_merge.merge_snapshots", side_effect=ValueError("Conflict on key 'X'"))
def test_cmd_merge_strict_conflict(mock_merge, capsys):
    cmd_merge(_ns(strategy="strict"))
    out = capsys.readouterr().out
    assert "[error]" in out
    assert "strict" in out


# ---------------------------------------------------------------------------
# cmd_merge_conflicts
# ---------------------------------------------------------------------------

@patch("stashrun.cli_merge.merge_conflicts", return_value={})
def test_cmd_merge_conflicts_none(mock_mc, capsys):
    cmd_merge_conflicts(_ns())
    out = capsys.readouterr().out
    assert "No conflicts" in out


@patch("stashrun.cli_merge.merge_conflicts",
       return_value={"KEY": ["val1", "val2"]})
def test_cmd_merge_conflicts_shows_keys(mock_mc, capsys):
    cmd_merge_conflicts(_ns())
    out = capsys.readouterr().out
    assert "KEY" in out
    assert "val1" in out
    assert "val2" in out


# ---------------------------------------------------------------------------
# register_merge_commands
# ---------------------------------------------------------------------------

def test_register_merge_commands_adds_parsers():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_merge_commands(sub)
    args = parser.parse_args(["merge", "snap_a", "snap_b", "--into", "out"])
    assert args.sources == ["snap_a", "snap_b"]
    assert args.target == "out"
    assert args.strategy == "last_wins"


def test_register_merge_conflicts_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_merge_commands(sub)
    args = parser.parse_args(["merge-conflicts", "snap_a", "snap_b"])
    assert args.sources == ["snap_a", "snap_b"]
