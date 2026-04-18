import pytest
from unittest.mock import patch
from stashrun import snapshots_dependencies as sd


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_add_dependency_new():
    assert sd.add_dependency("b", "a") is True
    assert "a" in sd.get_dependencies("b")


def test_add_dependency_duplicate():
    sd.add_dependency("b", "a")
    assert sd.add_dependency("b", "a") is False


def test_add_dependency_self_returns_false():
    assert sd.add_dependency("a", "a") is False


def test_add_multiple_dependencies():
    sd.add_dependency("c", "a")
    sd.add_dependency("c", "b")
    deps = sd.get_dependencies("c")
    assert "a" in deps and "b" in deps


def test_remove_dependency_existing():
    sd.add_dependency("b", "a")
    assert sd.remove_dependency("b", "a") is True
    assert sd.get_dependencies("b") == []


def test_remove_dependency_missing():
    assert sd.remove_dependency("b", "a") is False


def test_get_dependencies_missing_returns_empty():
    assert sd.get_dependencies("nonexistent") == []


def test_get_dependents():
    sd.add_dependency("b", "a")
    sd.add_dependency("c", "a")
    dependents = sd.get_dependents("a")
    assert "b" in dependents and "c" in dependents


def test_get_dependents_none():
    assert sd.get_dependents("orphan") == []


def test_clear_dependencies_existing():
    sd.add_dependency("b", "a")
    assert sd.clear_dependencies("b") is True
    assert sd.get_dependencies("b") == []


def test_clear_dependencies_missing():
    assert sd.clear_dependencies("ghost") is False


def test_all_dependencies_empty():
    assert sd.all_dependencies() == {}


def test_all_dependencies_returns_all():
    sd.add_dependency("b", "a")
    sd.add_dependency("c", "b")
    data = sd.all_dependencies()
    assert "b" in data and "c" in data
