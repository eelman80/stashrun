import pytest
from unittest.mock import patch
from stashrun import snapshots_checksums as sc


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    import stashrun.storage as storage
    monkeypatch.setattr(storage, "_stash_dir_cache", None, raising=False)
    yield tmp_path


ENV_A = {"FOO": "bar", "BAZ": "qux"}
ENV_B = {"FOO": "bar", "BAZ": "changed"}


def test_compute_checksum_is_deterministic():
    assert sc.compute_checksum(ENV_A) == sc.compute_checksum(ENV_A)


def test_compute_checksum_differs_on_change():
    assert sc.compute_checksum(ENV_A) != sc.compute_checksum(ENV_B)


def test_compute_checksum_is_hex_string():
    result = sc.compute_checksum(ENV_A)
    assert isinstance(result, str)
    assert len(result) == 64


def test_store_and_get_checksum():
    checksum = sc.store_checksum("snap1", ENV_A)
    assert sc.get_checksum("snap1") == checksum


def test_get_checksum_missing_returns_none():
    assert sc.get_checksum("nonexistent") is None


def test_remove_checksum_existing():
    sc.store_checksum("snap1", ENV_A)
    assert sc.remove_checksum("snap1") is True
    assert sc.get_checksum("snap1") is None


def test_remove_checksum_missing_returns_false():
    assert sc.remove_checksum("ghost") is False


def test_verify_checksum_match():
    sc.store_checksum("snap1", ENV_A)
    assert sc.verify_checksum("snap1", ENV_A) is True


def test_verify_checksum_mismatch():
    sc.store_checksum("snap1", ENV_A)
    assert sc.verify_checksum("snap1", ENV_B) is False


def test_verify_checksum_no_stored_returns_none():
    assert sc.verify_checksum("missing", ENV_A) is None


def test_list_checksums_empty():
    assert sc.list_checksums() == {}


def test_list_checksums_multiple():
    sc.store_checksum("a", ENV_A)
    sc.store_checksum("b", ENV_B)
    result = sc.list_checksums()
    assert set(result.keys()) == {"a", "b"}
