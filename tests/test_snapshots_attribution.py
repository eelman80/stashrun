"""Tests for stashrun.snapshots_attribution."""

from __future__ import annotations

import pytest

from stashrun.snapshots_attribution import (
    add_contributor,
    find_by_author,
    get_attribution,
    list_attributions,
    remove_attribution,
    set_attribution,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_attribution_creates_entry():
    set_attribution("snap1", "alice")
    info = get_attribution("snap1")
    assert info is not None
    assert info["author"] == "alice"
    assert info["contributors"] == []
    assert info["source"] is None


def test_set_attribution_with_contributors():
    set_attribution("snap2", "bob", contributors=["carol", "dave"])
    info = get_attribution("snap2")
    assert set(info["contributors"]) == {"carol", "dave"}


def test_set_attribution_with_source():
    set_attribution("snap3", "eve", source="ci-pipeline")
    info = get_attribution("snap3")
    assert info["source"] == "ci-pipeline"


def test_set_attribution_overwrites():
    set_attribution("snap4", "alice")
    set_attribution("snap4", "bob", contributors=["carol"])
    info = get_attribution("snap4")
    assert info["author"] == "bob"
    assert "carol" in info["contributors"]


def test_get_attribution_missing_returns_none():
    assert get_attribution("nonexistent") is None


def test_add_contributor_new():
    set_attribution("snap5", "alice")
    result = add_contributor("snap5", "frank")
    assert result is True
    info = get_attribution("snap5")
    assert "frank" in info["contributors"]


def test_add_contributor_duplicate_no_change():
    set_attribution("snap6", "alice", contributors=["grace"])
    add_contributor("snap6", "grace")
    info = get_attribution("snap6")
    assert info["contributors"].count("grace") == 1


def test_add_contributor_missing_entry_returns_false():
    result = add_contributor("no-such-snap", "heidi")
    assert result is False


def test_remove_attribution_existing():
    set_attribution("snap7", "alice")
    result = remove_attribution("snap7")
    assert result is True
    assert get_attribution("snap7") is None


def test_remove_attribution_missing_returns_false():
    result = remove_attribution("ghost")
    assert result is False


def test_list_attributions_empty():
    assert list_attributions() == {}


def test_list_attributions_returns_all():
    set_attribution("a", "alice")
    set_attribution("b", "bob")
    entries = list_attributions()
    assert set(entries.keys()) == {"a", "b"}


def test_find_by_author_returns_matching():
    set_attribution("x", "alice")
    set_attribution("y", "alice")
    set_attribution("z", "bob")
    result = find_by_author("alice")
    assert set(result) == {"x", "y"}


def test_find_by_author_no_match():
    set_attribution("w", "carol")
    result = find_by_author("nobody")
    assert result == []
