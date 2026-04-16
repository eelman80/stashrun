"""Tests for snapshots_batch module."""

import pytest
from unittest.mock import patch, MagicMock
from stashrun import snapshots_batch


SNAPS = {"dev": {"A": "1"}, "prod": {"B": "2"}, "staging": {"C": "3"}}


@patch("stashrun.snapshots_batch.remove_snapshot")
def test_batch_delete_all_success(mock_rm):
    mock_rm.return_value = True
    results = snapshots_batch.batch_delete(["dev", "prod"])
    assert results == {"dev": True, "prod": True}
    assert mock_rm.call_count == 2


@patch("stashrun.snapshots_batch.remove_snapshot")
def test_batch_delete_partial_failure(mock_rm):
    mock_rm.side_effect = [True, False]
    results = snapshots_batch.batch_delete(["dev", "missing"])
    assert results["dev"] is True
    assert results["missing"] is False


@patch("stashrun.snapshots_batch.remove_snapshot")
def test_batch_delete_exception_handled(mock_rm):
    mock_rm.side_effect = Exception("boom")
    results = snapshots_batch.batch_delete(["dev"])
    assert results["dev"] is False


@patch("stashrun.snapshots_batch.copy_snapshot")
def test_batch_copy_success(mock_cp):
    mock_cp.return_value = True
    results = snapshots_batch.batch_copy([("dev", "dev-bak")])
    assert results["dev->dev-bak"] is True


@patch("stashrun.snapshots_batch.copy_snapshot")
def test_batch_copy_overwrite_passed(mock_cp):
    mock_cp.return_value = True
    snapshots_batch.batch_copy([("dev", "dev2")], overwrite=True)
    mock_cp.assert_called_once_with("dev", "dev2", overwrite=True)


@patch("stashrun.snapshots_batch.get_snapshots_by_tag")
@patch("stashrun.snapshots_batch.remove_snapshot")
def test_batch_tag_delete(mock_rm, mock_tag):
    mock_tag.return_value = ["dev", "prod"]
    mock_rm.return_value = True
    results = snapshots_batch.batch_tag_delete("release")
    assert set(results.keys()) == {"dev", "prod"}


@patch("stashrun.snapshots_batch.list_all_snapshots")
def test_batch_export_names_no_filter(mock_list):
    mock_list.return_value = ["dev", "prod", "staging"]
    names = snapshots_batch.batch_export_names()
    assert names == ["dev", "prod", "staging"]


@patch("stashrun.snapshots_batch.list_all_snapshots")
def test_batch_export_names_with_pattern(mock_list):
    mock_list.return_value = ["dev", "prod", "dev-backup"]
    names = snapshots_batch.batch_export_names(pattern="dev")
    assert "dev" in names
    assert "dev-backup" in names
    assert "prod" not in names


@patch("stashrun.snapshots_batch.get_snapshot")
def test_batch_get_returns_envs(mock_get):
    mock_get.side_effect = lambda n: SNAPS.get(n)
    result = snapshots_batch.batch_get(["dev", "prod", "missing"])
    assert result["dev"] == {"A": "1"}
    assert result["missing"] is None
