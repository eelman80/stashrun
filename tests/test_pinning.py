"""Tests for stashrun.pinning."""

from __future__ import annotations

import pytest

from stashrun import pinning
from stashrun.storage import get_stash_dir


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    yield tmp_path


def test_pin_snapshot_new():
    assert pinning.pin_snapshot("snap1") is True


def test_pin_snapshot_duplicate():
    pinning.pin_snapshot("snap1")
    assert pinning.pin_snapshot("snap1") is False


def test_pin_multiple_snapshots():
    pinning.pin_snapshot("snap1")
    pinning.pin_snapshot("snap2")
    pins = pinning.list_pins()
    assert "snap1" in pins
    assert "snap2" in pins


def test_unpin_existing():
    pinning.pin_snapshot("snap1")
    assert pinning.unpin_snapshot("snap1") is True
    assert pinning.is_pinned("snap1") is False


def test_unpin_missing():
    assert pinning.unpin_snapshot("ghost") is False


def test_is_pinned_true():
    pinning.pin_snapshot("snap1")
    assert pinning.is_pinned("snap1") is True


def test_is_pinned_false():
    assert pinning.is_pinned("nope") is False


def test_list_pins_empty():
    assert pinning.list_pins() == []


def test_list_pins_sorted():
    pinning.pin_snapshot("z_snap")
    pinning.pin_snapshot("a_snap")
    pins = pinning.list_pins()
    assert pins == sorted(pins)


def test_clear_pins_returns_count():
    pinning.pin_snapshot("snap1")
    pinning.pin_snapshot("snap2")
    assert pinning.clear_pins() == 2


def test_clear_pins_empties_list():
    pinning.pin_snapshot("snap1")
    pinning.clear_pins()
    assert pinning.list_pins() == []


def test_pins_file_created():
    pinning.pin_snapshot("snap1")
    assert (get_stash_dir() / "pins.json").exists()
