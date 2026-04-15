"""Integration helpers that fire hooks around snapshot operations."""

from typing import Optional

from stashrun.hooks import run_hook
from stashrun.snapshot import create_snapshot, restore_snapshot


def create_snapshot_with_hooks(
    name: str,
    keys: Optional[list] = None,
    prefix: Optional[str] = None,
) -> dict:
    """Run pre_save hook, create snapshot, run post_save hook.

    Returns a dict with 'snapshot' and 'pre_exit'/'post_exit' codes.
    """
    pre_exit = run_hook("pre_save", name)
    snapshot = create_snapshot(name, keys=keys, prefix=prefix)
    post_exit = run_hook("post_save", name)
    return {"snapshot": snapshot, "pre_exit": pre_exit, "post_exit": post_exit}


def restore_snapshot_with_hooks(
    name: str,
    overwrite: bool = True,
) -> dict:
    """Run pre_restore hook, restore snapshot, run post_restore hook.

    Returns a dict with 'env' (applied env or None) and hook exit codes.
    """
    pre_exit = run_hook("pre_restore", name)
    env = restore_snapshot(name, overwrite=overwrite)
    post_exit = run_hook("post_restore", name)
    return {"env": env, "pre_exit": pre_exit, "post_exit": post_exit}
