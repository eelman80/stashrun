"""Tests for stashrun.snapshots_coherence."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_coherence import coherence_rank, coherence_summary, compute_coherence


def _patch_deps(
    env=None,
    bad_keys=None,
    empty_vals=None,
    checksum_ok=True,
    status="active",
    perms=None,
):
    if perms is None:
        perms = {"read": True, "write": True}
    return [
        patch("stashrun.snapshots_coherence.get_snapshot", return_value=env if env is not False else None),
        patch("stashrun.snapshots_coherence.validate_key_pattern", return_value=bad_keys or []),
        patch("stashrun.snapshots_coherence.validate_value_nonempty", return_value=empty_vals or []),
        patch("stashrun.snapshots_coherence.verify_checksum", return_value=checksum_ok),
        patch("stashrun.snapshots_coherence.get_status", return_value=status),
        patch("stashrun.snapshots_coherence.get_permissions", return_value=perms),
        patch("stashrun.snapshots_coherence.list_snapshots", return_value=["snap1", "snap2"]),
    ]


def test_compute_coherence_missing_returns_none():
    with patch("stashrun.snapshots_coherence.get_snapshot", return_value=None):
        assert compute_coherence("ghost") is None


def test_compute_coherence_perfect_score():
    patches = _patch_deps(env={"FOO": "bar"})
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 100
    assert result["issues"] == []


def test_compute_coherence_bad_keys_deducts_20():
    patches = _patch_deps(env={"foo": "bar"}, bad_keys=["foo"])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 80
    assert any("naming" in i for i in result["issues"])


def test_compute_coherence_empty_values_deducts_20():
    patches = _patch_deps(env={"FOO": ""}, empty_vals=["FOO"])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 80
    assert any("empty" in i for i in result["issues"])


def test_compute_coherence_checksum_mismatch_deducts_20():
    patches = _patch_deps(env={"FOO": "bar"}, checksum_ok=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 80
    assert any("checksum" in i for i in result["issues"])


def test_compute_coherence_deprecated_status_deducts_20():
    patches = _patch_deps(env={"FOO": "bar"}, status="deprecated")
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 80


def test_compute_coherence_no_read_permission_deducts_20():
    patches = _patch_deps(env={"FOO": "bar"}, perms={"read": False, "write": True})
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 80


def test_compute_coherence_multiple_issues_cumulative():
    patches = _patch_deps(
        env={"foo": ""},
        bad_keys=["foo"],
        empty_vals=["foo"],
        checksum_ok=False,
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_coherence("snap1")
    assert result["score"] == 40
    assert len(result["issues"]) == 3


def test_coherence_rank_sorted_desc():
    call_count = 0
    scores = [100, 60]

    def _fake_compute(name):
        nonlocal call_count
        s = scores[call_count % 2]
        call_count += 1
        return {"name": name, "score": s, "issues": []}

    with patch("stashrun.snapshots_coherence.list_snapshots", return_value=["a", "b"]), \
         patch("stashrun.snapshots_coherence.get_snapshot", side_effect=[{"X": "1"}, {"Y": "2"}]), \
         patch("stashrun.snapshots_coherence.validate_key_pattern", return_value=[]), \
         patch("stashrun.snapshots_coherence.validate_value_nonempty", return_value=[]), \
         patch("stashrun.snapshots_coherence.verify_checksum", return_value=True), \
         patch("stashrun.snapshots_coherence.get_status", return_value="active"), \
         patch("stashrun.snapshots_coherence.get_permissions", return_value={"read": True}):
        ranked = coherence_rank()
    assert ranked[0]["score"] >= ranked[-1]["score"]


def test_coherence_summary_empty():
    with patch("stashrun.snapshots_coherence.list_snapshots", return_value=[]):
        s = coherence_summary()
    assert s["count"] == 0
    assert s["average"] == 0.0
