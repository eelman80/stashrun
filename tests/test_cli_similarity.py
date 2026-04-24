"""Tests for cli_similarity commands."""

import pytest
from unittest.mock import patch
from types import SimpleNamespace

from stashrun.cli_similarity import cmd_similarity_compare, cmd_similarity_find, cmd_similarity_matrix


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


SAMPLE = {
    "snapshot_a": "snap_a",
    "snapshot_b": "snap_b",
    "shared_keys": ["HOST", "DEBUG"],
    "key_overlap": 0.6667,
    "value_overlap": 1.0,
    "score": 83.34,
}


def test_cmd_similarity_compare_success(capsys):
    with patch("stashrun.cli_similarity.compute_similarity", return_value=SAMPLE):
        cmd_similarity_compare(_ns(name_a="snap_a", name_b="snap_b"))
    out = capsys.readouterr().out
    assert "83.34%" in out
    assert "HOST" in out


def test_cmd_similarity_compare_missing(capsys):
    with patch("stashrun.cli_similarity.compute_similarity", return_value=None):
        cmd_similarity_compare(_ns(name_a="snap_a", name_b="missing"))
    out = capsys.readouterr().out
    assert "error" in out


def test_cmd_similarity_find_results(capsys):
    results = [SAMPLE]
    with patch("stashrun.cli_similarity.find_similar", return_value=results):
        cmd_similarity_find(_ns(name="snap_a", threshold=50.0))
    out = capsys.readouterr().out
    assert "snap_b" in out
    assert "83.34%" in out


def test_cmd_similarity_find_empty(capsys):
    with patch("stashrun.cli_similarity.find_similar", return_value=[]):
        cmd_similarity_find(_ns(name="snap_a", threshold=50.0))
    out = capsys.readouterr().out
    assert "No snapshots" in out


def test_cmd_similarity_matrix_success(capsys):
    pairs = [SAMPLE, {**SAMPLE, "snapshot_a": "snap_a", "snapshot_b": "snap_c", "score": 10.0}]
    with patch("stashrun.cli_similarity.similarity_matrix", return_value=pairs):
        cmd_similarity_matrix(_ns(names=["snap_a", "snap_b", "snap_c"]))
    out = capsys.readouterr().out
    assert "snap_b" in out
    assert "83.34%" in out


def test_cmd_similarity_matrix_too_few_names(capsys):
    cmd_similarity_matrix(_ns(names=["snap_a"]))
    out = capsys.readouterr().out
    assert "error" in out


def test_cmd_similarity_matrix_no_pairs(capsys):
    with patch("stashrun.cli_similarity.similarity_matrix", return_value=[]):
        cmd_similarity_matrix(_ns(names=["snap_a", "snap_b"]))
    out = capsys.readouterr().out
    assert "No valid pairs" in out
