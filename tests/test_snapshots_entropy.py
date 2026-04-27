"""Tests for stashrun.snapshots_entropy."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from stashrun.snapshots_entropy import (
    _char_entropy,
    compute_entropy,
    entropy_rank,
    entropy_summary,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_FAKE_SNAPSHOTS = {
    "alpha": {"KEY": "aaaa", "TOKEN": "aB3$xZ9!qW2"},
    "beta": {"PATH": "/usr/bin", "HOME": "/home/user"},
    "empty": {},
}


def _fake_get(name):
    return _FAKE_SNAPSHOTS.get(name)


def _fake_list():
    return list(_FAKE_SNAPSHOTS.keys())


@pytest.fixture(autouse=True)
def mock_deps():
    with patch("stashrun.snapshots_entropy.get_snapshot", side_effect=_fake_get), \
         patch("stashrun.snapshots_entropy.list_snapshots", side_effect=_fake_list):
        yield


# ---------------------------------------------------------------------------
# _char_entropy
# ---------------------------------------------------------------------------

def test_char_entropy_empty_string():
    assert _char_entropy("") == 0.0


def test_char_entropy_single_char():
    assert _char_entropy("aaaa") == 0.0


def test_char_entropy_two_chars():
    result = _char_entropy("abab")
    assert result == pytest.approx(1.0, abs=1e-6)


def test_char_entropy_high_randomness():
    # Long string with many unique chars should have higher entropy
    result = _char_entropy("aB3$xZ9!qW2mN7@kP")
    assert result > 3.5


# ---------------------------------------------------------------------------
# compute_entropy
# ---------------------------------------------------------------------------

def test_compute_entropy_missing_returns_none():
    assert compute_entropy("nonexistent") is None


def test_compute_entropy_empty_snapshot():
    report = compute_entropy("empty")
    assert report is not None
    assert report["score"] == 0
    assert report["high_entropy_keys"] == []


def test_compute_entropy_returns_dict():
    report = compute_entropy("alpha")
    assert isinstance(report, dict)
    assert "mean_entropy" in report
    assert "max_entropy" in report
    assert "score" in report
    assert "high_entropy_keys" in report


def test_compute_entropy_score_range():
    for name in ["alpha", "beta"]:
        report = compute_entropy(name)
        assert 0 <= report["score"] <= 100


def test_compute_entropy_high_entropy_key_detected():
    # TOKEN value is random-looking; should appear in high_entropy_keys
    report = compute_entropy("alpha")
    assert "TOKEN" in report["high_entropy_keys"]


def test_compute_entropy_low_entropy_key_excluded():
    report = compute_entropy("alpha")
    # KEY = "aaaa" has zero entropy — must NOT be in high_entropy_keys
    assert "KEY" not in report["high_entropy_keys"]


# ---------------------------------------------------------------------------
# entropy_rank
# ---------------------------------------------------------------------------

def test_entropy_rank_returns_list_of_tuples():
    ranked = entropy_rank()
    assert isinstance(ranked, list)
    for item in ranked:
        assert len(item) == 2


def test_entropy_rank_descending_order():
    ranked = entropy_rank()
    scores = [s for _, s in ranked]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# entropy_summary
# ---------------------------------------------------------------------------

def test_entropy_summary_keys():
    summary = entropy_summary()
    assert "total" in summary
    assert "average_score" in summary
    assert "top" in summary


def test_entropy_summary_total():
    summary = entropy_summary()
    assert summary["total"] == len(_FAKE_SNAPSHOTS)
