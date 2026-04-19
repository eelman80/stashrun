"""Tests for snapshots_maturity module."""

import pytest
from stashrun.snapshots_maturity import (
    set_maturity, get_maturity, remove_maturity,
    list_maturity, find_by_maturity, DEFAULT_LEVEL
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_maturity_valid():
    assert set_maturity("snap1", "stable") is True


def test_set_maturity_invalid():
    assert set_maturity("snap1", "unknown") is False


def test_set_maturity_overwrites():
    set_maturity("snap1", "draft")
    set_maturity("snap1", "stable")
    assert get_maturity("snap1") == "stable"


def test_get_maturity_default():
    assert get_maturity("nonexistent") == DEFAULT_LEVEL


def test_get_maturity_custom_default():
    assert get_maturity("nonexistent", default="deprecated") == "deprecated"


def test_get_maturity_after_set():
    set_maturity("snap1", "deprecated")
    assert get_maturity("snap1") == "deprecated"


def test_remove_maturity_existing():
    set_maturity("snap1", "stable")
    assert remove_maturity("snap1") is True
    assert get_maturity("snap1") == DEFAULT_LEVEL


def test_remove_maturity_missing():
    assert remove_maturity("ghost") is False


def test_list_maturity_empty():
    assert list_maturity() == {}


def test_list_maturity_multiple():
    set_maturity("a", "draft")
    set_maturity("b", "stable")
    data = list_maturity()
    assert data["a"] == "draft"
    assert data["b"] == "stable"


def test_find_by_maturity_match():
    set_maturity("x", "stable")
    set_maturity("y", "draft")
    results = find_by_maturity("stable")
    assert "x" in results
    assert "y" not in results


def test_find_by_maturity_no_match():
    set_maturity("x", "draft")
    assert find_by_maturity("deprecated") == []
