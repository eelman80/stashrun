"""Tests for stashrun.cli_watchlist."""

import argparse
import pytest
from stashrun import watchlist
from stashrun.cli_watchlist import (
    cmd_watch_add,
    cmd_watch_remove,
    cmd_watch_list,
    cmd_watch_check,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.storage._stash_dir", None)
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stashrun"))
    yield tmp_path / ".stashrun"


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_cmd_watch_add_new(capsys):
    cmd_watch_add(_ns(key="API_KEY", label=None))
    out = capsys.readouterr().out
    assert "Watching" in out
    assert "API_KEY" in out


def test_cmd_watch_add_duplicate(capsys):
    watchlist.watch_key("API_KEY")
    cmd_watch_add(_ns(key="API_KEY", label=None))
    out = capsys.readouterr().out
    assert "Already watched" in out


def test_cmd_watch_remove_existing(capsys):
    watchlist.watch_key("MY_VAR")
    cmd_watch_remove(_ns(key="MY_VAR"))
    out = capsys.readouterr().out
    assert "Removed" in out
    assert "MY_VAR" in out


def test_cmd_watch_remove_missing(capsys):
    cmd_watch_remove(_ns(key="GHOST"))
    out = capsys.readouterr().out
    assert "not in watchlist" in out


def test_cmd_watch_list_empty(capsys):
    cmd_watch_list(_ns())
    out = capsys.readouterr().out
    assert "empty" in out.lower()


def test_cmd_watch_list_with_keys(capsys):
    watchlist.watch_key("ALPHA")
    watchlist.watch_key("BETA")
    cmd_watch_list(_ns())
    out = capsys.readouterr().out
    assert "ALPHA" in out
    assert "BETA" in out


def test_cmd_watch_check_watched(capsys):
    watchlist.watch_key("DB_PASS")
    cmd_watch_check(_ns(key="DB_PASS"))
    out = capsys.readouterr().out
    assert "is watched" in out


def test_cmd_watch_check_not_watched(capsys):
    cmd_watch_check(_ns(key="UNKNOWN"))
    out = capsys.readouterr().out
    assert "NOT watched" in out
