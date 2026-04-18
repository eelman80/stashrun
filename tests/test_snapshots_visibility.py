import pytest
from unittest.mock import patch
from stashrun.snapshots_visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_by_visibility,
    is_visible,
)


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_visibility_valid(isolated_stash_dir):
    assert set_visibility("snap1", "public") is True
    assert get_visibility("snap1") == "public"


def test_set_visibility_invalid_level(isolated_stash_dir):
    assert set_visibility("snap1", "restricted") is False
    assert get_visibility("snap1") == "private"  # default


def test_get_visibility_default(isolated_stash_dir):
    assert get_visibility("nonexistent") == "private"


def test_get_visibility_custom_default(isolated_stash_dir):
    assert get_visibility("nonexistent", default="public") == "public"


def test_set_visibility_overwrites(isolated_stash_dir):
    set_visibility("snap1", "public")
    set_visibility("snap1", "hidden")
    assert get_visibility("snap1") == "hidden"


def test_remove_visibility_existing(isolated_stash_dir):
    set_visibility("snap1", "public")
    assert remove_visibility("snap1") is True
    assert get_visibility("snap1") == "private"


def test_remove_visibility_missing(isolated_stash_dir):
    assert remove_visibility("ghost") is False


def test_list_by_visibility(isolated_stash_dir):
    set_visibility("a", "public")
    set_visibility("b", "hidden")
    set_visibility("c", "public")
    assert sorted(list_by_visibility("public")) == ["a", "c"]
    assert list_by_visibility("hidden") == ["b"]
    assert list_by_visibility("private") == []


def test_is_visible_public_to_public(isolated_stash_dir):
    set_visibility("snap1", "public")
    assert is_visible("snap1", "public") is True


def test_is_visible_private_to_public(isolated_stash_dir):
    set_visibility("snap1", "private")
    assert is_visible("snap1", "public") is False


def test_is_visible_private_to_private(isolated_stash_dir):
    set_visibility("snap1", "private")
    assert is_visible("snap1", "private") is True


def test_is_visible_hidden_to_hidden(isolated_stash_dir):
    set_visibility("snap1", "hidden")
    assert is_visible("snap1", "hidden") is True


def test_is_visible_hidden_to_private(isolated_stash_dir):
    set_visibility("snap1", "hidden")
    assert is_visible("snap1", "private") is False
