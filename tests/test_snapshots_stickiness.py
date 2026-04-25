"""Tests for stashrun.snapshots_stickiness."""

from unittest.mock import patch, MagicMock
import pytest

from stashrun.snapshots_stickiness import (
    compute_stickiness,
    stickiness_rank,
    stickiness_summary,
)


def _patch_deps(
    snapshot=None,
    access_count=0,
    is_fav=False,
    is_pin=False,
    bookmarks=None,
    history=None,
):
    """Return a context manager stack that patches all external dependencies."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        with (
            patch("stashrun.snapshots_stickiness.get_snapshot", return_value=snapshot),
            patch("stashrun.snapshots_stickiness.get_access_count", return_value=access_count),
            patch("stashrun.snapshots_stickiness.is_favorite", return_value=is_fav),
            patch("stashrun.snapshots_stickiness.is_pinned", return_value=is_pin),
            patch(
                "stashrun.snapshots_stickiness._load_bookmarks",
                return_value=bookmarks or {},
            ),
            patch("stashrun.snapshots_stickiness.get_history", return_value=history or []),
        ):
            yield

    return _ctx()


def test_compute_stickiness_missing_returns_none():
    with _patch_deps(snapshot=None):
        assert compute_stickiness("ghost") is None


def test_compute_stickiness_all_zero():
    with _patch_deps(snapshot={"X": "1"}):
        result = compute_stickiness("snap")
    assert result is not None
    assert result["total"] == 0
    assert result["name"] == "snap"


def test_compute_stickiness_access_score_capped():
    with _patch_deps(snapshot={"X": "1"}, access_count=100):
        result = compute_stickiness("snap")
    assert result["access_score"] == 40  # capped at 20 accesses * 2


def test_compute_stickiness_favorite_adds_score():
    with _patch_deps(snapshot={"X": "1"}, is_fav=True):
        result = compute_stickiness("snap")
    assert result["favorite_score"] == 15


def test_compute_stickiness_pinned_adds_score():
    with _patch_deps(snapshot={"X": "1"}, is_pin=True):
        result = compute_stickiness("snap")
    assert result["pinned_score"] == 15


def test_compute_stickiness_bookmark_adds_score():
    bm = {"alias": "snap"}
    with _patch_deps(snapshot={"X": "1"}, bookmarks=bm):
        result = compute_stickiness("snap")
    assert result["bookmark_score"] == 10


def test_compute_stickiness_restore_events_capped():
    history = [{"event": "restore"}] * 50
    with _patch_deps(snapshot={"X": "1"}, history=history):
        result = compute_stickiness("snap")
    assert result["restore_score"] == 20  # capped at 10 restores * 2


def test_compute_stickiness_full_score():
    history = [{"event": "restore"}] * 10
    bm = {"a": "snap"}
    with _patch_deps(
        snapshot={"X": "1"},
        access_count=20,
        is_fav=True,
        is_pin=True,
        bookmarks=bm,
        history=history,
    ):
        result = compute_stickiness("snap")
    assert result["total"] == 100


def test_stickiness_rank_sorted_descending():
    def _fake_list():
        return ["a", "b", "c"]

    scores = {"a": 10, "b": 50, "c": 30}

    def _fake_compute(name):
        return {"name": name, "total": scores[name]}

    with (
        patch("stashrun.snapshots_stickiness.list_snapshots", side_effect=_fake_list),
        patch("stashrun.snapshots_stickiness.compute_stickiness", side_effect=_fake_compute),
    ):
        ranked = stickiness_rank()

    assert [r["name"] for r in ranked] == ["b", "c", "a"]


def test_stickiness_summary_empty():
    with patch("stashrun.snapshots_stickiness.stickiness_rank", return_value=[]):
        summary = stickiness_summary()
    assert summary["count"] == 0
    assert summary["average"] == 0.0


def test_stickiness_summary_values():
    ranked = [
        {"name": "a", "total": 80},
        {"name": "b", "total": 40},
        {"name": "c", "total": 60},
    ]
    with patch("stashrun.snapshots_stickiness.stickiness_rank", return_value=ranked):
        summary = stickiness_summary()
    assert summary["count"] == 3
    assert summary["max"] == 80
    assert summary["min"] == 40
    assert summary["average"] == 60.0
