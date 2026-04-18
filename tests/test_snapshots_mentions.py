import pytest
from unittest.mock import patch
from stashrun import snapshots_mentions as sm


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_add_mention_new():
    assert sm.add_mention("snap1", "TICKET-123") is True
    assert "TICKET-123" in sm.get_mentions("snap1")


def test_add_mention_duplicate():
    sm.add_mention("snap1", "TICKET-123")
    assert sm.add_mention("snap1", "TICKET-123") is False
    assert sm.get_mentions("snap1").count("TICKET-123") == 1


def test_add_multiple_mentions():
    sm.add_mention("snap1", "TICKET-1")
    sm.add_mention("snap1", "TICKET-2")
    refs = sm.get_mentions("snap1")
    assert "TICKET-1" in refs
    assert "TICKET-2" in refs


def test_remove_mention_existing():
    sm.add_mention("snap1", "TICKET-123")
    assert sm.remove_mention("snap1", "TICKET-123") is True
    assert sm.get_mentions("snap1") == []


def test_remove_mention_missing():
    assert sm.remove_mention("snap1", "TICKET-999") is False


def test_remove_cleans_up_empty_entry():
    sm.add_mention("snap1", "REF-1")
    sm.remove_mention("snap1", "REF-1")
    data = sm._load_mentions()
    assert "snap1" not in data


def test_get_mentions_missing_returns_empty():
    assert sm.get_mentions("nonexistent") == []


def test_clear_mentions_existing():
    sm.add_mention("snap1", "A")
    sm.add_mention("snap1", "B")
    assert sm.clear_mentions("snap1") is True
    assert sm.get_mentions("snap1") == []


def test_clear_mentions_missing():
    assert sm.clear_mentions("ghost") is False


def test_find_by_mention_match():
    sm.add_mention("snap1", "JIRA-42")
    sm.add_mention("snap2", "JIRA-42")
    sm.add_mention("snap3", "OTHER-1")
    result = sm.find_by_mention("JIRA-42")
    assert "snap1" in result
    assert "snap2" in result
    assert "snap3" not in result


def test_find_by_mention_no_match():
    assert sm.find_by_mention("NOTHING") == []
