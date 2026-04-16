"""Tests for snapshots_stats module."""
import pytest
from unittest.mock import patch
from stashrun import snapshots_stats


SNAPS = {
    "alpha": {"A": "1", "B": "2", "C": "3"},
    "beta": {"A": "10", "B": "20"},
    "gamma": {"A": "100"},
}


def _fake_list():
    return list(SNAPS.keys())


def _fake_get(name):
    return SNAPS.get(name)


def _fake_tags(name):
    return ["t"] if name == "alpha" else []


def _fake_pins():
    return ["alpha", "beta"]


@pytest.fixture(autouse=True)
def mock_deps():
    with patch.object(snapshots_stats, "list_all_snapshots", _fake_list), \
         patch.object(snapshots_stats, "get_snapshot", _fake_get), \
         patch.object(snapshots_stats, "get_tags", _fake_tags), \
         patch.object(snapshots_stats, "list_pins", _fake_pins):
        yield


def test_snapshot_count():
    assert snapshots_stats.snapshot_count() == 3


def test_total_keys():
    assert snapshots_stats.total_keys() == 6


def test_average_keys():
    assert snapshots_stats.average_keys() == pytest.approx(2.0)


def test_most_common_keys_order():
    result = snapshots_stats.most_common_keys(3)
    assert result[0] == ("A", 3)
    assert result[1] == ("B", 2)
    assert result[2] == ("C", 1)


def test_most_common_keys_top_n():
    result = snapshots_stats.most_common_keys(1)
    assert len(result) == 1
    assert result[0][0] == "A"


def test_tagged_snapshot_count():
    assert snapshots_stats.tagged_snapshot_count() == 1


def test_pinned_snapshot_count():
    assert snapshots_stats.pinned_snapshot_count() == 2


def test_summary_keys():
    s = snapshots_stats.summary()
    assert s["total_snapshots"] == 3
    assert s["total_keys"] == 6
    assert s["average_keys"] == 2.0
    assert s["tagged"] == 1
    assert s["pinned"] == 2
    assert isinstance(s["most_common_keys"], list)
