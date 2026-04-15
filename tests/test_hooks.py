"""Tests for stashrun/hooks.py"""

import pytest
from unittest.mock import patch

from stashrun import hooks as H


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_hook_valid_event():
    assert H.set_hook("pre_save", "echo pre") is True
    assert H.get_hook("pre_save") == "echo pre"


def test_set_hook_invalid_event():
    assert H.set_hook("on_magic", "echo x") is False
    assert H.get_hook("on_magic") is None


def test_set_hook_overwrites():
    H.set_hook("post_save", "echo first")
    H.set_hook("post_save", "echo second")
    assert H.get_hook("post_save") == "echo second"


def test_remove_hook_existing():
    H.set_hook("pre_restore", "echo before")
    assert H.remove_hook("pre_restore") is True
    assert H.get_hook("pre_restore") is None


def test_remove_hook_missing():
    assert H.remove_hook("post_restore") is False


def test_list_hooks_empty():
    assert H.list_hooks() == {}


def test_list_hooks_multiple():
    H.set_hook("pre_save", "echo a")
    H.set_hook("post_restore", "echo b")
    result = H.list_hooks()
    assert result["pre_save"] == "echo a"
    assert result["post_restore"] == "echo b"


def test_run_hook_no_hook_registered():
    result = H.run_hook("pre_save", "mysnap")
    assert result is None


def test_run_hook_executes_command():
    H.set_hook("post_save", "exit 0")
    code = H.run_hook("post_save", "mysnap")
    assert code == 0


def test_run_hook_passes_env_vars():
    captured = {}

    def fake_run(cmd, shell, env):
        captured.update(env)
        class R:
            returncode = 0
        return R()

    H.set_hook("pre_save", "echo test")
    with patch("subprocess.run", side_effect=fake_run):
        H.run_hook("pre_save", "snap123")

    assert captured["STASHRUN_SNAPSHOT"] == "snap123"
    assert captured["STASHRUN_EVENT"] == "pre_save"
