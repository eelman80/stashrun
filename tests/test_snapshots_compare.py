"""Tests for stashrun/snapshots_compare.py"""

import pytest
from unittest.mock import patch
from stashrun.snapshots_compare import (
    compare_snapshots,
    keys_unique_to,
    keys_in_common,
    value_conflicts,
)

SNAPS = {
    "snap_a": {"FOO": "1", "BAR": "hello", "ONLY_A": "yes"},
    "snap_b": {"FOO": "2", "BAR": "hello", "ONLY_B": "yes"},
    "snap_c": {"FOO": "1", "BAZ": "world"},
}


def _fake_get(name):
    return SNAPS.get(name)


@pytest.fixture(autouse=True)
def mock_get_snapshot():
    with patch("stashrun.snapshots_compare.get_snapshot", side_effect=_fake_get):
        yield


def test_compare_snapshots_keys_union():
    result = compare_snapshots(["snap_a", "snap_b"])
    assert set(result["keys"]) == {"FOO", "BAR", "ONLY_A", "ONLY_B"}


def test_compare_snapshots_matrix_values():
    result = compare_snapshots(["snap_a", "snap_b"])
    assert result["matrix"]["FOO"] == ["1", "2"]
    assert result["matrix"]["BAR"] == ["hello", "hello"]


def test_compare_snapshots_absent_key_is_none():
    result = compare_snapshots(["snap_a", "snap_b"])
    assert result["matrix"]["ONLY_A"] == ["yes", None]
    assert result["matrix"]["ONLY_B"] == [None, "yes"]


def test_compare_snapshots_missing_snapshot():
    result = compare_snapshots(["snap_a", "nonexistent"])
    assert result["matrix"]["FOO"] == ["1", None]


def test_compare_snapshots_preserves_order():
    result = compare_snapshots(["snap_b", "snap_a"])
    assert result["snapshots"] == ["snap_b", "snap_a"]


def test_keys_unique_to_returns_only_unique():
    unique = keys_unique_to("snap_a", ["snap_b", "snap_c"])
    assert "ONLY_A" in unique
    assert "FOO" not in unique
    assert "BAR" not in unique


def test_keys_unique_to_empty_others():
    unique = keys_unique_to("snap_c", [])
    assert unique == SNAPS["snap_c"]


def test_keys_in_common_two_snapshots():
    common = keys_in_common(["snap_a", "snap_b"])
    assert set(common.keys()) == {"FOO", "BAR"}


def test_keys_in_common_no_overlap():
    common = keys_in_common(["snap_a", "snap_c"])
    assert "FOO" in common
    assert "BAR" not in common
    assert "BAZ" not in common


def test_keys_in_common_empty_list():
    assert keys_in_common([]) == {}


def test_value_conflicts_detects_diff():
    conflicts = value_conflicts(["snap_a", "snap_b"])
    assert "FOO" in conflicts
    assert "BAR" not in conflicts


def test_value_conflicts_no_conflicts():
    conflicts = value_conflicts(["snap_a", "snap_a"])
    assert conflicts == {}
