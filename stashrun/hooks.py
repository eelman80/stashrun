"""Lifecycle hooks for snapshot events (pre/post save, restore)."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from stashrun.storage import get_stash_dir

_HOOKS_FILE = "hooks.json"

HOOK_EVENTS = ("pre_save", "post_save", "pre_restore", "post_restore")


def _hooks_path() -> Path:
    return get_stash_dir() / _HOOKS_FILE


def _load_hooks() -> dict:
    p = _hooks_path()
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)


def _save_hooks(data: dict) -> None:
    _hooks_path().write_text(json.dumps(data, indent=2))


def set_hook(event: str, command: str) -> bool:
    """Register a shell command for a lifecycle event. Returns False if event is invalid."""
    if event not in HOOK_EVENTS:
        return False
    hooks = _load_hooks()
    hooks[event] = command
    _save_hooks(hooks)
    return True


def remove_hook(event: str) -> bool:
    """Remove the hook for an event. Returns False if not set."""
    hooks = _load_hooks()
    if event not in hooks:
        return False
    del hooks[event]
    _save_hooks(hooks)
    return True


def get_hook(event: str) -> Optional[str]:
    """Return the command registered for an event, or None."""
    return _load_hooks().get(event)


def list_hooks() -> dict:
    """Return all registered hooks."""
    return _load_hooks()


def run_hook(event: str, snapshot_name: str) -> Optional[int]:
    """Execute the hook command for an event. Returns exit code or None if no hook."""
    cmd = get_hook(event)
    if cmd is None:
        return None
    env_extra = {"STASHRUN_SNAPSHOT": snapshot_name, "STASHRUN_EVENT": event}
    import os
    env = {**os.environ, **env_extra}
    result = subprocess.run(cmd, shell=True, env=env)
    return result.returncode
