"""Tests for cli_popularity commands."""

import pytest
from unittest.mock import patch
from argparse import Namespace


def _ns(**kwargs):
    return Namespace(**kwargs)


def test_cmd_popularity_show_success(capsys):
    result = {
        "name": "mysnap",
        "access_score": 10,
        "favorite_score": 20,
        "reaction_score": 6,
        "rating_score": 16.0,
        "total": 52.0,
    }
    with patch("stashrun.cli_popularity.compute_popularity", return_value=result):
        from stashrun.cli_popularity import cmd_popularity_show
        cmd_popularity_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "mysnap" in out
    assert "52.0" in out


def test_cmd_popularity_show_missing(capsys):
    with patch("stashrun.cli_popularity.compute_popularity", return_value=None):
        from stashrun.cli_popularity import cmd_popularity_show
        cmd_popularity_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_popularity_top_shows_ranked(capsys):
    ranked = [
        {"name": "a", "total": 80.0},
        {"name": "b", "total": 50.0},
    ]
    with patch("stashrun.cli_popularity.popularity_rank", return_value=ranked):
        from stashrun.cli_popularity import cmd_popularity_top
        cmd_popularity_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "a" in out
    assert "80.0" in out


def test_cmd_popularity_top_empty(capsys):
    with patch("stashrun.cli_popularity.popularity_rank", return_value=[]):
        from stashrun.cli_popularity import cmd_popularity_top
        cmd_popularity_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_popularity_summary(capsys):
    summary = {"count": 5, "average": 34.5, "top": "best_snap"}
    with patch("stashrun.cli_popularity.popularity_summary", return_value=summary):
        from stashrun.cli_popularity import cmd_popularity_summary
        cmd_popularity_summary(_ns())
    out = capsys.readouterr().out
    assert "5" in out
    assert "34.5" in out
    assert "best_snap" in out
