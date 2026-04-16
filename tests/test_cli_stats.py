"""Tests for cli_stats commands."""
import argparse
from unittest.mock import patch
from stashrun import cli_stats, snapshots_stats


def _ns(**kwargs):
    defaults = {"top": 5}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


FAKE_SUMMARY = {
    "total_snapshots": 4,
    "total_keys": 20,
    "average_keys": 5.0,
    "tagged": 2,
    "pinned": 1,
    "most_common_keys": [("PATH", 4), ("HOME", 3)],
}


def test_cmd_stats_output(capsys):
    with patch.object(snapshots_stats, "summary", return_value=FAKE_SUMMARY):
        cli_stats.cmd_stats(_ns())
    out = capsys.readouterr().out
    assert "4" in out
    assert "20" in out
    assert "5.0" in out
    assert "PATH" in out
    assert "HOME" in out


def test_cmd_stats_no_keys(capsys):
    empty = dict(FAKE_SUMMARY, most_common_keys=[])
    with patch.object(snapshots_stats, "summary", return_value=empty):
        cli_stats.cmd_stats(_ns())
    out = capsys.readouterr().out
    assert "(none)" in out


def test_cmd_stats_keys_output(capsys):
    with patch.object(snapshots_stats, "most_common_keys", return_value=[("A", 3), ("B", 1)]):
        cli_stats.cmd_stats_keys(_ns(top=2))
    out = capsys.readouterr().out
    assert "A: 3" in out
    assert "B: 1" in out


def test_cmd_stats_keys_empty(capsys):
    with patch.object(snapshots_stats, "most_common_keys", return_value=[]):
        cli_stats.cmd_stats_keys(_ns(top=5))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_register_stats_commands():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    cli_stats.register_stats_commands(sub)
    args = parser.parse_args(["stats"])
    assert hasattr(args, "func")
