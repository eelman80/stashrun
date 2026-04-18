"""Tests for stashrun.snapshots_subscribers."""

import pytest

from stashrun import snapshots_subscribers as sub_mod
from stashrun.snapshots_subscribers import (
    subscribe,
    unsubscribe,
    list_subscribers,
    clear_subscribers,
    find_subscriptions,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_subscribe_new():
    assert subscribe("snap1", "alice") is True
    assert "alice" in list_subscribers("snap1")


def test_subscribe_duplicate():
    subscribe("snap1", "alice")
    assert subscribe("snap1", "alice") is False
    assert list_subscribers("snap1").count("alice") == 1


def test_subscribe_multiple_subscribers():
    subscribe("snap1", "alice")
    subscribe("snap1", "bob")
    subs = list_subscribers("snap1")
    assert "alice" in subs
    assert "bob" in subs


def test_unsubscribe_existing():
    subscribe("snap1", "alice")
    assert unsubscribe("snap1", "alice") is True
    assert "alice" not in list_subscribers("snap1")


def test_unsubscribe_missing():
    assert unsubscribe("snap1", "ghost") is False


def test_list_subscribers_empty():
    assert list_subscribers("nonexistent") == []


def test_clear_subscribers_returns_count():
    subscribe("snap1", "alice")
    subscribe("snap1", "bob")
    removed = clear_subscribers("snap1")
    assert removed == 2
    assert list_subscribers("snap1") == []


def test_clear_subscribers_missing_snapshot():
    assert clear_subscribers("ghost") == 0


def test_find_subscriptions_returns_snapshot_names():
    subscribe("snap1", "alice")
    subscribe("snap2", "alice")
    subscribe("snap3", "bob")
    result = find_subscriptions("alice")
    assert "snap1" in result
    assert "snap2" in result
    assert "snap3" not in result


def test_find_subscriptions_no_matches():
    subscribe("snap1", "bob")
    assert find_subscriptions("alice") == []


def test_subscribers_persist_across_calls():
    subscribe("snap1", "alice")
    subscribe("snap1", "bob")
    unsubscribe("snap1", "alice")
    subs = list_subscribers("snap1")
    assert subs == ["bob"]
