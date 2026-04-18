"""Tests for snapshots_versioning module."""

import pytest
from unittest.mock import patch

from stashrun import snapshots_versioning as sv


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


ENV_A = {"FOO": "1", "BAR": "2"}
ENV_B = {"FOO": "99", "BAR": "2", "BAZ": "3"}


def _save(name, env):
    from stashrun.storage import save_snapshot
    save_snapshot(name, env)


def test_push_version_returns_version_number():
    _save("snap", ENV_A)
    n = sv.push_version("snap")
    assert n == 1


def test_push_version_increments():
    _save("snap", ENV_A)
    sv.push_version("snap")
    _save("snap", ENV_B)
    n = sv.push_version("snap")
    assert n == 2


def test_push_version_missing_returns_none():
    result = sv.push_version("ghost")
    assert result is None


def test_list_versions_empty():
    assert sv.list_versions("snap") == []


def test_list_versions_after_push():
    _save("snap", ENV_A)
    sv.push_version("snap")
    versions = sv.list_versions("snap")
    assert len(versions) == 1
    assert versions[0] == ENV_A


def test_get_version_valid_index():
    _save("snap", ENV_A)
    sv.push_version("snap")
    env = sv.get_version("snap", 1)
    assert env == ENV_A


def test_get_version_out_of_range_returns_none():
    _save("snap", ENV_A)
    sv.push_version("snap")
    assert sv.get_version("snap", 5) is None
    assert sv.get_version("snap", 0) is None


def test_restore_version_updates_active():
    from stashrun.storage import load_snapshot
    _save("snap", ENV_A)
    sv.push_version("snap")
    _save("snap", ENV_B)
    sv.push_version("snap")
    ok = sv.restore_version("snap", 1)
    assert ok is True
    assert load_snapshot("snap") == ENV_A


def test_restore_version_missing_returns_false():
    assert sv.restore_version("snap", 3) is False


def test_drop_versions_removes_all():
    _save("snap", ENV_A)
    sv.push_version("snap")
    ok = sv.drop_versions("snap")
    assert ok is True
    assert sv.list_versions("snap") == []


def test_drop_versions_missing_returns_false():
    assert sv.drop_versions("ghost") is False


def test_version_count():
    _save("snap", ENV_A)
    sv.push_version("snap")
    sv.push_version("snap")
    assert sv.version_count("snap") == 2
