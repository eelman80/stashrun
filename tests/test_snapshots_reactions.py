import pytest
from unittest.mock import patch
from stashrun import snapshots_reactions as sr


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_reactions.get_stash_dir", lambda: tmp_path)
    return tmp_path


def test_add_reaction_valid(isolated_stash_dir):
    assert sr.add_reaction("snap1", "👍") is True
    assert "👍" in sr.get_reactions("snap1")


def test_add_reaction_invalid(isolated_stash_dir):
    assert sr.add_reaction("snap1", "💩") is False
    assert sr.get_reactions("snap1") == []


def test_add_reaction_duplicate(isolated_stash_dir):
    sr.add_reaction("snap1", "🔥")
    sr.add_reaction("snap1", "🔥")
    assert sr.get_reactions("snap1").count("🔥") == 1


def test_add_multiple_reactions(isolated_stash_dir):
    sr.add_reaction("snap1", "👍")
    sr.add_reaction("snap1", "✅")
    reactions = sr.get_reactions("snap1")
    assert "👍" in reactions
    assert "✅" in reactions


def test_remove_reaction_existing(isolated_stash_dir):
    sr.add_reaction("snap1", "👍")
    assert sr.remove_reaction("snap1", "👍") is True
    assert "👍" not in sr.get_reactions("snap1")


def test_remove_reaction_missing(isolated_stash_dir):
    assert sr.remove_reaction("snap1", "👍") is False


def test_remove_last_reaction_cleans_entry(isolated_stash_dir):
    sr.add_reaction("snap1", "🚀")
    sr.remove_reaction("snap1", "🚀")
    assert "snap1" not in sr.list_all_reactions()


def test_get_reactions_missing_returns_empty(isolated_stash_dir):
    assert sr.get_reactions("nonexistent") == []


def test_clear_reactions_existing(isolated_stash_dir):
    sr.add_reaction("snap1", "👍")
    assert sr.clear_reactions("snap1") is True
    assert sr.get_reactions("snap1") == []


def test_clear_reactions_missing(isolated_stash_dir):
    assert sr.clear_reactions("ghost") is False


def test_list_all_reactions(isolated_stash_dir):
    sr.add_reaction("a", "👍")
    sr.add_reaction("b", "🐛")
    data = sr.list_all_reactions()
    assert "a" in data
    assert "b" in data
