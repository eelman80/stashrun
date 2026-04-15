"""Tests for stashrun/templates.py"""

import pytest
from pathlib import Path

from stashrun import templates as T


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def test_save_template_creates_entry():
    assert T.save_template("mytemplate", {"FOO": None, "BAR": "default"}) is True
    assert T.get_template("mytemplate") == {"FOO": None, "BAR": "default"}


def test_save_template_overwrites():
    T.save_template("t", {"A": None})
    T.save_template("t", {"B": "val"})
    assert T.get_template("t") == {"B": "val"}


def test_get_template_missing_returns_none():
    assert T.get_template("nonexistent") is None


def test_delete_template_existing():
    T.save_template("del_me", {"X": None})
    assert T.delete_template("del_me") is True
    assert T.get_template("del_me") is None


def test_delete_template_missing_returns_false():
    assert T.delete_template("ghost") is False


def test_list_templates_empty():
    assert T.list_templates() == []


def test_list_templates_sorted():
    T.save_template("zebra", {})
    T.save_template("alpha", {})
    T.save_template("middle", {})
    assert T.list_templates() == ["alpha", "middle", "zebra"]


def test_apply_template_uses_env_values():
    T.save_template("app", {"HOME": None, "PATH": None})
    env = {"HOME": "/home/user", "PATH": "/usr/bin", "EXTRA": "ignored"}
    result = T.apply_template("app", env)
    assert result == {"HOME": "/home/user", "PATH": "/usr/bin"}


def test_apply_template_uses_default_for_missing_key():
    T.save_template("defaults", {"MISSING": "fallback", "PRESENT": None})
    env = {"PRESENT": "yes"}
    result = T.apply_template("defaults", env)
    assert result == {"MISSING": "fallback", "PRESENT": "yes"}


def test_apply_template_skips_none_default_if_missing():
    T.save_template("strict", {"REQUIRED": None})
    result = T.apply_template("strict", {})
    assert "REQUIRED" not in result


def test_apply_template_missing_template_returns_none():
    result = T.apply_template("no_such", {"A": "1"})
    assert result is None
