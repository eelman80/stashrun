"""Tests for stashrun.storage module."""

import json
import os
import pytest
from pathlib import Path

from stashrun.storage import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
    snapshot_path,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    """Redirect all snapshot I/O to a temporary directory."""
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_save_snapshot_creates_file():
    path = save_snapshot("myproject", {"API_KEY": "abc123", "DEBUG": "true"})
    assert path.exists()


def test_save_snapshot_content():
    env = {"DB_URL": "postgres://localhost/dev", "PORT": "5432"}
    save_snapshot("db-dev", env, description="Local DB config")
    data = json.loads(snapshot_path("db-dev").read_text())
    assert data["name"] == "db-dev"
    assert data["description"] == "Local DB config"
    assert data["env"] == env
    assert "created_at" in data


def test_load_snapshot_returns_dict():
    save_snapshot("staging", {"ENV": "staging"})
    result = load_snapshot("staging")
    assert result is not None
    assert result["env"]["ENV"] == "staging"


def test_load_snapshot_missing_returns_none():
    result = load_snapshot("nonexistent")
    assert result is None


def test_list_snapshots_empty():
    assert list_snapshots() == []


def test_list_snapshots_returns_metadata():
    save_snapshot("alpha", {"X": "1"}, description="first")
    save_snapshot("beta", {"Y": "2", "Z": "3"})
    snapshots = list_snapshots()
    assert len(snapshots) == 2
    names = {s["name"] for s in snapshots}
    assert names == {"alpha", "beta"}
    beta = next(s for s in snapshots if s["name"] == "beta")
    assert beta["var_count"] == 2


def test_delete_snapshot_removes_file():
    save_snapshot("temp", {"TMP": "yes"})
    assert delete_snapshot("temp") is True
    assert load_snapshot("temp") is None


def test_delete_snapshot_nonexistent_returns_false():
    assert delete_snapshot("ghost") is False
