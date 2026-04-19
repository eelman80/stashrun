import pytest
import types
from stashrun import cli_categories as cc
from stashrun import snapshots_categories as sc


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_categories.get_stash_dir", lambda: tmp_path)


def _ns(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_cmd_category_set_success(capsys):
    cc.cmd_category_set(_ns(name="snap1", category="prod"))
    out = capsys.readouterr().out
    assert "prod" in out and "snap1" in out


def test_cmd_category_get_existing(capsys):
    sc.set_category("snap1", "staging")
    cc.cmd_category_get(_ns(name="snap1"))
    assert "staging" in capsys.readouterr().out


def test_cmd_category_get_missing(capsys):
    cc.cmd_category_get(_ns(name="ghost"))
    assert "uncategorized" in capsys.readouterr().out


def test_cmd_category_remove_existing(capsys):
    sc.set_category("snap1", "dev")
    cc.cmd_category_remove(_ns(name="snap1"))
    assert "removed" in capsys.readouterr().out


def test_cmd_category_remove_missing(capsys):
    cc.cmd_category_remove(_ns(name="ghost"))
    assert "No category" in capsys.readouterr().out


def test_cmd_category_list_empty(capsys):
    cc.cmd_category_list(_ns())
    assert "No categories" in capsys.readouterr().out


def test_cmd_category_list_shows_entries(capsys):
    sc.set_category("a", "prod")
    cc.cmd_category_list(_ns())
    assert "prod" in capsys.readouterr().out


def test_cmd_category_find_match(capsys):
    sc.set_category("a", "prod")
    cc.cmd_category_find(_ns(category="prod"))
    assert "a" in capsys.readouterr().out


def test_cmd_category_find_no_match(capsys):
    cc.cmd_category_find(_ns(category="missing"))
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_category_all(capsys):
    sc.set_category("a", "prod")
    sc.set_category("b", "dev")
    cc.cmd_category_all(_ns())
    out = capsys.readouterr().out
    assert "prod" in out and "dev" in out
