"""Per-snapshot permission flags (read, write, delete, share)."""

import json
from pathlib import Path
from stashrun.storage import get_stash_dir

VALID_PERMISSIONS = {"read", "write", "delete", "share"}


def _permissions_path() -> Path:
    return get_stash_dir() / "permissions.json"


def _load_permissions() -> dict:
    p = _permissions_path()
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_permissions(data: dict) -> None:
    _permissions_path().write_text(json.dumps(data, indent=2))


def set_permission(name: str, permission: str, allowed: bool) -> bool:
    """Set a specific permission flag for a snapshot. Returns False if invalid."""
    if permission not in VALID_PERMISSIONS:
        return False
    data = _load_permissions()
    if name not in data:
        data[name] = {}
    data[name][permission] = allowed
    _save_permissions(data)
    return True


def get_permissions(name: str) -> dict:
    """Return permission dict for snapshot, defaulting all to True."""
    data = _load_permissions()
    perms = data.get(name, {})
    return {p: perms.get(p, True) for p in VALID_PERMISSIONS}


def has_permission(name: str, permission: str) -> bool:
    """Check if a snapshot has a specific permission (defaults to True)."""
    if permission not in VALID_PERMISSIONS:
        return False
    return get_permissions(name).get(permission, True)


def reset_permissions(name: str) -> bool:
    """Remove all custom permissions for a snapshot."""
    data = _load_permissions()
    if name not in data:
        return False
    del data[name]
    _save_permissions(data)
    return True


def list_restricted(permission: str) -> list:
    """List snapshot names where a given permission is explicitly False."""
    data = _load_permissions()
    return [name for name, perms in data.items() if perms.get(permission) is False]
