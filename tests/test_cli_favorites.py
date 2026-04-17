import pytest
import types
from unittest.mock import patch
from stashrun import cli_favorites as cli_mod
from stashrun import snapshots_favorites as fav_mod


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(fav_mod, "get_stash_dir", lambda: tmp_path)
    yield tmp_path


def _ns(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_cmd_favorite_add_success(capsys):
    cli_mod.cmd_favorite_add(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "Added" in out


def test_cmd_favorite_add_duplicate(capsys):
    fav_mod.add_favorite("snap1")
    cli_mod.cmd_favorite_add(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_favorite_remove_success(capsys):
    fav_mod.add_favorite("snap1")
    cli_mod.cmd_favorite_remove(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_favorite_remove_missing(capsys):
    cli_mod.cmd_favorite_remove(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not in favorites" in out


def test_cmd_favorite_list_empty(capsys):
    cli_mod.cmd_favorite_list(_ns())
    out = capsys.readouterr().out
    assert "No favorites" in out


def test_cmd_favorite_list_with_entries(capsys):
    fav_mod.add_favorite("a")
    fav_mod.add_favorite("b")
    cli_mod.cmd_favorite_list(_ns())
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_cmd_favorite_check_true(capsys):
    fav_mod.add_favorite("snap1")
    cli_mod.cmd_favorite_check(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "is a favorite" in out


def test_cmd_favorite_check_false(capsys):
    cli_mod.cmd_favorite_check(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "not a favorite" in out


def test_cmd_favorite_clear(capsys):
    fav_mod.add_favorite("a")
    fav_mod.add_favorite("b")
    cli_mod.cmd_favorite_clear(_ns())
    out = capsys.readouterr().out
    assert "2" in out
