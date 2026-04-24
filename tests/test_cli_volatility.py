"""Tests for stashrun.cli_volatility."""

from __future__ import annotations

import argparse
from unittest.mock import patch

from stashrun.cli_volatility import (
    cmd_volatility_show,
    cmd_volatility_top,
    cmd_volatility_summary,
)


def _ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


_PROFILE = {
    "name": "mysnap",
    "version_count": 3,
    "key_churn": 0.25,
    "access_count": 5,
    "volatility_score": 42,
}


def test_cmd_volatility_show_success(capsys):
    with patch("stashrun.cli_volatility.compute_volatility", return_value=_PROFILE):
        cmd_volatility_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "mysnap" in out
    assert "42" in out
    assert "0.25" in out


def test_cmd_volatility_show_missing(capsys):
    with patch("stashrun.cli_volatility.compute_volatility", return_value=None):
        cmd_volatility_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_volatility_top_shows_ranked(capsys):
    ranked = [
        {"name": "b", "volatility_score": 80},
        {"name": "a", "volatility_score": 20},
    ]
    with patch("stashrun.cli_volatility.list_snapshots", return_value=["a", "b"]), \
         patch("stashrun.cli_volatility.volatility_rank", return_value=ranked):
        cmd_volatility_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "80" in out
    assert "b" in out


def test_cmd_volatility_top_empty(capsys):
    with patch("stashrun.cli_volatility.list_snapshots", return_value=[]), \
         patch("stashrun.cli_volatility.volatility_rank", return_value=[]):
        cmd_volatility_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_volatility_summary_success(capsys):
    summary = {"count": 5, "avg_score": 37.4, "max_score": 90, "min_score": 5}
    with patch("stashrun.cli_volatility.list_snapshots", return_value=["a"]), \
         patch("stashrun.cli_volatility.volatility_summary", return_value=summary):
        cmd_volatility_summary(_ns())
    out = capsys.readouterr().out
    assert "37.4" in out
    assert "90" in out


def test_cmd_volatility_summary_empty(capsys):
    summary = {"count": 0, "avg_score": 0.0, "max_score": 0, "min_score": 0}
    with patch("stashrun.cli_volatility.list_snapshots", return_value=[]), \
         patch("stashrun.cli_volatility.volatility_summary", return_value=summary):
        cmd_volatility_summary(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out
