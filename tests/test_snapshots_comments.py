import pytest
from unittest.mock import patch
from stashrun import snapshots_comments as sc


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_and_get_comment():
    sc.set_comment("snap1", "DB_HOST", "primary host")
    assert sc.get_comment("snap1", "DB_HOST") == "primary host"


def test_get_comment_missing_returns_none():
    assert sc.get_comment("snap1", "MISSING") is None


def test_set_comment_overwrites():
    sc.set_comment("snap1", "KEY", "old")
    sc.set_comment("snap1", "KEY", "new")
    assert sc.get_comment("snap1", "KEY") == "new"


def test_remove_comment_existing():
    sc.set_comment("snap1", "KEY", "hello")
    assert sc.remove_comment("snap1", "KEY") is True
    assert sc.get_comment("snap1", "KEY") is None


def test_remove_comment_missing_returns_false():
    assert sc.remove_comment("snap1", "NOPE") is False


def test_remove_last_key_cleans_snapshot_entry():
    sc.set_comment("snap1", "K", "v")
    sc.remove_comment("snap1", "K")
    data = sc._load_comments()
    assert "snap1" not in data


def test_get_all_comments_returns_dict():
    sc.set_comment("snap1", "A", "alpha")
    sc.set_comment("snap1", "B", "beta")
    result = sc.get_all_comments("snap1")
    assert result == {"A": "alpha", "B": "beta"}


def test_get_all_comments_empty_snapshot():
    assert sc.get_all_comments("nonexistent") == {}


def test_clear_comments_returns_count():
    sc.set_comment("snap1", "X", "1")
    sc.set_comment("snap1", "Y", "2")
    count = sc.clear_comments("snap1")
    assert count == 2
    assert sc.get_all_comments("snap1") == {}


def test_clear_comments_missing_snapshot_returns_zero():
    assert sc.clear_comments("ghost") == 0


def test_comments_isolated_per_snapshot():
    sc.set_comment("s1", "K", "for s1")
    sc.set_comment("s2", "K", "for s2")
    assert sc.get_comment("s1", "K") == "for s1"
    assert sc.get_comment("s2", "K") == "for s2"
