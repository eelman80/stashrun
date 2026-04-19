import pytest
from unittest.mock import patch
from stashrun import snapshots_endorsements as se


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_add_endorsement_new(isolated_stash_dir):
    assert se.add_endorsement("snap1", "alice") is True
    assert "alice" in se.get_endorsements("snap1")


def test_add_endorsement_duplicate(isolated_stash_dir):
    se.add_endorsement("snap1", "alice")
    assert se.add_endorsement("snap1", "alice") is False
    assert se.get_endorsements("snap1").count("alice") == 1


def test_add_multiple_endorsers(isolated_stash_dir):
    se.add_endorsement("snap1", "alice")
    se.add_endorsement("snap1", "bob")
    endorsers = se.get_endorsements("snap1")
    assert "alice" in endorsers
    assert "bob" in endorsers


def test_remove_endorsement_existing(isolated_stash_dir):
    se.add_endorsement("snap1", "alice")
    assert se.remove_endorsement("snap1", "alice") is True
    assert "alice" not in se.get_endorsements("snap1")


def test_remove_endorsement_missing(isolated_stash_dir):
    assert se.remove_endorsement("snap1", "ghost") is False


def test_get_endorsements_empty(isolated_stash_dir):
    assert se.get_endorsements("unknown") == []


def test_endorsement_count(isolated_stash_dir):
    se.add_endorsement("snap1", "alice")
    se.add_endorsement("snap1", "bob")
    assert se.endorsement_count("snap1") == 2


def test_clear_endorsements_existing(isolated_stash_dir):
    se.add_endorsement("snap1", "alice")
    assert se.clear_endorsements("snap1") is True
    assert se.get_endorsements("snap1") == []


def test_clear_endorsements_missing(isolated_stash_dir):
    assert se.clear_endorsements("nonexistent") is False


def test_top_endorsed(isolated_stash_dir):
    se.add_endorsement("snap_a", "alice")
    se.add_endorsement("snap_a", "bob")
    se.add_endorsement("snap_b", "carol")
    top = se.top_endorsed(n=2)
    assert top[0] == ("snap_a", 2)
    assert top[1] == ("snap_b", 1)


def test_top_endorsed_empty(isolated_stash_dir):
    assert se.top_endorsed() == []
