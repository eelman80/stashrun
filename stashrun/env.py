"""Utilities for capturing and restoring environment variables."""

import os
from typing import Dict, List, Optional


def capture_env(keys: Optional[List[str]] = None) -> Dict[str, str]:
    """Capture current environment variables.

    Args:
        keys: Optional list of specific keys to capture.
              If None, captures all environment variables.

    Returns:
        A dictionary of environment variable names to values.
    """
    if keys is None:
        return dict(os.environ)
    return {k: os.environ[k] for k in keys if k in os.environ}


def apply_env(env: Dict[str, str], overwrite: bool = True) -> None:
    """Apply a dictionary of environment variables to the current process.

    Args:
        env: Dictionary of variable names to values.
        overwrite: If True, overwrite existing variables. Default True.
    """
    for key, value in env.items():
        if overwrite or key not in os.environ:
            os.environ[key] = value


def diff_env(
    base: Dict[str, str], target: Dict[str, str]
) -> Dict[str, dict]:
    """Compute the diff between two environment snapshots.

    Returns:
        A dict with keys 'added', 'removed', 'changed', each mapping
        variable names to their values (or old/new for 'changed').
    """
    added = {k: target[k] for k in target if k not in base}
    removed = {k: base[k] for k in base if k not in target}
    changed = {
        k: {"old": base[k], "new": target[k]}
        for k in base
        if k in target and base[k] != target[k]
    }
    return {"added": added, "removed": removed, "changed": changed}


def filter_env(
    env: Dict[str, str], prefixes: Optional[List[str]] = None
) -> Dict[str, str]:
    """Filter environment variables by key prefix.

    Args:
        env: Source environment dictionary.
        prefixes: List of prefixes to include. If None, returns all.

    Returns:
        Filtered environment dictionary.
    """
    if prefixes is None:
        return dict(env)
    return {
        k: v for k, v in env.items()
        if any(k.startswith(p) for p in prefixes)
    }
