"""Tests for stashrun.snapshots_readiness."""

import pytest
from unittest.mock import patch

MOD = "stashrun.snapshots_readiness"


def _patch_deps(
    snapshot=None,
    owner=None,
    status="unknown",
    lifecycle="unknown",
    stored_checksum=None,
    live_checksum="abc",
    perms=None,
    all_names=None,
):
    if perms is None:
        perms = {"read": True, "write": True, "delete": True}
    if all_names is None:
        all_names = []
    env = snapshot if snapshot is not None else {"KEY": "val"}
    return [
        patch(f"{MOD}.get_snapshot", return_value=env),
        patch(f"{MOD}.get_owner", return_value=owner),
        patch(f"{MOD}.get_status", return_value=status),
        patch(f"{MOD}.get_lifecycle", return_value=lifecycle),
        patch(f"{MOD}.get_checksum", return_value=stored_checksum),
        patch(f"{MOD}.compute_checksum", return_value=live_checksum),
        patch(f"{MOD}.get_permissions", return_value=perms),
        patch(f"{MOD}.list_all_snapshots", return_value=all_names),
    ]


def _apply(patches):
    for p in patches:
        p.start()
    return patches


def _stop(patches):
    for p in patches:
        p.stop()


def test_compute_readiness_missing_returns_none():
    with patch(f"{MOD}.get_snapshot", return_value=None):
        from stashrun.snapshots_readiness import compute_readiness
        assert compute_readiness("ghost") is None


def test_compute_readiness_all_zero():
    patches = _patch_deps(status="unknown", lifecycle="unknown", owner=None,
                          stored_checksum=None,
                          perms={"read": False, "write": True, "delete": True})
    _apply(patches)
    try:
        from stashrun import snapshots_readiness
        import importlib; importlib.reload(snapshots_readiness)
        result = snapshots_readiness.compute_readiness("snap1")
        assert result is not None
        assert result["score"] == 0
        assert result["has_owner"] is False
        assert result["checksum_valid"] is None
    finally:
        _stop(patches)


def test_compute_readiness_full_score():
    patches = _patch_deps(
        owner="alice",
        status="active",
        lifecycle="stable",
        stored_checksum="abc",
        live_checksum="abc",
        perms={"read": True, "write": True, "delete": True},
    )
    _apply(patches)
    try:
        from stashrun import snapshots_readiness
        import importlib; importlib.reload(snapshots_readiness)
        result = snapshots_readiness.compute_readiness("snap1")
        assert result["score"] == 100
        assert result["has_owner"] is True
        assert result["checksum_valid"] is True
        assert result["permissions_open"] is True
    finally:
        _stop(patches)


def test_compute_readiness_stale_checksum_partial_score():
    patches = _patch_deps(
        owner="bob",
        status="active",
        lifecycle="stable",
        stored_checksum="old",
        live_checksum="new",
    )
    _apply(patches)
    try:
        from stashrun import snapshots_readiness
        import importlib; importlib.reload(snapshots_readiness)
        result = snapshots_readiness.compute_readiness("snap1")
        # owner(20) + status(20) + lifecycle(20) + stale checksum(5) + perms(15) = 80
        assert result["score"] == 80
        assert result["checksum_valid"] is False
    finally:
        _stop(patches)


def test_readiness_rank_sorted_descending():
    from stashrun import snapshots_readiness
    import importlib; importlib.reload(snapshots_readiness)

    results = {"a": {"score": 40}, "b": {"score": 90}, "c": {"score": 60}}
    with patch(f"{MOD}.list_all_snapshots", return_value=["a", "b", "c"]), \
         patch(f"{MOD}.compute_readiness", side_effect=lambda n: results[n]):
        ranked = snapshots_readiness.readiness_rank()
    assert ranked[0] == ("b", 90)
    assert ranked[1] == ("c", 60)
    assert ranked[2] == ("a", 40)


def test_readiness_summary_statistics():
    from stashrun import snapshots_readiness
    import importlib; importlib.reload(snapshots_readiness)

    results = {"x": {"score": 50}, "y": {"score": 100}}
    with patch(f"{MOD}.list_all_snapshots", return_value=["x", "y"]), \
         patch(f"{MOD}.compute_readiness", side_effect=lambda n: results[n]):
        summary = snapshots_readiness.readiness_summary()
    assert summary["count"] == 2
    assert summary["average"] == 75.0
    assert summary["max"] == 100
    assert summary["min"] == 50


def test_readiness_summary_empty():
    from stashrun import snapshots_readiness
    import importlib; importlib.reload(snapshots_readiness)

    with patch(f"{MOD}.list_all_snapshots", return_value=[]), \
         patch(f"{MOD}.compute_readiness", return_value=None):
        summary = snapshots_readiness.readiness_summary()
    assert summary["count"] == 0
    assert summary["average"] == 0
