"""Tests for stashrun.encryption and stashrun.encrypted_snapshot."""

import os
import pytest
from unittest.mock import patch

pytest.importorskip("cryptography", reason="cryptography package required")

from stashrun.encryption import generate_key, encrypt_env, decrypt_env, get_key, KEY_ENV_VAR
from stashrun.encrypted_snapshot import (
    save_snapshot_encrypted,
    load_snapshot_decrypted,
    is_snapshot_encrypted,
    _ENCRYPTED_MARKER,
)
from stashrun.storage import load_snapshot


@pytest.fixture
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_generate_key_returns_string():
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    env = {"FOO": "bar", "SECRET": "mysecret"}
    ciphertext = encrypt_env(env, key)
    assert isinstance(ciphertext, str)
    result = decrypt_env(ciphertext, key)
    assert result == env


def test_encrypt_produces_different_output_than_input():
    key = generate_key()
    env = {"API_KEY": "12345"}
    ciphertext = encrypt_env(env, key)
    assert "12345" not in ciphertext


def test_get_key_from_env(monkeypatch):
    monkeypatch.setenv(KEY_ENV_VAR, "testkey")
    assert get_key() == "testkey"


def test_get_key_missing_returns_none(monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)
    with patch("stashrun.encryption._key_file_path") as mock_path:
        mock_path.return_value.__class__ = type
        from pathlib import Path
        p = Path("/nonexistent/path/.stashrun_key")
        mock_path.return_value = p
        result = get_key()
    assert result is None


def test_save_snapshot_encrypted_stores_marker(isolated_stash_dir, monkeypatch):
    key = generate_key()
    monkeypatch.setenv(KEY_ENV_VAR, key)
    env = {"DB_PASS": "secret"}
    save_snapshot_encrypted("enc_test", env)
    raw = load_snapshot("enc_test")
    assert _ENCRYPTED_MARKER in raw


def test_save_snapshot_no_key_stores_plaintext(isolated_stash_dir, monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)
    with patch("stashrun.encrypted_snapshot.get_key", return_value=None):
        env = {"PLAIN": "value"}
        save_snapshot_encrypted("plain_test", env)
    raw = load_snapshot("plain_test")
    assert _ENCRYPTED_MARKER not in raw
    assert raw["PLAIN"] == "value"


def test_load_snapshot_decrypted_roundtrip(isolated_stash_dir, monkeypatch):
    key = generate_key()
    monkeypatch.setenv(KEY_ENV_VAR, key)
    env = {"TOKEN": "abc123", "HOST": "localhost"}
    save_snapshot_encrypted("rt_test", env)
    result = load_snapshot_decrypted("rt_test")
    assert result == env


def test_load_snapshot_decrypted_missing_returns_none(isolated_stash_dir):
    result = load_snapshot_decrypted("nonexistent")
    assert result is None


def test_is_snapshot_encrypted_true(isolated_stash_dir, monkeypatch):
    key = generate_key()
    monkeypatch.setenv(KEY_ENV_VAR, key)
    save_snapshot_encrypted("enc_check", {"X": "1"})
    assert is_snapshot_encrypted("enc_check") is True


def test_is_snapshot_encrypted_false(isolated_stash_dir, monkeypatch):
    monkeypatch.delenv(KEY_ENV_VAR, raising=False)
    with patch("stashrun.encrypted_snapshot.get_key", return_value=None):
        save_snapshot_encrypted("plain_check", {"Y": "2"})
    assert is_snapshot_encrypted("plain_check") is False
