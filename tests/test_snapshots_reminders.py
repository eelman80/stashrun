import time
import pytest
from unittest.mock import patch
from pathlib import Path

import stashrun.snapshots_reminders as R


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_set_and_get_reminder():
    R.set_reminder("snap1", "Review this snapshot")
    rem = R.get_reminder("snap1")
    assert rem is not None
    assert rem["message"] == "Review this snapshot"
    assert rem["due_ts"] is None


def test_set_reminder_with_due_ts():
    future = time.time() + 3600
    R.set_reminder("snap2", "Expires soon", due_ts=future)
    rem = R.get_reminder("snap2")
    assert abs(rem["due_ts"] - future) < 1


def test_get_reminder_missing_returns_none():
    assert R.get_reminder("nonexistent") is None


def test_set_reminder_overwrites():
    R.set_reminder("snap3", "First")
    R.set_reminder("snap3", "Second")
    assert R.get_reminder("snap3")["message"] == "Second"


def test_remove_reminder_existing():
    R.set_reminder("snap4", "To remove")
    assert R.remove_reminder("snap4") is True
    assert R.get_reminder("snap4") is None


def test_remove_reminder_missing_returns_false():
    assert R.remove_reminder("ghost") is False


def test_list_reminders_empty():
    assert R.list_reminders() == {}


def test_list_reminders_multiple():
    R.set_reminder("a", "msg a")
    R.set_reminder("b", "msg b")
    result = R.list_reminders()
    assert set(result.keys()) == {"a", "b"}


def test_due_reminders_past_only():
    past = time.time() - 10
    future = time.time() + 3600
    R.set_reminder("old", "overdue", due_ts=past)
    R.set_reminder("new", "upcoming", due_ts=future)
    R.set_reminder("noduedate", "no date")
    due = R.due_reminders()
    names = [n for n, _ in due]
    assert "old" in names
    assert "new" not in names
    assert "noduedate" not in names


def test_due_reminders_empty_when_none_past():
    future = time.time() + 9999
    R.set_reminder("future", "not yet", due_ts=future)
    assert R.due_reminders() == []
