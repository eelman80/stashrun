"""Tests for stashrun.scheduling."""

from __future__ import annotations

import pytest

from stashrun import scheduling


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(scheduling, "get_stash_dir", lambda: tmp_path)
    return tmp_path


def test_set_schedule_creates_entry():
    entry = scheduling.set_schedule("nightly", "prod", "0 2 * * *")
    assert entry["snapshot"] == "prod"
    assert entry["cron"] == "0 2 * * *"


def test_set_schedule_overwrites():
    scheduling.set_schedule("nightly", "prod", "0 2 * * *")
    entry = scheduling.set_schedule("nightly", "staging", "0 3 * * *")
    assert entry["snapshot"] == "staging"
    assert entry["cron"] == "0 3 * * *"


def test_get_schedule_returns_entry():
    scheduling.set_schedule("weekly", "backup", "0 0 * * 0")
    entry = scheduling.get_schedule("weekly")
    assert entry is not None
    assert entry["snapshot"] == "backup"


def test_get_schedule_missing_returns_none():
    assert scheduling.get_schedule("nonexistent") is None


def test_remove_schedule_existing():
    scheduling.set_schedule("daily", "dev", "0 1 * * *")
    result = scheduling.remove_schedule("daily")
    assert result is True
    assert scheduling.get_schedule("daily") is None


def test_remove_schedule_missing_returns_false():
    result = scheduling.remove_schedule("ghost")
    assert result is False


def test_list_schedules_empty():
    assert scheduling.list_schedules() == {}


def test_list_schedules_multiple():
    scheduling.set_schedule("a", "snap1", "0 1 * * *")
    scheduling.set_schedule("b", "snap2", "0 2 * * *")
    result = scheduling.list_schedules()
    assert set(result.keys()) == {"a", "b"}


def test_find_schedules_for_snapshot():
    scheduling.set_schedule("s1", "prod", "0 1 * * *")
    scheduling.set_schedule("s2", "prod", "0 2 * * *")
    scheduling.set_schedule("s3", "dev", "0 3 * * *")
    names = scheduling.find_schedules_for_snapshot("prod")
    assert sorted(names) == ["s1", "s2"]


def test_find_schedules_for_snapshot_none_match():
    scheduling.set_schedule("s1", "staging", "0 1 * * *")
    names = scheduling.find_schedules_for_snapshot("prod")
    assert names == []


def test_schedules_persisted_to_disk(tmp_path):
    scheduling.set_schedule("persist", "snap", "* * * * *")
    assert (tmp_path / "schedules.json").exists()
