import pytest
from unittest.mock import patch
from types import SimpleNamespace as NS

from stashrun.cli_confidence import cmd_confidence_show, cmd_confidence_top


def _ns(**kwargs):
    return NS(**kwargs)


FULL_INFO = {
    "score": 85,
    "max_score": 100,
    "percent": 85.0,
    "checksum_exists": True,
    "checksum_valid": True,
    "rating": 4,
    "no_empty_values": True,
    "has_keys": True,
}


def test_cmd_confidence_show_success(capsys):
    with patch("stashrun.cli_confidence.compute_confidence", return_value=FULL_INFO):
        cmd_confidence_show(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "85.0%" in out
    assert "snap1" in out


def test_cmd_confidence_show_missing(capsys):
    with patch("stashrun.cli_confidence.compute_confidence", return_value=None):
        cmd_confidence_show(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_confidence_top_shows_ranked(capsys):
    ranked = [("snap_a", 90.0), ("snap_b", 70.0)]
    with patch("stashrun.cli_confidence.list_all_snapshots", return_value=["snap_a", "snap_b"]), \
         patch("stashrun.cli_confidence.confidence_rank", return_value=ranked):
        cmd_confidence_top(_ns(limit=10))
    out = capsys.readouterr().out
    assert "snap_a" in out
    assert "90.0" in out


def test_cmd_confidence_top_empty(capsys):
    with patch("stashrun.cli_confidence.list_all_snapshots", return_value=[]), \
         patch("stashrun.cli_confidence.confidence_rank", return_value=[]):
        cmd_confidence_top(_ns(limit=5))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_confidence_top_respects_limit(capsys):
    ranked = [(f"snap_{i}", float(100 - i)) for i in range(20)]
    with patch("stashrun.cli_confidence.list_all_snapshots", return_value=[]), \
         patch("stashrun.cli_confidence.confidence_rank", return_value=ranked):
        cmd_confidence_top(_ns(limit=3))
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 3
