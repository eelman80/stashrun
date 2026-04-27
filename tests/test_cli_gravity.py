"""Tests for stashrun.cli_gravity."""

from __future__ import annotations

import argparse
from unittest.mock import patch

from stashrun.cli_gravity import cmd_gravity_show, cmd_gravity_top, cmd_gravity_summary


def _ns(**kwargs):
    defaults = {"name": "mysnap", "limit": 10}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# cmd_gravity_show
# ---------------------------------------------------------------------------

def test_cmd_gravity_show_success(capsys):
    fake = {
        "name": "mysnap", "total": 42,
        "dependents": 2, "dep_score": 30,
        "mentions": 1, "mention_score": 5,
        "relations": 3, "relation_score": 12,
        "endorsements": 1, "endorse_score": 3,
    }
    with patch("stashrun.cli_gravity.compute_gravity", return_value=fake):
        cmd_gravity_show(_ns())
    out = capsys.readouterr().out
    assert "42" in out
    assert "mysnap" in out


def test_cmd_gravity_show_missing(capsys):
    with patch("stashrun.cli_gravity.compute_gravity", return_value=None):
        cmd_gravity_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


# ---------------------------------------------------------------------------
# cmd_gravity_top
# ---------------------------------------------------------------------------

def test_cmd_gravity_top_shows_ranked(capsys):
    ranked = [
        {"name": "alpha", "total": 80},
        {"name": "beta", "total": 40},
    ]
    with patch("stashrun.cli_gravity.gravity_rank", return_value=ranked):
        cmd_gravity_top(_ns())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_gravity_top_empty(capsys):
    with patch("stashrun.cli_gravity.gravity_rank", return_value=[]):
        cmd_gravity_top(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_gravity_top_respects_limit(capsys):
    ranked = [{"name": f"s{i}", "total": 100 - i} for i in range(20)]
    with patch("stashrun.cli_gravity.gravity_rank", return_value=ranked):
        cmd_gravity_top(_ns(limit=3))
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 3


# ---------------------------------------------------------------------------
# cmd_gravity_summary
# ---------------------------------------------------------------------------

def test_cmd_gravity_summary_output(capsys):
    summary = {"count": 5, "avg": 22.4, "max": 60, "top": "alpha"}
    with patch("stashrun.cli_gravity.gravity_summary", return_value=summary):
        cmd_gravity_summary(_ns())
    out = capsys.readouterr().out
    assert "5" in out
    assert "22.4" in out
    assert "alpha" in out


def test_cmd_gravity_summary_empty(capsys):
    summary = {"count": 0, "avg": 0.0, "max": 0, "top": None}
    with patch("stashrun.cli_gravity.gravity_summary", return_value=summary):
        cmd_gravity_summary(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out
