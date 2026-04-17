import pytest
import types
from stashrun import cli_groups as cg
from stashrun import snapshots_groups as sg


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def _ns(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_cmd_group_create_success(capsys):
    cg.cmd_group_create(_ns(name="g1"))
    assert "created" in capsys.readouterr().out


def test_cmd_group_create_duplicate(capsys):
    sg.create_group("g1")
    cg.cmd_group_create(_ns(name="g1"))
    assert "already exists" in capsys.readouterr().out


def test_cmd_group_delete_success(capsys):
    sg.create_group("g1")
    cg.cmd_group_delete(_ns(name="g1"))
    assert "deleted" in capsys.readouterr().out


def test_cmd_group_delete_missing(capsys):
    cg.cmd_group_delete(_ns(name="ghost"))
    assert "not found" in capsys.readouterr().out


def test_cmd_group_add_success(capsys):
    sg.create_group("g1")
    cg.cmd_group_add(_ns(group="g1", snapshot="snap_a"))
    assert "Added" in capsys.readouterr().out


def test_cmd_group_add_missing_group(capsys):
    cg.cmd_group_add(_ns(group="nope", snapshot="snap_a"))
    assert "not found" in capsys.readouterr().out


def test_cmd_group_show_members(capsys):
    sg.create_group("g1")
    sg.add_to_group("g1", "snap_a")
    cg.cmd_group_show(_ns(name="g1"))
    assert "snap_a" in capsys.readouterr().out


def test_cmd_group_show_empty(capsys):
    sg.create_group("g1")
    cg.cmd_group_show(_ns(name="g1"))
    assert "empty" in capsys.readouterr().out


def test_cmd_group_list_output(capsys):
    sg.create_group("alpha")
    cg.cmd_group_list(_ns())
    assert "alpha" in capsys.readouterr().out


def test_cmd_group_find_output(capsys):
    sg.create_group("g1")
    sg.add_to_group("g1", "snap1")
    cg.cmd_group_find(_ns(snapshot="snap1"))
    assert "g1" in capsys.readouterr().out
