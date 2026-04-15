"""Tests for stashrun.watchlist."""

import pytest
from stashrun import watchlist


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.storage._stash_dir", None)
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stashrun"))
    yield tmp_path / ".stashrun"


def test_watch_key_new():
    result = watchlist.watch_key("MY_KEY")
    assert result is True
    assert "MY_KEY" in watchlist.get_watched_keys()


def test_watch_key_duplicate():
    watchlist.watch_key("MY_KEY")
    result = watchlist.watch_key("MY_KEY")
    assert result is False
    assert watchlist.get_watched_keys().count("MY_KEY") == 1


def test_watch_key_with_label():
    watchlist.watch_key("DB_URL", label="Database URL")
    keys = watchlist.get_watched_keys()
    assert "DB_URL" in keys


def test_unwatch_existing():
    watchlist.watch_key("TOKEN")
    result = watchlist.unwatch_key("TOKEN")
    assert result is True
    assert "TOKEN" not in watchlist.get_watched_keys()


def test_unwatch_missing():
    result = watchlist.unwatch_key("NONEXISTENT")
    assert result is False


def test_get_watched_keys_empty():
    assert watchlist.get_watched_keys() == []


def test_get_watched_keys_multiple():
    watchlist.watch_key("A")
    watchlist.watch_key("B")
    watchlist.watch_key("C")
    keys = watchlist.get_watched_keys()
    assert set(keys) == {"A", "B", "C"}


def test_is_watched_true():
    watchlist.watch_key("SECRET")
    assert watchlist.is_watched("SECRET") is True


def test_is_watched_false():
    assert watchlist.is_watched("NOT_THERE") is False


def test_check_watched_changes_detects_change():
    watchlist.watch_key("PORT")
    changes = watchlist.check_watched_changes({"PORT": "8080"}, {"PORT": "9090"})
    assert len(changes) == 1
    assert changes[0]["key"] == "PORT"
    assert changes[0]["old"] == "8080"
    assert changes[0]["new"] == "9090"


def test_check_watched_changes_no_change():
    watchlist.watch_key("PORT")
    changes = watchlist.check_watched_changes({"PORT": "8080"}, {"PORT": "8080"})
    assert changes == []


def test_check_watched_changes_added_key():
    watchlist.watch_key("NEW_KEY")
    changes = watchlist.check_watched_changes({}, {"NEW_KEY": "hello"})
    assert len(changes) == 1
    assert changes[0]["old"] is None
    assert changes[0]["new"] == "hello"


def test_check_watched_changes_removed_key():
    watchlist.watch_key("GONE")
    changes = watchlist.check_watched_changes({"GONE": "value"}, {})
    assert len(changes) == 1
    assert changes[0]["old"] == "value"
    assert changes[0]["new"] is None


def test_check_watched_changes_ignores_unwatched():
    watchlist.watch_key("WATCHED")
    changes = watchlist.check_watched_changes(
        {"WATCHED": "a", "OTHER": "x"},
        {"WATCHED": "a", "OTHER": "y"},
    )
    assert changes == []
