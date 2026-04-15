"""Tests for stashrun.cli_encryption commands."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from stashrun.cli_encryption import cmd_keygen, cmd_key_status, register_encryption_commands
from stashrun.encryption import KEY_ENV_VAR


def _ns(**kwargs):
    defaults = {"save": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_keygen_prints_key(capsys):
    with patch("stashrun.cli_encryption.generate_key", return_value="FAKEKEY123"):
        cmd_keygen(_ns(save=False))
    out = capsys.readouterr().out
    assert "FAKEKEY123" in out


def test_cmd_keygen_save(capsys, tmp_path):
    fake_key = "SAVEDKEY456"
    fake_path = tmp_path / ".stashrun_key"
    with patch("stashrun.cli_encryption.generate_key", return_value=fake_key), \
         patch("stashrun.cli_encryption.save_key_to_file", return_value=fake_path) as mock_save:
        cmd_keygen(_ns(save=True))
    mock_save.assert_called_once_with(fake_key)
    out = capsys.readouterr().out
    assert str(fake_path) in out


def test_cmd_key_status_from_env(capsys, monkeypatch):
    monkeypatch.setenv(KEY_ENV_VAR, "somekey")
    cmd_key_status(_ns())
    out = capsys.readouterr().out
    assert KEY_ENV_VAR in out


def test_cmd_key_status_from_file(capsys, monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)
    with patch("stashrun.cli_encryption.get_key", return_value="filekey"):
        cmd_key_status(_ns())
    out = capsys.readouterr().out
    assert "key file" in out


def test_cmd_key_status_no_key(capsys, monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)
    with patch("stashrun.cli_encryption.get_key", return_value=None):
        cmd_key_status(_ns())
    out = capsys.readouterr().out
    assert "No encryption key" in out


def test_register_encryption_commands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register_encryption_commands(subparsers)
    args = parser.parse_args(["keygen"])
    assert args.func == cmd_keygen
    args2 = parser.parse_args(["key-status"])
    assert args2.func == cmd_key_status
