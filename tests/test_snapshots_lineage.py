import pytest
from unittest.mock import patch
from stashrun import snapshots_lineage as lin


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_parent_creates_entry():
    assert lin.set_parent("child", "parent") is True
    assert lin.get_parent("child") == "parent"


def test_set_parent_self_reference_returns_false():
    assert lin.set_parent("snap", "snap") is False
    assert lin.get_parent("snap") is None


def test_get_parent_missing_returns_none():
    assert lin.get_parent("nonexistent") is None


def test_get_children_returns_direct_children():
    lin.set_parent("child1", "root")
    lin.set_parent("child2", "root")
    lin.set_parent("other", "elsewhere")
    children = lin.get_children("root")
    assert set(children) == {"child1", "child2"}


def test_get_children_no_children_returns_empty():
    assert lin.get_children("orphan") == []


def test_remove_lineage_existing():
    lin.set_parent("child", "parent")
    assert lin.remove_lineage("child") is True
    assert lin.get_parent("child") is None


def test_remove_lineage_missing_returns_false():
    assert lin.remove_lineage("ghost") is False


def test_get_ancestors_chain():
    lin.set_parent("c", "b")
    lin.set_parent("b", "a")
    ancestors = lin.get_ancestors("c")
    assert ancestors == ["b", "a"]


def test_get_ancestors_no_parent_returns_empty():
    assert lin.get_ancestors("root") == []


def test_get_ancestors_cycle_protection():
    lin.set_parent("x", "y")
    lin.set_parent("y", "x")  # cycle
    ancestors = lin.get_ancestors("x")
    assert "x" not in ancestors  # should not loop forever


def test_lineage_summary_includes_children():
    lin.set_parent("child", "parent")
    summary = lin.lineage_summary()
    assert "child" in summary
    assert summary["child"]["parent"] == "parent"
