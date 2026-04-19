import argparse
import pytest
from unittest.mock import patch
from stashrun.cli_impact import cmd_impact_show, cmd_impact_top, cmd_impact_summary


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


FULL_RESULT = {
    "name": "mysnap",
    "dependents": 2,
    "subscribers": 3,
    "groups": 1,
    "dependent_score": 20,
    "subscriber_score": 15,
    "group_score": 10,
    "total": 45,
}


def test_cmd_impact_show_success(capsys):
    with patch("stashrun.cli_impact.compute_impact", return_value=FULL_RESULT):
        cmd_impact_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "mysnap" in out
    assert "45" in out


def test_cmd_impact_show_missing(capsys):
    with patch("stashrun.cli_impact.compute_impact", return_value=None):
        cmd_impact_show(_ns(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_impact_top_shows_ranked(capsys):
    ranked = [{"name": "a", "total": 80}, {"name": "b", "total": 40}]
    with patch("stashrun.cli_impact.list_all_snapshots", return_value=["a", "b"]), \
         patch("stashrun.cli_impact.impact_rank", return_value=ranked):
        cmd_impact_top(_ns(limit=5))
    out = capsys.readouterr().out
    assert "a: 80" in out
    assert "b: 40" in out


def test_cmd_impact_top_empty(capsys):
    with patch("stashrun.cli_impact.list_all_snapshots", return_value=[]), \
         patch("stashrun.cli_impact.impact_rank", return_value=[]):
        cmd_impact_top(_ns(limit=5))
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_impact_summary_output(capsys):
    summary = {"count": 3, "avg_total": 25.5, "max_total": 60}
    with patch("stashrun.cli_impact.list_all_snapshots", return_value=["a", "b", "c"]), \
         patch("stashrun.cli_impact.impact_summary", return_value=summary):
        cmd_impact_summary(_ns())
    out = capsys.readouterr().out
    assert "25.5" in out
    assert "60" in out
