"""Tests for stashrun.snapshots_resilience."""

import pytest
from unittest.mock import patch

MOD = "stashrun.snapshots_resilience"


def _patch_deps(
    snapshot=None,
    encrypted=False,
    checksum=None,
    checksum_valid=True,
    pinned=False,
    versions=None,
    retention=None,
):
    snapshots = ["snap1"] if snapshot is not None else []
    return [
        patch(f"{MOD}.get_snapshot", return_value=snapshot),
        patch(f"{MOD}.list_all_snapshots", return_value=snapshots),
        patch(f"{MOD}.is_snapshot_encrypted", return_value=encrypted),
        patch(f"{MOD}.get_checksum", return_value=checksum),
        patch(f"{MOD}.verify_checksum", return_value=checksum_valid),
        patch(f"{MOD}.is_pinned", return_value=pinned),
        patch(f"{MOD}.list_versions", return_value=versions or []),
        patch(f"{MOD}.get_retention", return_value=retention),
    ]


def test_compute_resilience_missing_returns_none():
    with patch(f"{MOD}.get_snapshot", return_value=None):
        from stashrun.snapshots_resilience import compute_resilience
        assert compute_resilience("ghost") is None


def test_compute_resilience_all_zero():
    patches = _patch_deps(snapshot={"K": "V"})
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result is not None
    assert result["score"] == 0
    assert result["details"]["encrypted"] is False
    assert result["details"]["checksum"] == "missing"
    assert result["details"]["pinned"] is False
    assert result["details"]["versions"] == 0
    assert result["details"]["retention_policy"] is None


def test_compute_resilience_encrypted_adds_25():
    patches = _patch_deps(snapshot={"K": "V"}, encrypted=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["score"] >= 25
    assert result["details"]["encrypted"] is True


def test_compute_resilience_valid_checksum_adds_20():
    patches = _patch_deps(snapshot={"K": "V"}, checksum="abc", checksum_valid=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["details"]["checksum"] == "valid"
    assert result["score"] >= 20


def test_compute_resilience_invalid_checksum_adds_5():
    patches = _patch_deps(snapshot={"K": "V"}, checksum="abc", checksum_valid=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["details"]["checksum"] == "invalid"
    assert result["score"] == 5


def test_compute_resilience_pinned_adds_15():
    patches = _patch_deps(snapshot={"K": "V"}, pinned=True)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["details"]["pinned"] is True
    assert result["score"] >= 15


def test_compute_resilience_retention_adds_20():
    patches = _patch_deps(snapshot={"K": "V"}, retention={"policy": "keep-last-5"})
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["details"]["retention_policy"] == "keep-last-5"
    assert result["score"] >= 20


def test_compute_resilience_score_capped_at_100():
    patches = _patch_deps(
        snapshot={"K": "V"},
        encrypted=True,
        checksum="abc",
        checksum_valid=True,
        pinned=True,
        versions=[1, 2, 3, 4, 5],
        retention={"policy": "keep-all"},
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7]:
        from stashrun.snapshots_resilience import compute_resilience
        result = compute_resilience("snap1")
    assert result["score"] <= 100


def test_resilience_summary_empty():
    with patch(f"{MOD}.list_all_snapshots", return_value=[]):
        from stashrun.snapshots_resilience import resilience_summary
        s = resilience_summary()
    assert s["count"] == 0
    assert s["average"] == 0
