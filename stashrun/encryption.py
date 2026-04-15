"""Optional encryption support for snapshots using Fernet symmetric encryption."""

import os
import base64
import json
from pathlib import Path
from typing import Optional

KEY_ENV_VAR = "STASHRUN_ENCRYPTION_KEY"
_KEY_FILE_NAME = ".stashrun_key"


def _key_file_path() -> Path:
    return Path.home() / _KEY_FILE_NAME


def generate_key() -> str:
    """Generate a new Fernet-compatible base64 key and return it as a string."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise RuntimeError("cryptography package is required for encryption support.")
    return Fernet.generate_key().decode()


def get_key() -> Optional[str]:
    """Retrieve encryption key from env var or key file."""
    key = os.environ.get(KEY_ENV_VAR)
    if key:
        return key
    path = _key_file_path()
    if path.exists():
        return path.read_text().strip()
    return None


def save_key_to_file(key: str) -> Path:
    """Persist key to the default key file."""
    path = _key_file_path()
    path.write_text(key)
    path.chmod(0o600)
    return path


def encrypt_env(env: dict, key: str) -> str:
    """Encrypt an env dict to a base64-encoded ciphertext string."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise RuntimeError("cryptography package is required for encryption support.")
    f = Fernet(key.encode() if isinstance(key, str) else key)
    plaintext = json.dumps(env).encode()
    return f.encrypt(plaintext).decode()


def decrypt_env(ciphertext: str, key: str) -> dict:
    """Decrypt a ciphertext string back to an env dict."""
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise RuntimeError("cryptography package is required for encryption support.")
    f = Fernet(key.encode() if isinstance(key, str) else key)
    plaintext = f.decrypt(ciphertext.encode() if isinstance(ciphertext, str) else ciphertext)
    return json.loads(plaintext.decode())
