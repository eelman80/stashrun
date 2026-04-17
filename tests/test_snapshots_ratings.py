"""Tests for snapshots_ratings module."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_ratings import set_rating, get_rating, remove_rating, list_ratings, top_rated


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_rating_valid(isolated_stash_dir):
    assert set_rating("snap1", 4) is True
    assert get_rating("snap1") == 4


def test_set_rating_invalid_low(isolated_stash_dir):
    assert set_rating("snap1", 0) is False
    assert get_rating("snap1") is None


def test_set_rating_invalid_high(isolated_stash_dir):
    assert set_rating("snap1", 6) is False


def test_set_rating_overwrites(isolated_stash_dir):
    set_rating("snap1", 3)
    set_rating("snap1", 5)
    assert get_rating("snap1") == 5


def test_get_rating_missing_returns_none(isolated_stash_dir):
    assert get_rating("nonexistent") is None


def test_remove_rating_existing(isolated_stash_dir):
    set_rating("snap1", 2)
    assert remove_rating("snap1") is True
    assert get_rating("snap1") is None


def test_remove_rating_missing_returns_false(isolated_stash_dir):
    assert remove_rating("ghost") is False


def test_list_ratings_empty(isolated_stash_dir):
    assert list_ratings() == {}


def test_list_ratings_multiple(isolated_stash_dir):
    set_rating("a", 1)
    set_rating("b", 5)
    data = list_ratings()
    assert data["a"] == 1
    assert data["b"] == 5


def test_top_rated_order(isolated_stash_dir):
    set_rating("low", 1)
    set_rating("mid", 3)
    set_rating("high", 5)
    results = top_rated(3)
    assert results[0] == ("high", 5)
    assert results[1] == ("mid", 3)
    assert results[2] == ("low", 1)


def test_top_rated_limits_results(isolated_stash_dir):
    for i, name in enumerate(["a", "b", "c", "d", "e"], start=1):
        set_rating(name, i)
    results = top_rated(2)
    assert len(results) == 2
