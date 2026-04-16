import pytest
from unittest.mock import patch
from stashrun.snapshots_validate import (
    validate_required_keys,
    validate_key_pattern,
    validate_value_nonempty,
    validate_value_pattern,
    validate_snapshot,
)

SAMPLE_ENV = {"APP_HOST": "localhost", "APP_PORT": "8080", "DEBUG": ""}


def test_validate_required_keys_all_present():
    assert validate_required_keys(SAMPLE_ENV, ["APP_HOST", "APP_PORT"]) == []


def test_validate_required_keys_missing():
    missing = validate_required_keys(SAMPLE_ENV, ["APP_HOST", "DB_URL"])
    assert missing == ["DB_URL"]


def test_validate_key_pattern_all_match():
    env = {"APP_HOST": "x", "APP_PORT": "y"}
    result = validate_key_pattern(env, r"APP_[A-Z]+")
    assert all(result.values())


def test_validate_key_pattern_some_fail():
    result = validate_key_pattern(SAMPLE_ENV, r"APP_[A-Z]+")
    assert result["APP_HOST"] is True
    assert result["DEBUG"] is False


def test_validate_value_nonempty_finds_empty():
    assert validate_value_nonempty(SAMPLE_ENV) == ["DEBUG"]


def test_validate_value_nonempty_all_filled():
    assert validate_value_nonempty({"A": "1", "B": "2"}) == []


def test_validate_value_pattern_match():
    assert validate_value_pattern(SAMPLE_ENV, "APP_PORT", r"\d+") is True


def test_validate_value_pattern_no_match():
    assert validate_value_pattern(SAMPLE_ENV, "APP_HOST", r"\d+") is False


def test_validate_value_pattern_missing_key():
    assert validate_value_pattern(SAMPLE_ENV, "MISSING", r".*") is None


def _mock_get(name):
    return SAMPLE_ENV if name == "mysnap" else None


@patch("stashrun.snapshots_validate.get_snapshot", side_effect=_mock_get)
def test_validate_snapshot_missing(mock_get):
    report = validate_snapshot("nope")
    assert report == {"found": False}


@patch("stashrun.snapshots_validate.get_snapshot", side_effect=_mock_get)
def test_validate_snapshot_valid(mock_get):
    report = validate_snapshot("mysnap", required_keys=["APP_HOST"])
    assert report["found"] is True
    assert report["missing_keys"] == []
    assert report["valid"] is True


@patch("stashrun.snapshots_validate.get_snapshot", side_effect=_mock_get)
def test_validate_snapshot_missing_key(mock_get):
    report = validate_snapshot("mysnap", required_keys=["DB_URL"])
    assert "DB_URL" in report["missing_keys"]
    assert report["valid"] is False


@patch("stashrun.snapshots_validate.get_snapshot", side_effect=_mock_get)
def test_validate_snapshot_empty_values(mock_get):
    report = validate_snapshot("mysnap", no_empty_values=True)
    assert "DEBUG" in report["empty_values"]
    assert report["valid"] is False


@patch("stashrun.snapshots_validate.get_snapshot", side_effect=_mock_get)
def test_validate_snapshot_key_pattern(mock_get):
    report = validate_snapshot("mysnap", key_pattern=r"APP_[A-Z]+")
    assert "DEBUG" in report["invalid_keys"]
    assert report["valid"] is False
