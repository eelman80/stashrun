import pytest
from unittest.mock import patch
from stashrun import snapshots_changelog as cl


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_and_get_changelog():
    cl.set_changelog("snap1", "Initial release")
    assert cl.get_changelog("snap1") == "Initial release"


def test_get_changelog_missing_returns_none():
    assert cl.get_changelog("ghost") is None


def test_set_changelog_overwrites():
    cl.set_changelog("snap1", "v1")
    cl.set_changelog("snap1", "v2")
    assert cl.get_changelog("snap1") == "v2"


def test_remove_changelog_existing():
    cl.set_changelog("snap1", "msg")
    result = cl.remove_changelog("snap1")
    assert result is True
    assert cl.get_changelog("snap1") is None


def test_remove_changelog_missing_returns_false():
    assert cl.remove_changelog("nope") is False


def test_list_changelogs_empty():
    assert cl.list_changelogs() == {}


def test_list_changelogs_multiple():
    cl.set_changelog("a", "msg-a")
    cl.set_changelog("b", "msg-b")
    entries = cl.list_changelogs()
    assert entries == {"a": "msg-a", "b": "msg-b"}


def test_clear_changelogs_returns_count():
    cl.set_changelog("x", "one")
    cl.set_changelog("y", "two")
    count = cl.clear_changelogs()
    assert count == 2
    assert cl.list_changelogs() == {}


def test_clear_changelogs_empty_returns_zero():
    assert cl.clear_changelogs() == 0
