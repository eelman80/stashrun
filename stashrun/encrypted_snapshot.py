"""Snapshot operations with transparent encryption/decryption support."""

from typing import Optional
from stashrun.encryption import get_key, encrypt_env, decrypt_env
from stashrun.storage import save_snapshot, load_snapshot
from stashrun.env import capture_env

_ENCRYPTED_MARKER = "__encrypted__"


def save_snapshot_encrypted(name: str, env: dict) -> bool:
    """Save a snapshot, encrypting it if a key is available."""
    key = get_key()
    if key:
        ciphertext = encrypt_env(env, key)
        payload = {_ENCRYPTED_MARKER: ciphertext}
    else:
        payload = env
    return save_snapshot(name, payload)


def load_snapshot_decrypted(name: str) -> Optional[dict]:
    """Load a snapshot, decrypting it if it was stored encrypted."""
    payload = load_snapshot(name)
    if payload is None:
        return None
    if _ENCRYPTED_MARKER in payload:
        key = get_key()
        if not key:
            raise RuntimeError(
                "Snapshot is encrypted but no encryption key is configured. "
                f"Set the {__import__('stashrun.encryption', fromlist=['KEY_ENV_VAR']).KEY_ENV_VAR} environment variable."
            )
        return decrypt_env(payload[_ENCRYPTED_MARKER], key)
    return payload


def is_snapshot_encrypted(name: str) -> bool:
    """Return True if the named snapshot is stored in encrypted form."""
    payload = load_snapshot(name)
    if payload is None:
        return False
    return _ENCRYPTED_MARKER in payload
