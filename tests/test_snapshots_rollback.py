"""Tests for stashrun.snapshots_rollback."""

import pytest
from unittest.mock import patch, MagicMock

from stashrun.snapshots_rollback import (
    get_rollback_candidates,
    rollback_snapshot,
    rollback_to_index,
)


def _make_save_event(env: dict) -> dict:
    return {"event": "save", "detail": {"env": env}}


@patch("stashrun.snapshots_rollback.get_history")
def test_get_rollback_candidates_filters_saves(mock_hist):
    mock_hist.return_value = [
        {"event": "save", "detail": {"env": {"A": "1"}}},
        {"event": "restore", "detail": {}},
        {"event": "save", "detail": {"env": {"A": "2"}}},
    ]
    result = get_rollback_candidates("mysnap")
    assert len(result) == 2
    assert all(e["event"] == "save" for e in result)


@patch("stashrun.snapshots_rollback.get_history")
def test_get_rollback_candidates_empty(mock_hist):
    mock_hist.return_value = []
    assert get_rollback_candidates("x") == []


@patch("stashrun.snapshots_rollback.record_event")
@patch("stashrun.snapshots_rollback.create_snapshot")
@patch("stashrun.snapshots_rollback.get_history")
def test_rollback_snapshot_one_step(mock_hist, mock_create, mock_record):
    envs = [{"A": "1"}, {"A": "2"}, {"A": "3"}]
    mock_hist.return_value = [_make_save_event(e) for e in envs]

    result = rollback_snapshot("snap", steps=1)
    assert result == {"A": "2"}
    mock_create.assert_called_once_with("snap", env={"A": "2"})
    mock_record.assert_called_once()


@patch("stashrun.snapshots_rollback.record_event")
@patch("stashrun.snapshots_rollback.create_snapshot")
@patch("stashrun.snapshots_rollback.get_history")
def test_rollback_snapshot_not_enough_history(mock_hist, mock_create, mock_record):
    mock_hist.return_value = [_make_save_event({"A": "1"})]
    result = rollback_snapshot("snap", steps=1)
    assert result is None
    mock_create.assert_not_called()


@patch("stashrun.snapshots_rollback.record_event")
@patch("stashrun.snapshots_rollback.create_snapshot")
@patch("stashrun.snapshots_rollback.get_history")
def test_rollback_to_index_success(mock_hist, mock_create, mock_record):
    envs = [{"X": "a"}, {"X": "b"}, {"X": "c"}]
    mock_hist.return_value = [_make_save_event(e) for e in envs]

    result = rollback_to_index("snap", index=1)
    assert result == {"X": "b"}
    mock_create.assert_called_once_with("snap", env={"X": "b"})


@patch("stashrun.snapshots_rollback.record_event")
@patch("stashrun.snapshots_rollback.create_snapshot")
@patch("stashrun.snapshots_rollback.get_history")
def test_rollback_to_index_out_of_range(mock_hist, mock_create, mock_record):
    mock_hist.return_value = [_make_save_event({"Y": "1"})]
    result = rollback_to_index("snap", index=5)
    assert result is None
    mock_create.assert_not_called()


@patch("stashrun.snapshots_rollback.record_event")
@patch("stashrun.snapshots_rollback.create_snapshot")
@patch("stashrun.snapshots_rollback.get_history")
def test_rollback_missing_env_in_detail(mock_hist, mock_create, mock_record):
    mock_hist.return_value = [
        {"event": "save", "detail": {}},
        {"event": "save", "detail": {}},
    ]
    result = rollback_snapshot("snap", steps=1)
    assert result is None
    mock_create.assert_not_called()
