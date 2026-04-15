"""Tests for stashrun/cli_templates.py"""

import argparse
import pytest

from stashrun import templates as T
from stashrun.cli_templates import (
    cmd_template_apply,
    cmd_template_delete,
    cmd_template_list,
    cmd_template_save,
    cmd_template_show,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def _ns(**kwargs):
    return argparse.Namespace(**kwargs)


def test_cmd_template_save_no_defaults(capsys):
    cmd_template_save(_ns(name="simple", vars=["FOO", "BAR"]))
    out = capsys.readouterr().out
    assert "simple" in out
    assert "2 variable" in out
    assert T.get_template("simple") == {"FOO": None, "BAR": None}


def test_cmd_template_save_with_defaults(capsys):
    cmd_template_save(_ns(name="withdef", vars=["KEY=myval", "OTHER"]))
    assert T.get_template("withdef") == {"KEY": "myval", "OTHER": None}


def test_cmd_template_delete_existing(capsys):
    T.save_template("bye", {"X": None})
    cmd_template_delete(_ns(name="bye"))
    out = capsys.readouterr().out
    assert "deleted" in out
    assert T.get_template("bye") is None


def test_cmd_template_delete_missing(capsys):
    cmd_template_delete(_ns(name="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_template_show_existing(capsys):
    T.save_template("show_me", {"A": None, "B": "default_b"})
    cmd_template_show(_ns(name="show_me"))
    out = capsys.readouterr().out
    assert "show_me" in out
    assert "A" in out
    assert "B" in out
    assert "default_b" in out


def test_cmd_template_show_missing(capsys):
    cmd_template_show(_ns(name="nope"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_template_list_empty(capsys):
    cmd_template_list(_ns())
    out = capsys.readouterr().out
    assert "No templates" in out


def test_cmd_template_list_shows_names(capsys):
    T.save_template("alpha", {})
    T.save_template("beta", {})
    cmd_template_list(_ns())
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_template_apply_filters_env(capsys, monkeypatch):
    monkeypatch.setenv("MY_VAR", "hello")
    monkeypatch.setenv("UNRELATED", "ignored")
    T.save_template("filtered", {"MY_VAR": None})
    cmd_template_apply(_ns(name="filtered"))
    out = capsys.readouterr().out
    assert "MY_VAR" in out
    assert "hello" in out
    assert "UNRELATED" not in out


def test_cmd_template_apply_missing_template(capsys):
    cmd_template_apply(_ns(name="no_template"))
    out = capsys.readouterr().out
    assert "not found" in out
