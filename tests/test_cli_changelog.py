import pytest
from unittest.mock import patch
from stashrun.cli_changelog import (
    cmd_changelog_set,
    cmd_changelog_get,
    cmd_changelog_remove,
    cmd_changelog_list,
    cmd_changelog_clear,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def _ns(**kwargs):
    import types
    return types.SimpleNamespace(**kwargs)


def test_cmd_changelog_set_success(capsys):
    cmd_changelog_set(_ns(name="snap1", message="hello"))
    out = capsys.readouterr().out
    assert "snap1" in out


def test_cmd_changelog_get_existing(capsys):
    cmd_changelog_set(_ns(name="snap1", message="hello"))
    cmd_changelog_get(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "hello" in out


def test_cmd_changelog_get_missing(capsys):
    cmd_changelog_get(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No changelog" in out


def test_cmd_changelog_remove_existing(capsys):
    cmd_changelog_set(_ns(name="snap1", message="bye"))
    capsys.readouterr()
    cmd_changelog_remove(_ns(name="snap1"))
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_changelog_remove_missing(capsys):
    cmd_changelog_remove(_ns(name="nope"))
    out = capsys.readouterr().out
    assert "No changelog found" in out


def test_cmd_changelog_list_empty(capsys):
    cmd_changelog_list(_ns())
    out = capsys.readouterr().out
    assert "No changelog" in out


def test_cmd_changelog_clear(capsys):
    cmd_changelog_set(_ns(name="a", message="m"))
    capsys.readouterr()
    cmd_changelog_clear(_ns())
    out = capsys.readouterr().out
    assert "1" in out
