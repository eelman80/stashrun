import pytest
from stashrun import snapshots_priority as sp


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_priority_valid():
    assert sp.set_priority("snap1", "high") is True
    assert sp.get_priority("snap1") == "high"


def test_set_priority_invalid_level():
    assert sp.set_priority("snap1", "urgent") is False
    assert sp.get_priority("snap1") == sp.DEFAULT_PRIORITY


def test_get_priority_default():
    assert sp.get_priority("nonexistent") == "normal"


def test_get_priority_custom_default():
    assert sp.get_priority("nonexistent", default="low") == "low"


def test_set_priority_overwrites():
    sp.set_priority("snap1", "low")
    sp.set_priority("snap1", "critical")
    assert sp.get_priority("snap1") == "critical"


def test_remove_priority_existing():
    sp.set_priority("snap1", "high")
    assert sp.remove_priority("snap1") is True
    assert sp.get_priority("snap1") == sp.DEFAULT_PRIORITY


def test_remove_priority_missing():
    assert sp.remove_priority("ghost") is False


def test_list_by_priority_match():
    sp.set_priority("a", "high")
    sp.set_priority("b", "low")
    sp.set_priority("c", "high")
    result = sp.list_by_priority("high")
    assert set(result) == {"a", "c"}


def test_list_by_priority_no_match():
    sp.set_priority("a", "normal")
    assert sp.list_by_priority("critical") == []


def test_all_priorities_returns_full_map():
    sp.set_priority("x", "low")
    sp.set_priority("y", "high")
    data = sp.all_priorities()
    assert data["x"] == "low"
    assert data["y"] == "high"


def test_all_valid_priority_levels():
    for level in sp.VALID_PRIORITIES:
        assert sp.set_priority("snap", level) is True
