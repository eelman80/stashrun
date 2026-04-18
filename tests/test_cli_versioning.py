"""Tests for cli_versioning commands."""

import argparse
import pytest
from unittest.mock import patch

from stashrun import cli_versioning as cv


def _ns(**kwargs):
    base = {"name": "snap", "index": 1}
    base.update(kwargs)
    return argparse.Namespace(**base)


def test_cmd_version_push_success(capsys):
    with patch("stashrun.cli_versioning.push_version", return_value=1):
        cv.cmd_version_push(_ns())
    assert "version 1" in capsys.readouterr().out


def test_cmd_version_push_missing(capsys):
    with patch("stashrun.cli_versioning.push_version", return_value=None):
        cv.cmd_version_push(_ns())
    assert "not found" in capsys.readouterr().out


def test_cmd_version_list_empty(capsys):
    with patch("stashrun.cli_versioning.list_versions", return_value=[]):
        cv.cmd_version_list(_ns())
    assert "No versions" in capsys.readouterr().out


def test_cmd_version_list_shows_entries(capsys):
    envs = [{"A": "1", "B": "2"}, {"A": "9"}]
    with patch("stashrun.cli_versioning.list_versions", return_value=envs):
        cv.cmd_version_list(_ns())
    out = capsys.readouterr().out
    assert "v1" in out
    assert "v2" in out


def test_cmd_version_show_found(capsys):
    env = {"X": "hello"}
    with patch("stashrun.cli_versioning.get_version", return_value=env):
        cv.cmd_version_show(_ns(index=1))
    assert "X=hello" in capsys.readouterr().out


def test_cmd_version_show_missing(capsys):
    with patch("stashrun.cli_versioning.get_version", return_value=None):
        cv.cmd_version_show(_ns(index=99))
    assert "not found" in capsys.readouterr().out


def test_cmd_version_restore_success(capsys):
    with patch("stashrun.cli_versioning.restore_version", return_value=True):
        cv.cmd_version_restore(_ns(index=1))
    assert "Restored" in capsys.readouterr().out


def test_cmd_version_restore_failure(capsys):
    with patch("stashrun.cli_versioning.restore_version", return_value=False):
        cv.cmd_version_restore(_ns(index=5))
    assert "not found" in capsys.readouterr().out


def test_cmd_version_drop_success(capsys):
    with patch("stashrun.cli_versioning.drop_versions", return_value=True):
        cv.cmd_version_drop(_ns())
    assert "Dropped" in capsys.readouterr().out


def test_cmd_version_drop_missing(capsys):
    with patch("stashrun.cli_versioning.drop_versions", return_value=False):
        cv.cmd_version_drop(_ns())
    assert "No versions" in capsys.readouterr().out
