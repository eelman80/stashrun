"""Tests for stashrun.snapshots_lint."""

import pytest
from unittest.mock import patch
from stashrun.snapshots_lint import (
    lint_snapshot,
    lint_no_empty_values,
    lint_no_whitespace_keys,
    lint_no_lowercase_keys,
    lint_no_very_long_values,
)


def _fake_get(name):
    snapshots = {
        "clean": {"DB_HOST": "localhost", "API_KEY": "abc123"},
        "dirty": {
            "db_host": "localhost",
            "BAD KEY": "value",
            "EMPTY": "",
            "LONG": "x" * 2000,
        },
    }
    return snapshots.get(name)


@pytest.fixture(autouse=True)
def mock_get_snapshot():
    with patch("stashrun.snapshots_lint.get_snapshot", side_effect=_fake_get):
        yield


def test_lint_missing_snapshot():
    result = lint_snapshot("nonexistent")
    assert result["missing"] is True
    assert result["passed"] is False


def test_lint_clean_snapshot_passes():
    result = lint_snapshot("clean")
    assert result["missing"] is False
    assert result["passed"] is True
    assert result["warnings"] == []


def test_lint_dirty_snapshot_fails():
    result = lint_snapshot("dirty")
    assert result["passed"] is False
    assert len(result["warnings"]) > 0


def test_lint_no_empty_values_detects():
    warnings = lint_no_empty_values({"A": "", "B": "ok"})
    assert len(warnings) == 1
    assert "A" in warnings[0]


def test_lint_no_empty_values_clean():
    assert lint_no_empty_values({"A": "val"}) == []


def test_lint_no_whitespace_keys_detects():
    warnings = lint_no_whitespace_keys({"BAD KEY": "v", "GOOD": "v"})
    assert len(warnings) == 1
    assert "BAD KEY" in warnings[0]


def test_lint_no_lowercase_keys_detects():
    warnings = lint_no_lowercase_keys({"db_host": "v", "DB_HOST": "v"})
    assert any("db_host" in w for w in warnings)
    assert not any("DB_HOST" in w for w in warnings)


def test_lint_no_very_long_values_detects():
    warnings = lint_no_very_long_values({"BIG": "x" * 2000, "SMALL": "ok"})
    assert len(warnings) == 1
    assert "BIG" in warnings[0]


def test_lint_custom_rules_subset():
    result = lint_snapshot("dirty", rules=["no_empty_values"])
    assert any("EMPTY" in w for w in result["warnings"])
    assert not any("uppercase" in w.lower() for w in result["warnings"])
