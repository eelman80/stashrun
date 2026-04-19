import pytest
from unittest.mock import patch
from stashrun import snapshots_categories as sc


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("stashrun.snapshots_categories.get_stash_dir", lambda: tmp_path)


def test_set_and_get_category():
    sc.set_category("snap1", "production")
    assert sc.get_category("snap1") == "production"


def test_get_category_missing_returns_default():
    assert sc.get_category("missing") == "uncategorized"


def test_get_category_custom_default():
    assert sc.get_category("missing", default="other") == "other"


def test_set_category_overwrites():
    sc.set_category("snap1", "dev")
    sc.set_category("snap1", "staging")
    assert sc.get_category("snap1") == "staging"


def test_remove_category_existing():
    sc.set_category("snap1", "dev")
    assert sc.remove_category("snap1") is True
    assert sc.get_category("snap1") == "uncategorized"


def test_remove_category_missing():
    assert sc.remove_category("ghost") is False


def test_list_categories_empty():
    assert sc.list_categories() == {}


def test_list_categories_multiple():
    sc.set_category("a", "prod")
    sc.set_category("b", "dev")
    data = sc.list_categories()
    assert data == {"a": "prod", "b": "dev"}


def test_find_by_category_match():
    sc.set_category("a", "prod")
    sc.set_category("b", "dev")
    sc.set_category("c", "prod")
    result = sc.find_by_category("prod")
    assert sorted(result) == ["a", "c"]


def test_find_by_category_no_match():
    sc.set_category("a", "dev")
    assert sc.find_by_category("prod") == []


def test_all_category_names():
    sc.set_category("a", "prod")
    sc.set_category("b", "dev")
    sc.set_category("c", "prod")
    cats = sc.all_category_names()
    assert cats == ["dev", "prod"]


def test_all_category_names_empty():
    assert sc.all_category_names() == []
