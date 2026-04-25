"""Tests for snapshots_retention module."""
import pytest
from unittest.mock import patch, MagicMock

from stashrun import snapshots_retention as sr


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_set_retention_valid(isolated_stash_dir):
    assert sr.set_retention("mysnap", "keep_last", 5) is True


def test_set_retention_invalid_policy(isolated_stash_dir):
    assert sr.set_retention("mysnap", "bogus_policy") is False


def test_get_retention_after_set(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_last", 3)
    entry = sr.get_retention("mysnap")
    assert entry is not None
    assert entry["policy"] == "keep_last"
    assert entry["value"] == 3


def test_get_retention_missing_returns_none(isolated_stash_dir):
    assert sr.get_retention("nonexistent") is None


def test_set_retention_overwrites(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_last", 5)
    sr.set_retention("mysnap", "keep_days", 30)
    entry = sr.get_retention("mysnap")
    assert entry["policy"] == "keep_days"
    assert entry["value"] == 30


def test_remove_retention_existing(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_all")
    assert sr.remove_retention("mysnap") is True
    assert sr.get_retention("mysnap") is None


def test_remove_retention_missing(isolated_stash_dir):
    assert sr.remove_retention("ghost") is False


def test_list_retention_empty(isolated_stash_dir):
    assert sr.list_retention() == {}


def test_list_retention_multiple(isolated_stash_dir):
    sr.set_retention("a", "keep_last", 2)
    sr.set_retention("b", "keep_all")
    data = sr.list_retention()
    assert "a" in data
    assert "b" in data
    assert len(data) == 2


def test_apply_retention_no_policy(isolated_stash_dir):
    removed = sr.apply_retention("untracked")
    assert removed == []


def test_apply_retention_keep_all(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_all")
    removed = sr.apply_retention("mysnap")
    assert removed == []


def test_apply_retention_keep_last(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_last", 1)

    fake_history = [
        {"event": "save", "detail": {"snapshot": "mysnap_v1"}, "ts": 1000},
        {"event": "save", "detail": {"snapshot": "mysnap_v2"}, "ts": 2000},
        {"event": "save", "detail": {"snapshot": "mysnap_v3"}, "ts": 3000},
    ]

    with patch("stashrun.snapshots_retention.get_history", return_value=fake_history), \
         patch("stashrun.snapshots_retention.remove_snapshot", return_value=True) as mock_rm:
        removed = sr.apply_retention("mysnap")

    assert len(removed) == 2
    assert "mysnap_v1" in removed
    assert "mysnap_v2" in removed
    assert "mysnap_v3" not in removed


def test_apply_retention_keep_last_not_enough_history(isolated_stash_dir):
    sr.set_retention("mysnap", "keep_last", 5)

    fake_history = [
        {"event": "save", "detail": {"snapshot": "mysnap_v1"}, "ts": 1000},
    ]

    with patch("stashrun.snapshots_retention.get_history", return_value=fake_history), \
         patch("stashrun.snapshots_retention.remove_snapshot", return_value=True):
        removed = sr.apply_retention("mysnap")

    assert removed == []
