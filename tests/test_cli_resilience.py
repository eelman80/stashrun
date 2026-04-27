"""Tests for stashrun.cli_resilience."""

import argparse
import pytest
from unittest.mock import patch

from stashrun.cli_resilience import (
    cmd_resilience_show,
    cmd_resilience_top,
    cmd_resilience_summary,
)

MOD = "stashrun.cli_resilience"


def _ns(**kwargs):
    defaults = {"name": "snap1", "limit": 10}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_resilience_show_success(capsys):
    result = {"score": 60, "details": {"encrypted": True, "pinned": False}}
    with patch(f"{MOD}.compute_resilience", return_value=result):
        cmd_resilience_show(_ns())
    out = capsys.readouterr().out
    assert "60" in out
    assert "encrypted" in out


def test_cmd_resilience_show_missing(capsys):
    with patch(f"{MOD}.compute_resilience", return_value=None):
        cmd_resilience_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_resilience_top_shows_ranked(capsys):
    ranked = [("snap1", 80), ("snap2", 55)]
    with patch(f"{MOD}.resilience_rank", return_value=ranked):
        cmd_resilience_top(_ns())
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" in out


def test_cmd_resilience_top_empty(capsys):
    with patch(f"{MOD}.resilience_rank", return_value=[]):
        cmd_resilience_top(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_resilience_top_respects_limit(capsys):
    ranked = [(f"snap{i}", 100 - i) for i in range(20)]
    with patch(f"{MOD}.resilience_rank", return_value=ranked):
        cmd_resilience_top(_ns(limit=3))
    out = capsys.readouterr().out
    assert "snap0" in out
    assert "snap3" not in out


def test_cmd_resilience_summary_output(capsys):
    summary = {"count": 5, "average": 62.4, "min": 20, "max": 95}
    with patch(f"{MOD}.resilience_summary", return_value=summary):
        cmd_resilience_summary(_ns())
    out = capsys.readouterr().out
    assert "5" in out
    assert "62.4" in out


def test_cmd_resilience_summary_empty(capsys):
    summary = {"count": 0, "average": 0, "min": 0, "max": 0}
    with patch(f"{MOD}.resilience_summary", return_value=summary):
        cmd_resilience_summary(_ns())
    out = capsys.readouterr().out
    assert "No snapshots" in out
