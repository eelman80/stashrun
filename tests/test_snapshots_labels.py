import pytest
from unittest.mock import patch
from stashrun import snapshots_labels as sl


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_label_creates_entry():
    sl.set_label("snap1", "production config")
    assert sl.get_label("snap1") == "production config"


def test_set_label_overwrites():
    sl.set_label("snap1", "old label")
    sl.set_label("snap1", "new label")
    assert sl.get_label("snap1") == "new label"


def test_get_label_missing_returns_none():
    assert sl.get_label("nonexistent") is None


def test_remove_label_existing():
    sl.set_label("snap1", "some label")
    result = sl.remove_label("snap1")
    assert result is True
    assert sl.get_label("snap1") is None


def test_remove_label_missing_returns_false():
    result = sl.remove_label("ghost")
    assert result is False


def test_list_labels_empty():
    assert sl.list_labels() == {}


def test_list_labels_multiple():
    sl.set_label("a", "alpha")
    sl.set_label("b", "beta")
    labels = sl.list_labels()
    assert labels == {"a": "alpha", "b": "beta"}


def test_find_by_label_match():
    sl.set_label("snap1", "production database")
    sl.set_label("snap2", "staging config")
    results = sl.find_by_label("production")
    assert results == ["snap1"]


def test_find_by_label_case_insensitive():
    sl.set_label("snap1", "Production Config")
    results = sl.find_by_label("production")
    assert "snap1" in results


def test_find_by_label_no_match():
    sl.set_label("snap1", "staging")
    results = sl.find_by_label("production")
    assert results == []


def test_find_by_label_multiple_matches():
    sl.set_label("snap1", "prod-api")
    sl.set_label("snap2", "prod-db")
    sl.set_label("snap3", "staging")
    results = sl.find_by_label("prod")
    assert set(results) == {"snap1", "snap2"}
