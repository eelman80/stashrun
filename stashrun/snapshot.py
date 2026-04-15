"""High-level snapshot management combining env capture and storage."""

from typing import Dict, List, Optional

from stashrun.env import capture_env, apply_env, filter_env
from stashrun.storage import save_snapshot, load_snapshot, list_snapshots, delete_snapshot


def create_snapshot(
    name: str,
    keys: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Capture the current environment and persist it as a named snapshot.

    Args:
        name: Identifier for the snapshot.
        keys: Specific env var keys to include.
        prefixes: Only include vars matching these prefixes.

    Returns:
        The captured environment dictionary that was saved.
    """
    env = capture_env(keys=keys)
    if prefixes:
        env = filter_env(env, prefixes=prefixes)
    save_snapshot(name, env)
    return env


def restore_snapshot(name: str, overwrite: bool = True) -> Optional[Dict[str, str]]:
    """Load a named snapshot and apply it to the current environment.

    Args:
        name: Identifier of the snapshot to restore.
        overwrite: Whether to overwrite existing env vars.

    Returns:
        The restored environment dictionary, or None if not found.
    """
    env = load_snapshot(name)
    if env is None:
        return None
    apply_env(env, overwrite=overwrite)
    return env


def get_snapshot(name: str) -> Optional[Dict[str, str]]:
    """Retrieve a snapshot without applying it."""
    return load_snapshot(name)


def remove_snapshot(name: str) -> bool:
    """Delete a named snapshot.

    Returns:
        True if deleted, False if it did not exist.
    """
    return delete_snapshot(name)


def list_all_snapshots() -> List[str]:
    """Return names of all available snapshots."""
    return list_snapshots()
