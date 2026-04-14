"""Storage module for persisting and retrieving environment variable snapshots."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_STASH_DIR = Path.home() / ".stashrun"


def get_stash_dir() -> Path:
    """Return the stash directory, creating it if it doesn't exist."""
    stash_dir = Path(os.environ.get("STASHRUN_DIR", DEFAULT_STASH_DIR))
    stash_dir.mkdir(parents=True, exist_ok=True)
    return stash_dir


def snapshot_path(name: str) -> Path:
    """Return the file path for a named snapshot."""
    return get_stash_dir() / f"{name}.json"


def save_snapshot(name: str, env_vars: dict[str, str], description: str = "") -> Path:
    """Save a snapshot of environment variables under the given name.

    Args:
        name: Unique identifier for this snapshot.
        env_vars: Dictionary of environment variable key-value pairs.
        description: Optional human-readable description.

    Returns:
        Path to the saved snapshot file.
    """
    path = snapshot_path(name)
    payload = {
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
        "env": env_vars,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_snapshot(name: str) -> Optional[dict]:
    """Load a snapshot by name.

    Returns:
        The snapshot dict, or None if not found.
    """
    path = snapshot_path(name)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_snapshots() -> list[dict]:
    """Return metadata for all stored snapshots, sorted by creation time."""
    snapshots = []
    for file in get_stash_dir().glob("*.json"):
        try:
            data = json.loads(file.read_text())
            snapshots.append({
                "name": data.get("name", file.stem),
                "description": data.get("description", ""),
                "created_at": data.get("created_at", ""),
                "var_count": len(data.get("env", {})),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sorted(snapshots, key=lambda s: s["created_at"])


def delete_snapshot(name: str) -> bool:
    """Delete a snapshot by name.

    Returns:
        True if deleted, False if it did not exist.
    """
    path = snapshot_path(name)
    if path.exists():
        path.unlink()
        return True
    return False
