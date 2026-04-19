"""Tests for stashrun.snapshots_merge."""

import pytest
from unittest.mock import patch, MagicMock
from stashrun.snapshots_merge import (
    merge_envs,
    merge_snapshots,
    merge_conflicts,
    MERGE_STRATEGY_LAST_WINS,
    MERGE_STRATEGY_FIRST_WINS,
    MERGE_STRATEGY_STRICT,
)


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_envs_no_conflicts():
    a = {"A": "1", "B": "2"}
    b = {"C": "3"}
    merged, conflicts = merge_envs([a, b])
    assert merged == {"A": "1", "B": "2", "C": "3"}
    assert conflicts == []


def test_merge_envs_last_wins():
    a = {"KEY": "old"}
    b = {"KEY": "new"}
    merged, conflicts = merge_envs([a, b], strategy=MERGE_STRATEGY_LAST_WINS)
    assert merged["KEY"] == "new"
    assert "KEY" in conflicts


def test_merge_envs_first_wins():
    a = {"KEY": "first"}
    b = {"KEY": "second"}
    merged, conflicts = merge_envs([a, b], strategy=MERGE_STRATEGY_FIRST_WINS)
    assert merged["KEY"] == "first"
    assert "KEY" in conflicts


def test_merge_envs_strict_raises_on_conflict():
    a = {"KEY": "x"}
    b = {"KEY": "y"}
    with pytest.raises(ValueError, match="KEY"):
        merge_envs([a, b], strategy=MERGE_STRATEGY_STRICT)


def test_merge_envs_strict_no_conflict_ok():
    a = {"A": "1"}
    b = {"B": "2"}
    merged, conflicts = merge_envs([a, b], strategy=MERGE_STRATEGY_STRICT)
    assert merged == {"A": "1", "B": "2"}
    assert conflicts == []


def test_merge_envs_three_sources():
    envs = [{"X": "1"}, {"Y": "2"}, {"Z": "3"}]
    merged, conflicts = merge_envs(envs)
    assert merged == {"X": "1", "Y": "2", "Z": "3"}
    assert conflicts == []


def test_merge_envs_empty_list():
    """Merging an empty list of envs should return an empty dict with no conflicts."""
    merged, conflicts = merge_envs([])
    assert merged == {}
    assert conflicts == []


def test_merge_envs_single_source():
    """Merging a single env should return it unchanged with no conflicts."""
    env = {"A": "1", "B": "2"}
    merged, conflicts = merge_envs([env])
    assert merged == {"A": "1", "B": "2"}
    assert conflicts == []


# ---------------------------------------------------------------------------
# merge_snapshots
# ---------------------------------------------------------------------------

def _fake_get(name):
    data = {
        "snap_a": {"A": "1", "SHARED": "from_a"},
        "snap_b": {"B": "2", "SHARED": "from_b"},
    }
    return data.get(name)


@patch("stashrun.snapshots_merge.create_snapshot")
@patch("stashrun.snapshots_merge.get_snapshot", side_effect=_fake_get)
def test_merge_snapshots_success(mock_get, mock_create):
    result = merge_snapshots(["snap_a", "snap_b"], "merged")
    assert result is not None
    assert result["A"] == "1"
    assert result["B"] == "2"
    assert result["SHARED"] == "from_b"  # last wins
    mock_create.assert_called_once()


@patch("stashrun.snapshots_merge.get_snapshot", return_value=None)
def test_merge_snapshots_missing_returns_none(mock_get):
    result = merge_snapshots(["missing"], "out")
    assert result is None


# ---------------------------------------------------------------------------
# merge_conflicts
# ---------------------------------------------------------------------------

@patch("stashrun.snapshots_merge.get_snapshot", side_effect=_fake_get)
def test_merge_conflicts_dete