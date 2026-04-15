"""Tests for stashrun/snapshots_audit.py"""

from __future__ import annotations

import pytest

from stashrun.snapshots_audit import (
    clear_audit_log,
    get_audit_log,
    record_audit,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_record_audit_creates_entry():
    entry = record_audit("save", "mysnap")
    assert entry["action"] == "save"
    assert entry["snapshot"] == "mysnap"
    assert "timestamp" in entry
    assert "user" in entry


def test_record_audit_with_detail():
    entry = record_audit("restore", "mysnap", detail="forced restore")
    assert entry["detail"] == "forced restore"


def test_record_audit_custom_user():
    entry = record_audit("delete", "snap2", user="alice")
    assert entry["user"] == "alice"


def test_get_audit_log_all():
    record_audit("save", "snap-a")
    record_audit("restore", "snap-b")
    entries = get_audit_log()
    assert len(entries) == 2


def test_get_audit_log_filter_by_name():
    record_audit("save", "snap-a")
    record_audit("restore", "snap-b")
    entries = get_audit_log(snapshot_name="snap-a")
    assert len(entries) == 1
    assert entries[0]["snapshot"] == "snap-a"


def test_get_audit_log_filter_by_action():
    record_audit("save", "snap-a")
    record_audit("restore", "snap-a")
    record_audit("save", "snap-b")
    entries = get_audit_log(action="save")
    assert all(e["action"] == "save" for e in entries)
    assert len(entries) == 2


def test_get_audit_log_limit():
    for i in range(5):
        record_audit("save", f"snap-{i}")
    entries = get_audit_log(limit=3)
    assert len(entries) == 3
    assert entries[-1]["snapshot"] == "snap-4"


def test_clear_audit_log_all():
    record_audit("save", "snap-a")
    record_audit("save", "snap-b")
    removed = clear_audit_log()
    assert removed == 2
    assert get_audit_log() == []


def test_clear_audit_log_by_name():
    record_audit("save", "snap-a")
    record_audit("save", "snap-b")
    removed = clear_audit_log(snapshot_name="snap-a")
    assert removed == 1
    remaining = get_audit_log()
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "snap-b"


def test_get_audit_log_empty():
    assert get_audit_log() == []
