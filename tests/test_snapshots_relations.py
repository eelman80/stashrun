import pytest
from unittest.mock import patch
from stashrun.snapshots_relations import (
    add_relation, remove_relation, get_relations,
    find_related, clear_relations, RELATION_TYPES
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_add_relation_valid():
    assert add_relation("snap_a", "snap_b", "related") is True


def test_add_relation_invalid_type():
    assert add_relation("snap_a", "snap_b", "unknown") is False


def test_add_relation_self_link():
    assert add_relation("snap_a", "snap_a", "related") is False


def test_add_relation_duplicate():
    add_relation("snap_a", "snap_b", "derived")
    assert add_relation("snap_a", "snap_b", "derived") is False


def test_add_multiple_relation_types():
    add_relation("snap_a", "snap_b", "related")
    add_relation("snap_a", "snap_b", "conflicting")
    rels = get_relations("snap_a")
    assert "snap_b" in rels["related"]
    assert "snap_b" in rels["conflicting"]


def test_remove_relation_existing():
    add_relation("snap_a", "snap_b", "related")
    assert remove_relation("snap_a", "snap_b", "related") is True
    assert find_related("snap_a", "related") == []


def test_remove_relation_missing():
    assert remove_relation("snap_a", "snap_b", "related") is False


def test_get_relations_empty():
    assert get_relations("nonexistent") == {}


def test_find_related_returns_list():
    add_relation("snap_a", "snap_b", "supersedes")
    add_relation("snap_a", "snap_c", "supersedes")
    result = find_related("snap_a", "supersedes")
    assert "snap_b" in result
    assert "snap_c" in result


def test_find_related_empty():
    assert find_related("snap_a", "derived") == []


def test_clear_relations_existing():
    add_relation("snap_a", "snap_b", "related")
    assert clear_relations("snap_a") is True
    assert get_relations("snap_a") == {}


def test_clear_relations_missing():
    assert clear_relations("nonexistent") is False


def test_relation_types_set():
    assert "related" in RELATION_TYPES
    assert "derived" in RELATION_TYPES
    assert "conflicting" in RELATION_TYPES
    assert "supersedes" in RELATION_TYPES
