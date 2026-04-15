"""Tests for stashrun/snapshots_search.py"""

import pytest
from unittest.mock import patch
from stashrun import snapshots_search
from stashrun.snapshots_search import (
    search_by_name,
    search_by_tag,
    search_by_key,
    search_by_value,
    search_by_key_pattern,
)

ALL_SNAPSHOTS = ["dev-local", "prod-api", "staging-db", "dev-remote"]

SNAPSHOT_DATA = {
    "dev-local": {"APP_ENV": "development", "DB_HOST": "localhost"},
    "prod-api": {"APP_ENV": "production", "API_KEY": "secret123"},
    "staging-db": {"APP_ENV": "staging", "DB_HOST": "staging.db"},
    "dev-remote": {"APP_ENV": "development", "REMOTE_URL": "https://example.com"},
}

TAGS_DATA = {
    "dev-local": ["dev", "local"],
    "prod-api": ["prod"],
    "staging-db": ["staging", "db"],
    "dev-remote": ["dev", "remote"],
}


@pytest.fixture(autouse=True)
def mock_storage(monkeypatch):
    monkeypatch.setattr(snapshots_search, "list_snapshots", lambda d=None: ALL_SNAPSHOTS)
    monkeypatch.setattr(snapshots_search, "load_snapshot", lambda name, d=None: SNAPSHOT_DATA.get(name))
    monkeypatch.setattr(snapshots_search, "get_tags", lambda name, d=None: TAGS_DATA.get(name, []))


def test_search_by_name_match():
    results = search_by_name("dev")
    assert "dev-local" in results
    assert "dev-remote" in results
    assert "prod-api" not in results


def test_search_by_name_case_insensitive():
    results = search_by_name("PROD")
    assert "prod-api" in results


def test_search_by_name_no_match():
    results = search_by_name("zzz")
    assert results == []


def test_search_by_tag_match():
    results = search_by_tag("dev")
    assert "dev-local" in results
    assert "dev-remote" in results
    assert "prod-api" not in results


def test_search_by_tag_no_match():
    results = search_by_tag("nonexistent")
    assert results == []


def test_search_by_key_exact():
    results = search_by_key("API_KEY")
    assert results == ["prod-api"]


def test_search_by_key_common_key():
    results = search_by_key("DB_HOST")
    assert "dev-local" in results
    assert "staging-db" in results


def test_search_by_key_missing():
    results = search_by_key("NONEXISTENT")
    assert results == []


def test_search_by_value_match():
    results = search_by_value("localhost")
    assert results == ["dev-local"]


def test_search_by_value_multiple():
    results = search_by_value("development")
    assert "dev-local" in results
    assert "dev-remote" in results


def test_search_by_key_pattern():
    results = search_by_key_pattern("db")
    assert "dev-local" in results
    assert "staging-db" in results


def test_search_by_key_pattern_case_insensitive():
    results = search_by_key_pattern("APP")
    assert len(results) == 4
