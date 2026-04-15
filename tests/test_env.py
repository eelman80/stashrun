"""Tests for stashrun.env module."""

import os
import pytest

from stashrun.env import capture_env, apply_env, diff_env, filter_env


def test_capture_env_all():
    env = capture_env()
    assert isinstance(env, dict)
    assert len(env) > 0


def test_capture_env_specific_keys(monkeypatch):
    monkeypatch.setenv("STASH_TEST_A", "alpha")
    monkeypatch.setenv("STASH_TEST_B", "beta")
    env = capture_env(keys=["STASH_TEST_A", "STASH_TEST_B", "STASH_TEST_MISSING"])
    assert env == {"STASH_TEST_A": "alpha", "STASH_TEST_B": "beta"}


def test_capture_env_missing_key_excluded(monkeypatch):
    monkeypatch.delenv("STASH_NONEXISTENT", raising=False)
    env = capture_env(keys=["STASH_NONEXISTENT"])
    assert "STASH_NONEXISTENT" not in env


def test_apply_env_sets_variables(monkeypatch):
    monkeypatch.delenv("STASH_APPLY_X", raising=False)
    apply_env({"STASH_APPLY_X": "hello"})
    assert os.environ["STASH_APPLY_X"] == "hello"


def test_apply_env_overwrite_true(monkeypatch):
    monkeypatch.setenv("STASH_APPLY_Y", "original")
    apply_env({"STASH_APPLY_Y": "updated"}, overwrite=True)
    assert os.environ["STASH_APPLY_Y"] == "updated"


def test_apply_env_overwrite_false(monkeypatch):
    monkeypatch.setenv("STASH_APPLY_Z", "keep")
    apply_env({"STASH_APPLY_Z": "ignore"}, overwrite=False)
    assert os.environ["STASH_APPLY_Z"] == "keep"


def test_diff_env_added():
    base = {"A": "1"}
    target = {"A": "1", "B": "2"}
    result = diff_env(base, target)
    assert result["added"] == {"B": "2"}
    assert result["removed"] == {}
    assert result["changed"] == {}


def test_diff_env_removed():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    result = diff_env(base, target)
    assert result["removed"] == {"B": "2"}


def test_diff_env_changed():
    base = {"A": "old"}
    target = {"A": "new"}
    result = diff_env(base, target)
    assert result["changed"] == {"A": {"old": "old", "new": "new"}}


def test_filter_env_by_prefix():
    env = {"AWS_KEY": "k", "AWS_SECRET": "s", "PATH": "/usr/bin"}
    filtered = filter_env(env, prefixes=["AWS_"])
    assert filtered == {"AWS_KEY": "k", "AWS_SECRET": "s"}


def test_filter_env_no_prefix_returns_all():
    env = {"A": "1", "B": "2"}
    assert filter_env(env) == env
