"""Tests for snapshots_sentiment module."""

import pytest
from unittest.mock import patch

from stashrun import snapshots_sentiment as sm


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_sentiment.get_stash_dir", lambda: tmp_path)


def test_set_sentiment_valid():
    assert sm.set_sentiment("snap1", "positive") is True
    assert sm.get_sentiment("snap1") == "positive"


def test_set_sentiment_invalid():
    assert sm.set_sentiment("snap1", "ecstatic") is False
    assert sm.get_sentiment("snap1") == "neutral"  # default


def test_set_sentiment_overwrites():
    sm.set_sentiment("snap1", "positive")
    sm.set_sentiment("snap1", "negative")
    assert sm.get_sentiment("snap1") == "negative"


def test_get_sentiment_default():
    assert sm.get_sentiment("nonexistent") == "neutral"


def test_get_sentiment_custom_default():
    assert sm.get_sentiment("nonexistent", default="mixed") == "mixed"


def test_remove_sentiment_existing():
    sm.set_sentiment("snap1", "positive")
    assert sm.remove_sentiment("snap1") is True
    assert sm.get_sentiment("snap1") == "neutral"


def test_remove_sentiment_missing():
    assert sm.remove_sentiment("ghost") is False


def test_list_sentiments_empty():
    assert sm.list_sentiments() == {}


def test_list_sentiments_populated():
    sm.set_sentiment("a", "positive")
    sm.set_sentiment("b", "negative")
    result = sm.list_sentiments()
    assert result == {"a": "positive", "b": "negative"}


def test_find_by_sentiment_match():
    sm.set_sentiment("a", "positive")
    sm.set_sentiment("b", "neutral")
    sm.set_sentiment("c", "positive")
    result = sm.find_by_sentiment("positive")
    assert sorted(result) == ["a", "c"]


def test_find_by_sentiment_no_match():
    sm.set_sentiment("a", "neutral")
    assert sm.find_by_sentiment("negative") == []


def test_all_valid_sentiments_accepted():
    for s in sm.VALID_SENTIMENTS:
        assert sm.set_sentiment("snap", s) is True
