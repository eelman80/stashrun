"""Tests for stashrun/cli_hooks.py"""

import argparse
import pytest

from stashrun import hooks as H
from stashrun.cli_hooks import (
    cmd_hook_list,
    cmd_hook_remove,
    cmd_hook_set,
    cmd_hook_show,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_cmd_hook_set_valid(capsys):
    cmd_hook_set(_ns(event="pre_save", command="echo hello"))
    assert H.get_hook("pre_save") == "echo hello"
    out = capsys.readouterr().out
    assert "pre_save" in out


def test_cmd_hook_set_invalid_event(capsys):
    cmd_hook_set(_ns(event="bad_event", command="echo x"))
    out = capsys.readouterr().out
    assert "Unknown event" in out


def test_cmd_hook_remove_existing(capsys):
    H.set_hook("post_save", "echo bye")
    cmd_hook_remove(_ns(event="post_save"))
    assert H.get_hook("post_save") is None
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_hook_remove_missing(capsys):
    cmd_hook_remove(_ns(event="pre_restore"))
    out = capsys.readouterr().out
    assert "No hook" in out


def test_cmd_hook_show_existing(capsys):
    H.set_hook("post_restore", "make deploy")
    cmd_hook_show(_ns(event="post_restore"))
    out = capsys.readouterr().out
    assert "make deploy" in out


def test_cmd_hook_show_missing(capsys):
    cmd_hook_show(_ns(event="post_restore"))
    out = capsys.readouterr().out
    assert "No hook" in out


def test_cmd_hook_list_empty(capsys):
    cmd_hook_list(_ns())
    out = capsys.readouterr().out
    assert "No hooks" in out


def test_cmd_hook_list_shows_all(capsys):
    H.set_hook("pre_save", "echo a")
    H.set_hook("post_save", "echo b")
    cmd_hook_list(_ns())
    out = capsys.readouterr().out
    assert "pre_save" in out
    assert "post_save" in out
