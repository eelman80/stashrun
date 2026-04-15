"""Combine templates with snapshots: create snapshots pre-filtered by a template."""

from typing import Optional

from stashrun.env import capture_env
from stashrun.snapshot import create_snapshot, get_snapshot
from stashrun.templates import apply_template, get_template


def create_snapshot_from_template(
    snapshot_name: str,
    template_name: str,
    prefix: Optional[str] = None,
) -> Optional[dict]:
    """Capture the current environment, filter it through a template, and save as a snapshot.

    Returns the saved env dict on success, or None if the template does not exist.
    """
    if get_template(template_name) is None:
        return None

    current_env = capture_env()
    filtered_env = apply_template(template_name, current_env)
    if filtered_env is None:
        return None

    create_snapshot(snapshot_name, env=filtered_env, prefix=prefix)
    return filtered_env


def compare_snapshot_to_template(snapshot_name: str, template_name: str) -> Optional[dict]:
    """Return keys from the template that are missing in the given snapshot.

    Returns a dict with 'missing' and 'present' key lists, or None if either is not found.
    """
    snapshot = get_snapshot(snapshot_name)
    if snapshot is None:
        return None

    template = get_template(template_name)
    if template is None:
        return None

    env = snapshot.get("env", {})
    missing = [k for k in template if k not in env]
    present = [k for k in template if k in env]
    return {"missing": missing, "present": present}
