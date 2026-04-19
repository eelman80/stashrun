"""Tests for snapshots_lifecycle module."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_lifecycle import (
    set_lifecycle,
    get_lifecycle,
    remove_lifecycle,
    list_by_state,
    lifecycle_summary,
    LIFECYCLE_STATES,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_lifecycle_valid():
    assert set_lifecycle("snap1", "active") is True


def test_set_lifecycle_invalid():
    assert set_lifecycle("snap1", "unknown") is False


def test_set_lifecycle_all_valid_states():
    for state in LIFECYCLE_STATES:
        assert set_lifecycle("snap", state) is True


def test_get_lifecycle_default():
    assert get_lifecycle("missing") == "active"


def test_get_lifecycle_custom_default():
    assert get_lifecycle("missing", default="draft") == "draft"


def test_get_lifecycle_after_set():
    set_lifecycle("snap1", "deprecated")
    assert get_lifecycle("snap1") == "deprecated"


def test_set_lifecycle_overwrites():
    set_lifecycle("snap1", "draft")
    set_lifecycle("snap1", "retired")
    assert get_lifecycle("snap1") == "retired"


def test_remove_lifecycle_existing():
    set_lifecycle("snap1", "active")
    assert remove_lifecycle("snap1") is True
    assert get_lifecycle("snap1") == "active"  # back to default


def test_remove_lifecycle_missing():
    assert remove_lifecycle("ghost") is False


def test_list_by_state_returns_matches():
    set_lifecycle("a", "draft")
    set_lifecycle("b", "draft")
    set_lifecycle("c", "active")
    result = list_by_state("draft")
    assert set(result) == {"a", "b"}


def test_list_by_state_empty():
    assert list_by_state("retired") == []


def test_lifecycle_summary_structure():
    set_lifecycle("x", "active")
    set_lifecycle("y", "retired")
    summary = lifecycle_summary()
    assert set(summary.keys()) == LIFECYCLE_STATES
    assert "x" in summary["active"]
    assert "y" in summary["retired"]
    assert summary["draft"] == []
