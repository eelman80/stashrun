import hashlib
import json
from typing import Optional
from stashrun.storage import get_stash_dir

_CHECKSUM_FILE = "checksums.json"


def _checksum_path():
    return get_stash_dir() / _CHECKSUM_FILE


def _load_checksums() -> dict:
    p = _checksum_path()
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_checksums(data: dict) -> None:
    p = _checksum_path()
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def compute_checksum(env: dict) -> str:
    """Compute a stable SHA256 checksum for an env dict."""
    serialized = json.dumps(env, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def store_checksum(name: str, env: dict) -> str:
    """Compute and store the checksum for a snapshot."""
    checksum = compute_checksum(env)
    data = _load_checksums()
    data[name] = checksum
    _save_checksums(data)
    return checksum


def get_checksum(name: str) -> Optional[str]:
    """Return the stored checksum for a snapshot, or None."""
    return _load_checksums().get(name)


def remove_checksum(name: str) -> bool:
    data = _load_checksums()
    if name not in data:
        return False
    del data[name]
    _save_checksums(data)
    return True


def verify_checksum(name: str, env: dict) -> Optional[bool]:
    """Compare current env against stored checksum.
    Returns True if match, False if mismatch, None if no stored checksum."""
    stored = get_checksum(name)
    if stored is None:
        return None
    return compute_checksum(env) == stored


def list_checksums() -> dict:
    return dict(_load_checksums())
