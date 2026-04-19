import pytest
import argparse
from unittest.mock import patch
from stashrun.cli_relations import (
    cmd_relation_add, cmd_relation_remove, cmd_relation_show,
    cmd_relation_find, cmd_relation_clear
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_cmd_relation_add_success(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="related"))
    out = capsys.readouterr().out
    assert "Linked" in out


def test_cmd_relation_add_invalid(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="unknown_type"))
    out = capsys.readouterr().out
    assert "Failed" in out


def test_cmd_relation_add_self(capsys):
    cmd_relation_add(_ns(source="a", target="a", relation="related"))
    out = capsys.readouterr().out
    assert "Failed" in out


def test_cmd_relation_remove_existing(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="derived"))
    cmd_relation_remove(_ns(source="a", target="b", relation="derived"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_relation_remove_missing(capsys):
    cmd_relation_remove(_ns(source="a", target="b", relation="derived"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_relation_show_with_data(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="supersedes"))
    capsys.readouterr()
    cmd_relation_show(_ns(name="a"))
    out = capsys.readouterr().out
    assert "supersedes" in out
    assert "b" in out


def test_cmd_relation_show_empty(capsys):
    cmd_relation_show(_ns(name="nope"))
    out = capsys.readouterr().out
    assert "No relations" in out


def test_cmd_relation_find_results(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="conflicting"))
    capsys.readouterr()
    cmd_relation_find(_ns(name="a", relation="conflicting"))
    out = capsys.readouterr().out
    assert "b" in out


def test_cmd_relation_clear_success(capsys):
    cmd_relation_add(_ns(source="a", target="b", relation="related"))
    capsys.readouterr()
    cmd_relation_clear(_ns(name="a"))
    out = capsys.readouterr().out
    assert "Cleared" in out


def test_cmd_relation_clear_missing(capsys):
    cmd_relation_clear(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "No relations" in out
