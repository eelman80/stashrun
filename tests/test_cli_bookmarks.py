import pytest
from types import SimpleNamespace
from stashrun.cli_bookmarks import (
    cmd_bookmark_set, cmd_bookmark_remove, cmd_bookmark_resolve,
    cmd_bookmark_list, cmd_bookmark_rename,
)


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_cmd_bookmark_set_success(capsys):
    cmd_bookmark_set(_ns(alias="prod", snapshot="production-snap"))
    out = capsys.readouterr().out
    assert "prod" in out
    assert "production-snap" in out


def test_cmd_bookmark_remove_existing(capsys):
    cmd_bookmark_set(_ns(alias="dev", snapshot="dev-snap"))
    cmd_bookmark_remove(_ns(alias="dev"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_bookmark_remove_missing(capsys):
    cmd_bookmark_remove(_ns(alias="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_bookmark_resolve_found(capsys):
    cmd_bookmark_set(_ns(alias="x", snapshot="snap-x"))
    capsys.readouterr()
    cmd_bookmark_resolve(_ns(alias="x"))
    out = capsys.readouterr().out
    assert "snap-x" in out


def test_cmd_bookmark_resolve_missing(capsys):
    cmd_bookmark_resolve(_ns(alias="missing"))
    out = capsys.readouterr().out
    assert "No bookmark" in out


def test_cmd_bookmark_list_empty(capsys):
    cmd_bookmark_list(_ns())
    out = capsys.readouterr().out
    assert "No bookmarks" in out


def test_cmd_bookmark_list_shows_entries(capsys):
    cmd_bookmark_set(_ns(alias="z", snapshot="snap-z"))
    capsys.readouterr()
    cmd_bookmark_list(_ns())
    out = capsys.readouterr().out
    assert "z -> snap-z" in out


def test_cmd_bookmark_rename_success(capsys):
    cmd_bookmark_set(_ns(alias="old", snapshot="snap-o"))
    capsys.readouterr()
    cmd_bookmark_rename(_ns(old="old", new="new"))
    out = capsys.readouterr().out
    assert "Renamed" in out
