import pytest
from unittest.mock import patch

from stashrun.snapshots_sharing import (
    encode_snapshot,
    decode_share_string,
    import_share_string,
    share_summary,
)

SAMPLE_ENV = {"FOO": "bar", "BAZ": "qux"}


@pytest.fixture
def mock_get():
    with patch("stashrun.snapshots_sharing.get_snapshot") as m:
        yield m


@pytest.fixture
def mock_create():
    with patch("stashrun.snapshots_sharing.create_snapshot") as m:
        yield m


def test_encode_snapshot_returns_string(mock_get):
    mock_get.return_value = SAMPLE_ENV
    result = encode_snapshot("mysnap")
    assert isinstance(result, str)
    assert len(result) > 0


def test_encode_snapshot_missing_returns_none(mock_get):
    mock_get.return_value = None
    assert encode_snapshot("ghost") is None


def test_decode_roundtrip(mock_get):
    mock_get.return_value = SAMPLE_ENV
    encoded = encode_snapshot("mysnap")
    data = decode_share_string(encoded)
    assert data is not None
    assert data["name"] == "mysnap"
    assert data["env"] == SAMPLE_ENV


def test_decode_invalid_returns_none():
    assert decode_share_string("not-valid-base64!!!") is None


def test_decode_missing_fields_returns_none():
    import base64, json
    bad = base64.urlsafe_b64encode(json.dumps({"x": 1}).encode()).decode()
    assert decode_share_string(bad) is None


def test_import_share_string_success(mock_get, mock_create):
    mock_get.return_value = SAMPLE_ENV
    encoded = encode_snapshot("mysnap")
    result = import_share_string(encoded)
    assert result == "mysnap"
    mock_create.assert_called_once_with("mysnap", env=SAMPLE_ENV)


def test_import_share_string_custom_name(mock_get, mock_create):
    mock_get.return_value = SAMPLE_ENV
    encoded = encode_snapshot("mysnap")
    result = import_share_string(encoded, name="newname")
    assert result == "newname"
    mock_create.assert_called_once_with("newname", env=SAMPLE_ENV)


def test_import_share_string_invalid_returns_none(mock_create):
    result = import_share_string("garbage")
    assert result is None
    mock_create.assert_not_called()


def test_share_summary(mock_get):
    mock_get.return_value = SAMPLE_ENV
    encoded = encode_snapshot("mysnap")
    summary = share_summary(encoded)
    assert summary == {"name": "mysnap", "key_count": 2}


def test_share_summary_invalid_returns_none():
    assert share_summary("bad") is None
