"""Tests for stashrun.cli_coherence."""

from __future__ import annotations

import argparse
from unittest.mock import patch

from stashrun.cli_coherence import cmd_coherence_show, cmd_coherence_summary, cmd_coherence_top


def _ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_coherence_show_success(capsys):
    report = {"name": "mysnap", "score": 80, "issues": ["checksum mismatch"]}
    with patch("stashrun.cli_coherence.compute_coherence", return_value=report):
        cmd_coherence_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "80" in out
    assert "checksum mismatch" in out


def test_cmd_coherence_show_perfect(capsys):
    report = {"name": "mysnap", "score": 100, "issues": []}
    with patch("stashrun.cli_coherence.compute_coherence", return_value=report):
        cmd_coherence_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "100" in out
    assert "No issues" in out


def test_cmd_coherence_show_missing(capsys):
    with patch("stashrun.cli_coherence.compute_coherence", return_value=None):
        cmd_coherence_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_coherence_top_shows_ranked(capsys):
    ranked = [
        {"name": "alpha", "score": 100, "issues": []},
        {"name": "beta", "score": 60, "issues": ["bad key"]},
    ]
    with patch("stashrun.cli_coherence.coherence_rank", return_value=ranked):
        cmd_coherence_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_coherence_top_empty(capsys):
    with patch("stashrun.cli_coherence.coherence_rank", return_value=[]):
        cmd_coherence_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_coherence_summary_output(capsys):
    summary = {"count": 5, "average": 88.0, "perfect": 3, "degraded": 1}
    with patch("stashrun.cli_coherence.coherence_summary", return_value=summary):
        cmd_coherence_summary(_ns())
    out = capsys.readouterr().out
    assert "5" in out
    assert "88.0" in out
    assert "3" in out


def test_cmd_coherence_summary_empty(capsys):
    summary = {"count": 0, "average": 0.0, "perfect": 0, "degraded": 0}
    with patch("stashrun.cli_coherence.coherence_summary", return_value=summary):
        cmd_coherence_summary(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out
