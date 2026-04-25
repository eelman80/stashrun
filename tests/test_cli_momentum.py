"""Tests for cli_momentum.py"""

import argparse
import pytest
from unittest.mock import patch
from stashrun.cli_momentum import cmd_momentum_show, cmd_momentum_top, cmd_momentum_summary


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


_SAMPLE = {
    "name": "mysnap",
    "version_score": 16,
    "access_score": 9,
    "rating_score": 20,
    "recency_score": 10,
    "total": 55,
}


def test_cmd_momentum_show_success(capsys):
    with patch("stashrun.cli_momentum.compute_momentum", return_value=_SAMPLE):
        cmd_momentum_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "mysnap" in out
    assert "55" in out


def test_cmd_momentum_show_missing(capsys):
    with patch("stashrun.cli_momentum.compute_momentum", return_value=None):
        cmd_momentum_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_momentum_top_shows_ranked(capsys):
    ranked = [
        {"name": "snap_b", "total": 80},
        {"name": "snap_a", "total": 40},
    ]
    with patch("stashrun.cli_momentum.momentum_rank", return_value=ranked):
        cmd_momentum_top(_ns(limit=5))
    out = capsys.readouterr().out
    assert "snap_b" in out
    assert "snap_a" in out


def test_cmd_momentum_top_empty(capsys):
    with patch("stashrun.cli_momentum.momentum_rank", return_value=[]):
        cmd_momentum_top(_ns(limit=5))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_momentum_top_respects_limit(capsys):
    ranked = [{"name": f"s{i}", "total": 100 - i} for i in range(20)]
    with patch("stashrun.cli_momentum.momentum_rank", return_value=ranked):
        cmd_momentum_top(_ns(limit=3))
    out = capsys.readouterr().out
    assert "s0" in out
    assert "s3" not in out


def test_cmd_momentum_summary(capsys):
    summary = {"count": 7, "average": 42.5, "top": "best_snap"}
    with patch("stashrun.cli_momentum.momentum_summary", return_value=summary):
        cmd_momentum_summary(_ns())
    out = capsys.readouterr().out
    assert "7" in out
    assert "42.5" in out
    assert "best_snap" in out


def test_cmd_momentum_summary_no_top(capsys):
    summary = {"count": 0, "average": 0.0, "top": None}
    with patch("stashrun.cli_momentum.momentum_summary", return_value=summary):
        cmd_momentum_summary(_ns())
    out = capsys.readouterr().out
    assert "N/A" in out
