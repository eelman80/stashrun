"""Tests for stashrun.snapshots_engagement."""

import pytest
from unittest.mock import patch

from stashrun.snapshots_engagement import (
    compute_engagement,
    engagement_rank,
    engagement_summary,
)


def _patch_deps(
    snapshot=True,
    reactions=None,
    comment=None,
    mentions=None,
    subscribers=None,
    endorsements=None,
    all_snapshots=None,
):
    return [
        patch("stashrun.snapshots_engagement.get_snapshot", return_value={"K": "V"} if snapshot else None),
        patch("stashrun.snapshots_engagement.get_reactions", return_value=reactions or []),
        patch("stashrun.snapshots_engagement.get_comment", return_value=comment),
        patch("stashrun.snapshots_engagement.get_mentions", return_value=mentions or []),
        patch("stashrun.snapshots_engagement.get_subscribers", return_value=subscribers or []),
        patch("stashrun.snapshots_engagement.get_endorsements", return_value=endorsements or []),
        patch("stashrun.snapshots_engagement.list_snapshots", return_value=all_snapshots or []),
    ]


def test_compute_engagement_missing_returns_none():
    with patch("stashrun.snapshots_engagement.get_snapshot", return_value=None):
        assert compute_engagement("ghost") is None


def test_compute_engagement_all_zero():
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_engagement("snap")
    assert result["total"] == 0
    assert result["reaction_score"] == 0
    assert result["comment_score"] == 0


def test_compute_engagement_comment_adds_score():
    patches = _patch_deps(comment="some note")
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_engagement("snap")
    assert result["comment_score"] == 10


def test_compute_engagement_reactions_capped_at_30():
    patches = _patch_deps(reactions=["👍"] * 20)
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_engagement("snap")
    assert result["reaction_score"] == 30


def test_compute_engagement_endorsements_score():
    patches = _patch_deps(endorsements=["alice", "bob"])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_engagement("snap")
    assert result["endorsement_score"] == 16


def test_compute_engagement_full_score():
    patches = _patch_deps(
        reactions=["👍"] * 10,
        comment="note",
        mentions=["a", "b", "c", "d", "e"],
        subscribers=["u1", "u2", "u3", "u4", "u5", "u6", "u7", "u8"],
        endorsements=["e1", "e2", "e3", "e4", "e5"],
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
        result = compute_engagement("snap")
    assert result["total"] == 30 + 10 + 20 + 24 + 40


def test_engagement_rank_sorted():
    def fake_get(name):
        return {"K": "V"}

    def fake_list():
        return ["a", "b", "c"]

    def fake_reactions(name):
        return ["👍"] * {"a": 2, "b": 6, "c": 0}[name]

    with patch("stashrun.snapshots_engagement.get_snapshot", side_effect=fake_get), \
         patch("stashrun.snapshots_engagement.get_reactions", side_effect=fake_reactions), \
         patch("stashrun.snapshots_engagement.get_comment", return_value=None), \
         patch("stashrun.snapshots_engagement.get_mentions", return_value=[]), \
         patch("stashrun.snapshots_engagement.get_subscribers", return_value=[]), \
         patch("stashrun.snapshots_engagement.get_endorsements", return_value=[]), \
         patch("stashrun.snapshots_engagement.list_snapshots", side_effect=fake_list):
        ranked = engagement_rank()

    names = [n for n, _ in ranked]
    assert names[0] == "b"
    assert names[-1] == "c"


def test_engagement_summary_empty():
    with patch("stashrun.snapshots_engagement.list_snapshots", return_value=[]):
        summary = engagement_summary()
    assert summary["count"] == 0
    assert summary["top"] is None
