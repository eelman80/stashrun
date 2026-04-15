"""Tests for stashrun.tags module."""

from __future__ import annotations

import pytest

from stashrun import tags as tag_mod


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / "stash"))
    yield tmp_path / "stash"


def test_add_tag_new():
    assert tag_mod.add_tag("snap1", "prod") is True
    assert "prod" in tag_mod.get_tags("snap1")


def test_add_tag_duplicate():
    tag_mod.add_tag("snap1", "prod")
    assert tag_mod.add_tag("snap1", "prod") is False
    assert tag_mod.get_tags("snap1").count("prod") == 1


def test_add_multiple_tags():
    tag_mod.add_tag("snap1", "prod")
    tag_mod.add_tag("snap1", "stable")
    tags = tag_mod.get_tags("snap1")
    assert "prod" in tags
    assert "stable" in tags


def test_remove_tag_existing():
    tag_mod.add_tag("snap1", "prod")
    assert tag_mod.remove_tag("snap1", "prod") is True
    assert "prod" not in tag_mod.get_tags("snap1")


def test_remove_tag_missing():
    assert tag_mod.remove_tag("snap1", "ghost") is False


def test_remove_last_tag_cleans_entry():
    tag_mod.add_tag("snap1", "only")
    tag_mod.remove_tag("snap1", "only")
    assert tag_mod.all_tags().get("snap1") is None


def test_find_by_tag_returns_snapshots():
    tag_mod.add_tag("snap1", "prod")
    tag_mod.add_tag("snap2", "prod")
    tag_mod.add_tag("snap3", "dev")
    result = tag_mod.find_by_tag("prod")
    assert set(result) == {"snap1", "snap2"}


def test_find_by_tag_no_match():
    assert tag_mod.find_by_tag("nonexistent") == []


def test_get_tags_unknown_snapshot():
    assert tag_mod.get_tags("unknown") == []


def test_remove_snapshot_tags():
    tag_mod.add_tag("snap1", "prod")
    tag_mod.add_tag("snap1", "stable")
    tag_mod.remove_snapshot_tags("snap1")
    assert tag_mod.get_tags("snap1") == []
    assert "snap1" not in tag_mod.all_tags()


def test_all_tags_returns_full_index():
    tag_mod.add_tag("a", "x")
    tag_mod.add_tag("b", "y")
    index = tag_mod.all_tags()
    assert index["a"] == ["x"]
    assert index["b"] == ["y"]


def test_find_by_tag_returns_sorted():
    """Snapshots returned by find_by_tag should be in a consistent order."""
    tag_mod.add_tag("snap3", "release")
    tag_mod.add_tag("snap1", "release")
    tag_mod.add_tag("snap2", "release")
    result = tag_mod.find_by_tag("release")
    assert result == sorted(result)
