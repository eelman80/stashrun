"""Tests for cli_trust commands."""

import pytest
from unittest.mock import patch
from types import SimpleNamespace


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_trust_show_success(capsys):
    from stashrun.cli_trust import cmd_trust_show
    result = {"score": 85, "level": "high", "breakdown": {"owner": 20, "checksum": 30}}
    with patch("stashrun.cli_trust.compute_trust", return_value=result):
        cmd_trust_show(_ns(name="mysnap"))
    out = capsys.readouterr().out
    assert "85/100" in out
    assert "high" in out
    assert "owner: +20" in out


def test_cmd_trust_show_missing(capsys):
    from stashrun.cli_trust import cmd_trust_show
    with patch("stashrun.cli_trust.compute_trust", return_value=None):
        cmd_trust_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_trust_top_shows_ranked(capsys):
    from stashrun.cli_trust import cmd_trust_top
    ranked = [("a", 90), ("b", 60)]
    with patch("stashrun.cli_trust.list_all_snapshots", return_value=["a", "b"]), \
         patch("stashrun.cli_trust.trust_rank", return_value=ranked):
        cmd_trust_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "a: 90" in out
    assert "b: 60" in out


def test_cmd_trust_top_empty(capsys):
    from stashrun.cli_trust import cmd_trust_top
    with patch("stashrun.cli_trust.list_all_snapshots", return_value=[]), \
         patch("stashrun.cli_trust.trust_rank", return_value=[]):
        cmd_trust_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_trust_summary(capsys):
    from stashrun.cli_trust import cmd_trust_summary
    summary = {"verified": 2, "high": 1, "medium": 0, "low": 0, "untrusted": 1}
    with patch("stashrun.cli_trust.list_all_snapshots", return_value=[]), \
         patch("stashrun.cli_trust.trust_summary", return_value=summary):
        cmd_trust_summary(_ns())
    out = capsys.readouterr().out
    assert "verified: 2" in out
    assert "untrusted: 1" in out
