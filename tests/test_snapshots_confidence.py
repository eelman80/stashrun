import pytest
from unittest.mock import patch

from stashrun.snapshots_confidence import compute_confidence, confidence_rank

ENV = {"KEY": "value", "OTHER": "data"}


def _patch_deps(env=ENV, checksum="abc", verify=True, rating=4, issues=None):
    return [
        patch("stashrun.snapshots_confidence.get_snapshot", return_value=env),
        patch("stashrun.snapshots_confidence.get_checksum", return_value=checksum),
        patch("stashrun.snapshots_confidence.verify_checksum", return_value=verify),
        patch("stashrun.snapshots_confidence.get_rating", return_value=rating),
        patch("stashrun.snapshots_confidence.validate_snapshot", return_value=issues or []),
    ]


def test_compute_confidence_missing_returns_none():
    with patch("stashrun.snapshots_confidence.get_snapshot", return_value=None):
        assert compute_confidence("ghost") is None


def test_compute_confidence_full_score():
    patches = _patch_deps()
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        info = compute_confidence("snap1")
    assert info is not None
    assert info["checksum_exists"] is True
    assert info["checksum_valid"] is True
    assert info["has_keys"] is True
    assert info["no_empty_values"] is True
    assert info["percent"] > 0


def test_compute_confidence_no_checksum():
    patches = _patch_deps(checksum=None, verify=False)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        info = compute_confidence("snap2")
    assert info["checksum_exists"] is False
    assert info["checksum_valid"] is False


def test_compute_confidence_no_rating():
    patches = _patch_deps(rating=None)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        info = compute_confidence("snap3")
    assert info["rating"] is None


def test_compute_confidence_empty_env():
    patches = _patch_deps(env={})
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        info = compute_confidence("snap4")
    assert info["has_keys"] is False


def test_compute_confidence_with_empty_values():
    issues = [{"check": "nonempty", "key": "KEY"}]
    patches = _patch_deps(issues=issues)
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        info = compute_confidence("snap5")
    assert info["no_empty_values"] is False


def test_confidence_rank_sorts_descending():
    results = {"a": 80.0, "b": 50.0, "c": 95.0}

    def fake_confidence(name):
        return {"percent": results[name], "score": 1, "max_score": 1}

    with patch("stashrun.snapshots_confidence.compute_confidence", side_effect=fake_confidence):
        ranked = confidence_rank(["a", "b", "c"])
    assert ranked[0][0] == "c"
    assert ranked[1][0] == "a"
    assert ranked[2][0] == "b"


def test_confidence_rank_skips_missing():
    def fake_confidence(name):
        return None if name == "missing" else {"percent": 70.0, "score": 1, "max_score": 1}

    with patch("stashrun.snapshots_confidence.compute_confidence", side_effect=fake_confidence):
        ranked = confidence_rank(["missing", "real"])
    assert len(ranked) == 1
    assert ranked[0][0] == "real"
