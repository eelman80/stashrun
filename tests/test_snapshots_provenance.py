"""Tests for stashrun.snapshots_provenance."""

import pytest

from stashrun.snapshots_provenance import (
    set_provenance,
    get_provenance,
    remove_provenance,
    list_provenance,
    find_by_origin,
    find_by_method,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_provenance_creates_entry():
    entry = set_provenance("snap1", origin="ci-pipeline")
    assert entry["origin"] == "ci-pipeline"
    assert entry["method"] == "manual"


def test_set_provenance_with_all_fields():
    entry = set_provenance(
        "snap2",
        origin="local",
        method="template",
        source_context="dev-env",
        created_by="alice",
    )
    assert entry["method"] == "template"
    assert entry["source_context"] == "dev-env"
    assert entry["created_by"] == "alice"


def test_get_provenance_returns_entry():
    set_provenance("snap3", origin="github-actions", method="automated")
    entry = get_provenance("snap3")
    assert entry is not None
    assert entry["origin"] == "github-actions"
    assert entry["method"] == "automated"


def test_get_provenance_missing_returns_none():
    assert get_provenance("nonexistent") is None


def test_set_provenance_overwrites():
    set_provenance("snap4", origin="first")
    set_provenance("snap4", origin="second")
    entry = get_provenance("snap4")
    assert entry["origin"] == "second"


def test_remove_provenance_existing():
    set_provenance("snap5", origin="local")
    assert remove_provenance("snap5") is True
    assert get_provenance("snap5") is None


def test_remove_provenance_missing_returns_false():
    assert remove_provenance("ghost") is False


def test_list_provenance_returns_all():
    set_provenance("a", origin="x")
    set_provenance("b", origin="y")
    data = list_provenance()
    assert "a" in data
    assert "b" in data


def test_list_provenance_empty():
    assert list_provenance() == {}


def test_find_by_origin_match():
    set_provenance("snap6", origin="ci-pipeline")
    set_provenance("snap7", origin="local-dev")
    results = find_by_origin("ci")
    assert "snap6" in results
    assert "snap7" not in results


def test_find_by_origin_case_insensitive():
    set_provenance("snap8", origin="CI-Pipeline")
    results = find_by_origin("ci-pipeline")
    assert "snap8" in results


def test_find_by_origin_no_match():
    set_provenance("snap9", origin="local")
    assert find_by_origin("github") == []


def test_find_by_method_match():
    set_provenance("snap10", origin="x", method="template")
    set_provenance("snap11", origin="y", method="manual")
    results = find_by_method("template")
    assert "snap10" in results
    assert "snap11" not in results


def test_find_by_method_no_match():
    set_provenance("snap12", origin="x", method="manual")
    assert find_by_method("automated") == []
