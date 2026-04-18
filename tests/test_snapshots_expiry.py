"""Tests for snapshots_expiry module."""

import time
import pytest
from unittest.mock import patch, MagicMock

from stashrun import snapshots_expiry as expiry_mod


FUTURE_TS = time.time() + 9999
PAST_TS = time.time() - 1


@patch("stashrun.snapshots_expiry.get_ttl")
def test_is_expired_no_ttl(mock_get):
    mock_get.return_value = None
    assert expiry_mod.is_expired("snap1") is False


@patch("stashrun.snapshots_expiry.get_ttl")
def test_is_expired_future(mock_get):
    mock_get.return_value = FUTURE_TS
    assert expiry_mod.is_expired("snap1") is False


@patch("stashrun.snapshots_expiry.get_ttl")
def test_is_expired_past(mock_get):
    mock_get.return_value = PAST_TS
    assert expiry_mod.is_expired("snap1") is True


@patch("stashrun.snapshots_expiry.list_ttl")
def test_list_expired_returns_only_past(mock_list):
    mock_list.return_value = {"old": PAST_TS, "new": FUTURE_TS}
    result = expiry_mod.list_expired()
    assert result == ["old"]


@patch("stashrun.snapshots_expiry.list_ttl")
def test_list_expired_empty(mock_list):
    mock_list.return_value = {}
    assert expiry_mod.list_expired() == []


@patch("stashrun.snapshots_expiry.remove_ttl")
@patch("stashrun.snapshots_expiry.remove_snapshot")
@patch("stashrun.snapshots_expiry.list_expired")
def test_purge_expired_deletes(mock_list, mock_remove, mock_rm_ttl):
    mock_list.return_value = ["snap_a", "snap_b"]
    mock_remove.return_value = True
    purged = expiry_mod.purge_expired()
    assert purged == ["snap_a", "snap_b"]
    assert mock_remove.call_count == 2
    assert mock_rm_ttl.call_count == 2


@patch("stashrun.snapshots_expiry.list_expired")
def test_purge_expired_dry_run(mock_list):
    mock_list.return_value = ["snap_x"]
    purged = expiry_mod.purge_expired(dry_run=True)
    assert purged == ["snap_x"]


@patch("stashrun.snapshots_expiry.get_ttl")
def test_expiry_status_no_ttl(mock_get):
    mock_get.return_value = None
    status = expiry_mod.expiry_status("mysnap")
    assert status["has_ttl"] is False
    assert status["expired"] is False


@patch("stashrun.snapshots_expiry.get_ttl")
def test_expiry_status_expired(mock_get):
    mock_get.return_value = PAST_TS
    status = expiry_mod.expiry_status("mysnap")
    assert status["has_ttl"] is True
    assert status["expired"] is True
    assert "expiry_iso" in status
