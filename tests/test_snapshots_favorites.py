import pytest
from unittest.mock import patch
from stashrun import snapshots_favorites as fav_mod


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(fav_mod, "get_stash_dir", lambda: tmp_path)
    yield tmp_path


def test_add_favorite_new():
    assert fav_mod.add_favorite("snap1") is True
    assert "snap1" in fav_mod.list_favorites()


def test_add_favorite_duplicate():
    fav_mod.add_favorite("snap1")
    assert fav_mod.add_favorite("snap1") is False
    assert fav_mod.list_favorites().count("snap1") == 1


def test_add_multiple_favorites():
    fav_mod.add_favorite("a")
    fav_mod.add_favorite("b")
    fav_mod.add_favorite("c")
    assert fav_mod.list_favorites() == ["a", "b", "c"]


def test_remove_existing():
    fav_mod.add_favorite("snap1")
    assert fav_mod.remove_favorite("snap1") is True
    assert "snap1" not in fav_mod.list_favorites()


def test_remove_missing():
    assert fav_mod.remove_favorite("ghost") is False


def test_is_favorite_true():
    fav_mod.add_favorite("snap1")
    assert fav_mod.is_favorite("snap1") is True


def test_is_favorite_false():
    assert fav_mod.is_favorite("snap1") is False


def test_list_favorites_empty():
    assert fav_mod.list_favorites() == []


def test_clear_favorites():
    fav_mod.add_favorite("a")
    fav_mod.add_favorite("b")
    count = fav_mod.clear_favorites()
    assert count == 2
    assert fav_mod.list_favorites() == []


def test_clear_favorites_empty():
    count = fav_mod.clear_favorites()
    assert count == 0
