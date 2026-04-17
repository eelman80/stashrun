import pytest
from unittest.mock import patch
from stashrun import snapshots_groups as sg


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_create_group_new():
    assert sg.create_group("mygroup") is True
    assert "mygroup" in sg.list_groups()


def test_create_group_duplicate():
    sg.create_group("mygroup")
    assert sg.create_group("mygroup") is False


def test_delete_group_existing():
    sg.create_group("g1")
    assert sg.delete_group("g1") is True
    assert "g1" not in sg.list_groups()


def test_delete_group_missing():
    assert sg.delete_group("ghost") is False


def test_add_to_group_success():
    sg.create_group("g1")
    assert sg.add_to_group("g1", "snap_a") is True
    assert "snap_a" in sg.get_group("g1")


def test_add_to_group_no_duplicate():
    sg.create_group("g1")
    sg.add_to_group("g1", "snap_a")
    sg.add_to_group("g1", "snap_a")
    assert sg.get_group("g1").count("snap_a") == 1


def test_add_to_group_missing_group():
    assert sg.add_to_group("nonexistent", "snap_a") is False


def test_remove_from_group_existing():
    sg.create_group("g1")
    sg.add_to_group("g1", "snap_a")
    assert sg.remove_from_group("g1", "snap_a") is True
    assert "snap_a" not in sg.get_group("g1")


def test_remove_from_group_missing():
    sg.create_group("g1")
    assert sg.remove_from_group("g1", "snap_x") is False


def test_get_group_missing_returns_none():
    assert sg.get_group("nope") is None


def test_list_groups_empty():
    assert sg.list_groups() == []


def test_find_groups_for_snapshot():
    sg.create_group("a")
    sg.create_group("b")
    sg.add_to_group("a", "snap1")
    sg.add_to_group("b", "snap1")
    result = sg.find_groups_for_snapshot("snap1")
    assert "a" in result
    assert "b" in result


def test_find_groups_for_snapshot_not_member():
    sg.create_group("a")
    assert sg.find_groups_for_snapshot("snap_x") == []
