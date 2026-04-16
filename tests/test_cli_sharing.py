import pytest
from unittest.mock import patch
from types import SimpleNamespace

from stashrun.cli_sharing import cmd_share_encode, cmd_share_import, cmd_share_inspect


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


def test_cmd_share_encode_success(capsys):
    with patch("stashrun.cli_sharing.encode_snapshot", return_value="ABC123"):
        cmd_share_encode(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "ABC123" in out


def test_cmd_share_encode_missing(capsys):
    with patch("stashrun.cli_sharing.encode_snapshot", return_value=None):
        cmd_share_encode(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_share_import_success(capsys):
    with patch("stashrun.cli_sharing.import_share_string", return_value="mysnap"):
        cmd_share_import(_ns(share_str="XYZ", name=None))
    out = capsys.readouterr().out
    assert "mysnap" in out
    assert "Imported" in out


def test_cmd_share_import_invalid(capsys):
    with patch("stashrun.cli_sharing.import_share_string", return_value=None):
        cmd_share_import(_ns(share_str="bad", name=None))
    out = capsys.readouterr().out
    assert "Invalid" in out


def test_cmd_share_inspect_success(capsys):
    with patch("stashrun.cli_sharing.share_summary", return_value={"name": "s", "key_count": 3}):
        cmd_share_inspect(_ns(share_str="XYZ"))
    out = capsys.readouterr().out
    assert "Name: s" in out
    assert "Keys: 3" in out


def test_cmd_share_inspect_invalid(capsys):
    with patch("stashrun.cli_sharing.share_summary", return_value=None):
        cmd_share_inspect(_ns(share_str="bad"))
    out = capsys.readouterr().out
    assert "Invalid" in out
