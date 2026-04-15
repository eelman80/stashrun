"""Tests for stashrun.notes."""

from __future__ import annotations

import pytest

from stashrun import notes as notes_mod


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path / ".stash"))
    yield tmp_path / ".stash"


def test_set_note_creates_entry():
    notes_mod.set_note("snap1", "initial release env")
    assert notes_mod.get_note("snap1") == "initial release env"


def test_set_note_overwrites():
    notes_mod.set_note("snap1", "old note")
    notes_mod.set_note("snap1", "new note")
    assert notes_mod.get_note("snap1") == "new note"


def test_get_note_missing_returns_none():
    assert notes_mod.get_note("nonexistent") is None


def test_remove_note_existing():
    notes_mod.set_note("snap2", "to be removed")
    result = notes_mod.remove_note("snap2")
    assert result is True
    assert notes_mod.get_note("snap2") is None


def test_remove_note_missing_returns_false():
    result = notes_mod.remove_note("ghost")
    assert result is False


def test_list_notes_empty():
    assert notes_mod.list_notes() == {}


def test_list_notes_multiple():
    notes_mod.set_note("a", "note a")
    notes_mod.set_note("b", "note b")
    result = notes_mod.list_notes()
    assert result == {"a": "note a", "b": "note b"}


def test_list_notes_returns_copy():
    notes_mod.set_note("x", "hello")
    result = notes_mod.list_notes()
    result["x"] = "mutated"
    assert notes_mod.get_note("x") == "hello"


def test_rename_note_success():
    notes_mod.set_note("old", "important note")
    result = notes_mod.rename_note("old", "new")
    assert result is True
    assert notes_mod.get_note("new") == "important note"
    assert notes_mod.get_note("old") is None


def test_rename_note_missing_returns_false():
    result = notes_mod.rename_note("does_not_exist", "target")
    assert result is False


def test_notes_persisted_to_disk(isolated_stash_dir):
    notes_mod.set_note("persistent", "saved value")
    notes_file = isolated_stash_dir / "notes.json"
    assert notes_file.exists()
    import json
    data = json.loads(notes_file.read_text())
    assert data["persistent"] == "saved value"
