import pytest
from stashrun.snapshots_bookmarks import (
    set_bookmark, remove_bookmark, resolve_bookmark,
    list_bookmarks, rename_bookmark,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_bookmark_creates_entry():
    set_bookmark("prod", "production-2024")
    assert resolve_bookmark("prod") == "production-2024"


def test_set_bookmark_overwrites():
    set_bookmark("prod", "snap-v1")
    set_bookmark("prod", "snap-v2")
    assert resolve_bookmark("prod") == "snap-v2"


def test_resolve_missing_returns_none():
    assert resolve_bookmark("ghost") is None


def test_remove_bookmark_existing():
    set_bookmark("dev", "dev-snap")
    result = remove_bookmark("dev")
    assert result is True
    assert resolve_bookmark("dev") is None


def test_remove_bookmark_missing():
    assert remove_bookmark("nonexistent") is False


def test_list_bookmarks_empty():
    assert list_bookmarks() == {}


def test_list_bookmarks_multiple():
    set_bookmark("a", "snap-a")
    set_bookmark("b", "snap-b")
    bm = list_bookmarks()
    assert bm == {"a": "snap-a", "b": "snap-b"}


def test_rename_bookmark_success():
    set_bookmark("old", "snap-x")
    result = rename_bookmark("old", "new")
    assert result is True
    assert resolve_bookmark("new") == "snap-x"
    assert resolve_bookmark("old") is None


def test_rename_bookmark_missing():
    assert rename_bookmark("ghost", "new") is False
