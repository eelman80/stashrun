"""Tests for stashrun.history module."""

import time
import pytest

from stashrun import history
from stashrun.storage import get_stash_dir


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def test_record_event_creates_entry():
    history.record_event("mysnap", "save")
    entries = history.get_history()
    assert len(entries) == 1
    assert entries[0]["snapshot"] == "mysnap"
    assert entries[0]["action"] == "save"


def test_record_event_with_detail():
    history.record_event("mysnap", "export", detail="json")
    entries = history.get_history()
    assert entries[0]["detail"] == "json"


def test_record_event_stores_timestamp():
    before = time.time()
    history.record_event("snap", "restore")
    after = time.time()
    entries = history.get_history()
    assert before <= entries[0]["timestamp"] <= after


def test_get_history_filter_by_name():
    history.record_event("alpha", "save")
    history.record_event("beta", "restore")
    history.record_event("alpha", "delete")
    entries = history.get_history(snapshot_name="alpha")
    assert len(entries) == 2
    assert all(e["snapshot"] == "alpha" for e in entries)


def test_get_history_no_filter_returns_all():
    history.record_event("alpha", "save")
    history.record_event("beta", "save")
    assert len(history.get_history()) == 2


def test_get_history_empty_when_no_file():
    assert history.get_history() == []


def test_clear_history_all():
    history.record_event("a", "save")
    history.record_event("b", "save")
    removed = history.clear_history()
    assert removed == 2
    assert history.get_history() == []


def test_clear_history_by_snapshot():
    history.record_event("alpha", "save")
    history.record_event("beta", "save")
    history.record_event("alpha", "restore")
    removed = history.clear_history(snapshot_name="alpha")
    assert removed == 2
    remaining = history.get_history()
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "beta"


def test_history_trims_to_max_entries(monkeypatch):
    monkeypatch.setattr(history, "_MAX_ENTRIES", 5)
    for i in range(8):
        history.record_event(f"snap{i}", "save")
    entries = history.get_history()
    assert len(entries) == 5
    # Should keep the most recent
    assert entries[-1]["snapshot"] == "snap7"
