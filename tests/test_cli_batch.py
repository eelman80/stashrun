"""Tests for cli_batch commands."""

import pytest
import argparse
from unittest.mock import patch
from stashrun import cli_batch


def _ns(**kwargs):
    base = {"names": [], "pairs": [], "overwrite": False, "tag": "", "pattern": None}
    base.update(kwargs)
    return argparse.Namespace(**base)


@patch("stashrun.cli_batch.batch_delete")
def test_cmd_batch_delete_success(mock_del, capsys):
    mock_del.return_value = {"dev": True, "old": False}
    cli_batch.cmd_batch_delete(_ns(names=["dev", "old"]))
    out = capsys.readouterr().out
    assert "deleted" in out
    assert "not found" in out


@patch("stashrun.cli_batch.batch_copy")
def test_cmd_batch_copy_success(mock_cp, capsys):
    mock_cp.return_value = {"dev->dev-bak": True}
    cli_batch.cmd_batch_copy(_ns(pairs=["dev", "dev-bak"], overwrite=False))
    out = capsys.readouterr().out
    assert "copied" in out


def test_cmd_batch_copy_odd_pairs(capsys):
    cli_batch.cmd_batch_copy(_ns(pairs=["dev"], overwrite=False))
    out = capsys.readouterr().out
    assert "Error" in out


@patch("stashrun.cli_batch.batch_tag_delete")
def test_cmd_batch_tag_delete_found(mock_tdel, capsys):
    mock_tdel.return_value = {"dev": True}
    cli_batch.cmd_batch_tag_delete(_ns(tag="release"))
    out = capsys.readouterr().out
    assert "deleted" in out


@patch("stashrun.cli_batch.batch_tag_delete")
def test_cmd_batch_tag_delete_none(mock_tdel, capsys):
    mock_tdel.return_value = {}
    cli_batch.cmd_batch_tag_delete(_ns(tag="ghost"))
    out = capsys.readouterr().out
    assert "No snapshots" in out


@patch("stashrun.cli_batch.batch_export_names")
def test_cmd_batch_list_results(mock_names, capsys):
    mock_names.return_value = ["dev", "prod"]
    cli_batch.cmd_batch_list(_ns(pattern=None))
    out = capsys.readouterr().out
    assert "dev" in out
    assert "prod" in out


@patch("stashrun.cli_batch.batch_export_names")
def test_cmd_batch_list_empty(mock_names, capsys):
    mock_names.return_value = []
    cli_batch.cmd_batch_list(_ns(pattern=None))
    out = capsys.readouterr().out
    assert "No snapshots" in out
